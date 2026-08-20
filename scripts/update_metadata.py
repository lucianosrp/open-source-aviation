#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Refresh the *Data Metadata* table in README.md.

The curated link lists in README.md are the single source of truth: every
``raw.githubusercontent.com`` link ending in ``.csv`` or ``.dat`` that appears
above the generated block is catalogued automatically. For each one we publish

* ``last_modified`` -- author date (UTC) of the newest commit touching the path,
* ``row_count``     -- data records, CSV-parsed so quoted newlines count once,
* ``size``          -- uncompressed size of the file.

Design notes
------------
* Standard library only. ``uv run`` therefore needs no package downloads, and
  there is no third-party dependency that can break the daily refresh.
* Files are streamed and parsed incrementally, so memory stays flat no matter
  how large the upstream datasets grow.
* A dataset that fails is never silently dropped: its previously published row
  is carried over and reported, so a transient upstream outage cannot delete
  data from the table.
* Nothing time-based is written into the README, so the table changes only when
  the underlying data changes -- the workflow commits real updates, not noise.

Usage
-----
    uv run --script scripts/update_metadata.py
    uv run --script scripts/update_metadata.py --check   # fail if out of date

Exit codes: ``0`` success, ``1`` a dataset was lost or the table is stale under
``--check``, ``2`` README.md is missing the generated block.
"""

from __future__ import annotations

import argparse
import csv
import gzip
import io
import json
import logging
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from collections.abc import Callable, Sequence
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, BinaryIO, TypeVar

LOG = logging.getLogger("update-metadata")

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_README = REPO_ROOT / "README.md"

BLOCK_START = "<!-- data-metadata:start -->"
BLOCK_END = "<!-- data-metadata:end -->"

USER_AGENT = "open-source-aviation-metadata (+https://github.com/lucianosrp/open-source-aviation)"

RAW_HOST = "raw.githubusercontent.com"
RAW_URL_RE = re.compile(rf"https://{re.escape(RAW_HOST)}/[^\s)\]\"'<>]+")

# Suffix -> is the first CSV record a header row?
# OurAirports ships column names; the OpenFlights .dat exports do not, which is
# why counting them with a header assumption undercounted every row by one.
CATALOGUED_SUFFIXES: dict[str, bool] = {".csv": True, ".dat": False}

COLUMNS = ("name", "last_modified", "row_count", "size")
ALIGN_LEFT = (True, True, False, False)

HTTP_TIMEOUT = 60.0
MAX_ATTEMPTS = 4
BACKOFF_SECONDS = 3.0
MAX_RATE_LIMIT_WAIT = 180.0
MAX_DOWNLOAD_BYTES = 1 << 30  # guard against a runaway upstream file
RETRYABLE_STATUS = frozenset({408, 425, 429, 500, 502, 503, 504})

T = TypeVar("T")


class SourceError(Exception):
    """A single dataset could not be refreshed."""


class RetryableError(SourceError):
    """A failure that is worth another attempt."""

    def __init__(self, message: str, retry_after: float | None = None) -> None:
        super().__init__(message)
        self.retry_after = retry_after


class ReadmeStructureError(Exception):
    """The README does not contain the generated block."""


@dataclass(frozen=True)
class Source:
    """A catalogued file hosted on raw.githubusercontent.com."""

    url: str
    owner: str
    repo: str
    ref: str
    path: str
    has_header: bool

    @property
    def filename(self) -> str:
        return self.path.rsplit("/", 1)[-1]

    @property
    def link(self) -> str:
        return f"[{self.filename}]({self.url})"


@dataclass
class Record:
    """One rendered table row."""

    source: Source
    last_modified: str = ""
    row_count: str = ""
    size: str = ""
    carried_over: bool = False
    error: str = ""

    @property
    def cells(self) -> tuple[str, ...]:
        return (self.source.link, self.last_modified, self.row_count, self.size)

    @property
    def has_data(self) -> bool:
        return bool(self.last_modified or self.row_count)


# --------------------------------------------------------------------------- #
# Discovery
# --------------------------------------------------------------------------- #


def parse_source(url: str) -> Source | None:
    """Turn a raw.githubusercontent.com URL into a :class:`Source`.

    Returns ``None`` for URLs that are not catalogued datasets. Both the short
    ``/<owner>/<repo>/<ref>/<path>`` and the fully qualified
    ``/<owner>/<repo>/refs/heads/<ref>/<path>`` layouts are understood.
    """
    parts = urllib.parse.urlsplit(url)
    if parts.netloc != RAW_HOST:
        return None
    segments = [segment for segment in parts.path.split("/") if segment]
    if len(segments) < 4:
        LOG.debug("ignoring raw URL with too few path segments: %s", url)
        return None

    owner, repo, *rest = segments
    if rest[0] == "refs" and len(rest) >= 4:
        ref, rest = rest[2], rest[3:]
    else:
        ref, rest = rest[0], rest[1:]

    path = "/".join(rest)
    has_header = CATALOGUED_SUFFIXES.get(Path(path).suffix.lower())
    if has_header is None:
        return None
    return Source(url=url, owner=owner, repo=repo, ref=ref, path=path, has_header=has_header)


def discover_sources(readme: str) -> list[Source]:
    """Collect catalogued datasets from the curated lists, in document order.

    Only the text above :data:`BLOCK_START` is scanned so that the generated
    table never feeds itself.
    """
    catalogue = readme.split(BLOCK_START, 1)[0]
    sources: dict[str, Source] = {}
    for match in RAW_URL_RE.finditer(catalogue):
        url = match.group(0).rstrip(".,;:")
        if url in sources:
            continue
        if source := parse_source(url):
            sources[url] = source
    return list(sources.values())


# --------------------------------------------------------------------------- #
# HTTP
# --------------------------------------------------------------------------- #


def _rate_limit_delay(headers: Any) -> float | None:
    """Seconds to wait per the server's rate-limit headers, if it asked us to."""
    retry_after = headers.get("Retry-After")
    if retry_after:
        try:
            return min(float(retry_after), MAX_RATE_LIMIT_WAIT)
        except ValueError:
            pass
    if headers.get("X-RateLimit-Remaining") == "0":
        reset = headers.get("X-RateLimit-Reset")
        try:
            wait = float(reset) - time.time() + 1.0 if reset else None
        except ValueError:
            wait = None
        if wait is not None and 0.0 < wait <= MAX_RATE_LIMIT_WAIT:
            return wait
    return None


def _open(url: str, headers: dict[str, str]) -> Any:
    """Open *url*, mapping transport failures onto retryable/fatal errors."""
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, **headers})
    try:
        return urllib.request.urlopen(request, timeout=HTTP_TIMEOUT)
    except urllib.error.HTTPError as exc:
        status, delay = exc.code, _rate_limit_delay(exc.headers)
        exc.close()
        if delay is not None:
            raise RetryableError(f"HTTP {status} (rate limited)", delay) from exc
        if status in RETRYABLE_STATUS:
            raise RetryableError(f"HTTP {status}") from exc
        raise SourceError(f"HTTP {status}") from exc
    except OSError as exc:  # URLError, timeouts, connection resets
        raise RetryableError(f"{type(exc).__name__}: {exc}") from exc


def _retry(operation: Callable[[], T], *, what: str) -> T:
    """Run *operation*, retrying retryable failures with exponential backoff."""
    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            return operation()
        except RetryableError as exc:
            if attempt == MAX_ATTEMPTS:
                raise SourceError(f"{exc} after {MAX_ATTEMPTS} attempts") from exc
            delay = (
                exc.retry_after
                if exc.retry_after is not None
                else BACKOFF_SECONDS * 2 ** (attempt - 1)
            )
            LOG.warning(
                "%s: %s -- retrying in %.0fs (attempt %d/%d)",
                what,
                exc,
                delay,
                attempt,
                MAX_ATTEMPTS,
            )
            time.sleep(delay)
    raise AssertionError("unreachable")


def fetch_last_modified(source: Source, token: str | None) -> datetime:
    """Author date of the newest commit touching ``source.path``."""
    query = urllib.parse.urlencode({"path": source.path, "sha": source.ref, "per_page": 1})
    api_url = f"https://api.github.com/repos/{source.owner}/{source.repo}/commits?{query}"
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"

    def call() -> datetime:
        with _open(api_url, headers) as response:
            payload = json.load(response)
        try:
            commit = payload[0]["commit"]
            stamp = (commit.get("author") or {}).get("date") or (commit.get("committer") or {}).get(
                "date"
            )
        except (IndexError, KeyError, TypeError) as exc:
            raise SourceError(f"unexpected commits payload: {exc}") from exc
        if not stamp:
            raise SourceError(f"no commit date for {source.path} on {source.ref}")
        return datetime.fromisoformat(stamp).astimezone(UTC)

    return _retry(call, what=f"commits API for {source.filename}")


# --------------------------------------------------------------------------- #
# Counting
# --------------------------------------------------------------------------- #


class _CountingReader(io.RawIOBase):
    """Raw reader that tallies the bytes pulled from an underlying stream."""

    def __init__(self, stream: Any, limit: int | None = None) -> None:
        self._stream = stream
        # Resolved at call time, not baked into a default argument, so the cap
        # stays overridable.
        self._limit = MAX_DOWNLOAD_BYTES if limit is None else limit
        self.bytes_read = 0

    def readable(self) -> bool:
        return True

    def readinto(self, buffer: Any) -> int:  # type: ignore[override]
        chunk = self._stream.read(len(buffer))
        if not chunk:
            return 0
        self.bytes_read += len(chunk)
        if self.bytes_read > self._limit:
            raise SourceError(f"stream exceeded {self._limit} bytes")
        buffer[: len(chunk)] = chunk
        return len(chunk)


def count_records(stream: BinaryIO | Any, *, has_header: bool) -> tuple[int, int]:
    """Return ``(row_count, size_bytes)`` for a binary CSV/DAT stream.

    Parsing with :mod:`csv` instead of counting newlines is load-bearing: some
    OurAirports exports quote free-text fields containing line breaks, so
    airport-comments.csv spans ~29k lines but holds only ~16k records. Blank
    lines are skipped, matching how the table was produced historically.
    """
    counter = _CountingReader(stream)
    text = io.TextIOWrapper(
        io.BufferedReader(counter), encoding="utf-8", errors="replace", newline=""
    )
    records = sum(1 for row in csv.reader(text) if row)
    return max(records - 1 if has_header else records, 0), counter.bytes_read


def fetch_row_count(source: Source) -> tuple[int, int]:
    """Stream ``source`` and return ``(row_count, size_bytes)``."""

    def call() -> tuple[int, int]:
        try:
            with _open(source.url, {"Accept-Encoding": "gzip"}) as response:
                stream: Any = response
                if (response.headers.get("Content-Encoding") or "").lower() == "gzip":
                    stream = gzip.GzipFile(fileobj=response)
                return count_records(stream, has_header=source.has_header)
        except SourceError:
            raise
        except (OSError, EOFError) as exc:
            raise RetryableError(f"stream failed: {exc}") from exc

    return _retry(call, what=f"download of {source.filename}")


# --------------------------------------------------------------------------- #
# Rendering
# --------------------------------------------------------------------------- #


def format_size(num_bytes: int) -> str:
    """Human-readable size using binary multiples."""
    size = float(num_bytes)
    for unit in ("B", "KB", "MB", "GB"):
        if size < 1024.0 or unit == "GB":
            return f"{size:.{0 if unit == 'B' else 1}f} {unit}"
        size /= 1024.0
    raise AssertionError("unreachable")


def render_table(records: Sequence[Record]) -> str:
    """Render a padded GitHub-flavoured markdown table."""
    body = [record.cells for record in records]
    widths = [max([len(COLUMNS[i]), *(len(row[i]) for row in body)]) for i in range(len(COLUMNS))]

    def row(cells: Sequence[str]) -> str:
        padded = (
            cell.ljust(widths[i]) if ALIGN_LEFT[i] else cell.rjust(widths[i])
            for i, cell in enumerate(cells)
        )
        return f"| {' | '.join(padded)} |"

    rule = "|".join(
        ":" + "-" * (width + 1) if ALIGN_LEFT[i] else "-" * (width + 1) + ":"
        for i, width in enumerate(widths)
    )
    return "\n".join([row(COLUMNS), f"|{rule}|", *(row(cells) for cells in body)])


def parse_published_rows(readme: str) -> dict[str, dict[str, str]]:
    """Map dataset URL -> the cells currently published, keyed by column name."""
    if BLOCK_START not in readme or BLOCK_END not in readme:
        return {}
    block = readme.split(BLOCK_START, 1)[1].split(BLOCK_END, 1)[0]
    lines = [
        [cell.strip() for cell in line.strip().strip("|").split("|")]
        for line in block.splitlines()
        if line.strip().startswith("|")
    ]
    if len(lines) < 3:  # header, alignment rule, at least one row
        return {}
    headers = lines[0]
    published: dict[str, dict[str, str]] = {}
    for cells in lines[2:]:
        if len(cells) != len(headers):
            continue
        if match := re.search(r"\]\((?P<url>[^)]+)\)", cells[0]):
            published[match.group("url")] = dict(zip(headers, cells, strict=True))
    return published


def splice(readme: str, table: str) -> str:
    """Replace the generated block in *readme* with *table*."""
    if BLOCK_START not in readme or BLOCK_END not in readme:
        raise ReadmeStructureError(
            f"missing the {BLOCK_START} / {BLOCK_END} markers -- "
            "add them where the table should be generated"
        )
    before, rest = readme.split(BLOCK_START, 1)
    _, after = rest.split(BLOCK_END, 1)
    return f"{before}{BLOCK_START}\n{table}\n{BLOCK_END}{after}"


# --------------------------------------------------------------------------- #
# Orchestration
# --------------------------------------------------------------------------- #


def build_record(source: Source, token: str | None, published: dict[str, dict[str, str]]) -> Record:
    """Refresh one dataset, falling back to its published row on failure."""
    record = Record(source=source)
    try:
        last_modified = fetch_last_modified(source, token)
        row_count, size_bytes = fetch_row_count(source)
    except SourceError as exc:
        record.error = str(exc)
        if previous := published.get(source.url):
            record.carried_over = True
            record.last_modified = previous.get("last_modified", "")
            record.row_count = previous.get("row_count", "")
            record.size = previous.get("size", "")
        return record

    record.last_modified = last_modified.strftime("%Y-%m-%d %H:%M:%S")
    record.row_count = f"{row_count:,}"
    record.size = format_size(size_bytes)
    return record


def collect(
    sources: Sequence[Source],
    token: str | None,
    published: dict[str, dict[str, str]],
    jobs: int,
) -> list[Record]:
    """Refresh every dataset concurrently and sort the resulting rows."""
    with ThreadPoolExecutor(max_workers=min(jobs, len(sources))) as pool:
        records = list(pool.map(lambda s: build_record(s, token, published), sources))
    return sort_records(records)


def sort_records(records: list[Record]) -> list[Record]:
    """Order rows newest first, breaking ties by filename.

    Two stable passes. The tie-break is what keeps the rendered table -- and
    therefore the git diff -- stable when several datasets share a timestamp.
    """
    records.sort(key=lambda record: record.source.filename)
    records.sort(key=lambda record: record.last_modified, reverse=True)
    return records


def _annotate(level: str, message: str) -> None:
    """Log *message* and surface it in the Actions UI when running in CI."""
    LOG.warning(message) if level == "warning" else LOG.error(message)
    if os.environ.get("GITHUB_ACTIONS") == "true":
        print(f"::{level}::{message}", flush=True)


def _write_step_summary(table: str, degraded: Sequence[Record]) -> None:
    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if not summary:
        return
    lines = ["## Data metadata", "", table, ""]
    if degraded:
        lines += ["### Warnings", ""]
        lines += [
            f"- **{record.source.filename}**: {record.error}"
            f"{' (kept published values)' if record.carried_over else ' (no data)'}"
            for record in degraded
        ]
        lines.append("")
    with open(summary, "a", encoding="utf-8") as handle:
        handle.write("\n".join(lines) + "\n")


def _atomic_write(path: Path, text: str) -> None:
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(text, encoding="utf-8", newline="\n")
    temporary.replace(path)


def _raise_csv_field_limit() -> None:
    """Allow the long free-text fields in airport-comments.csv."""
    limit = 1 << 24
    while limit > 1 << 17:
        try:
            csv.field_size_limit(limit)
            return
        except OverflowError:
            limit >>= 1


def parse_args(argv: Sequence[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Refresh the Data Metadata table in README.md.")
    parser.add_argument(
        "--readme",
        type=Path,
        default=DEFAULT_README,
        help="README to update (default: %(default)s)",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="do not write; exit 1 if the table is out of date",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="exit 1 on any dataset failure, even when published values were kept",
    )
    parser.add_argument(
        "--jobs", type=int, default=6, help="parallel refreshes (default: %(default)s)"
    )
    parser.add_argument("-v", "--verbose", action="store_true", help="debug logging")
    args = parser.parse_args(argv)
    if args.jobs < 1:
        parser.error("--jobs must be at least 1")
    return args


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(levelname)s %(message)s",
        stream=sys.stderr,
    )
    _raise_csv_field_limit()

    readme_path: Path = args.readme
    try:
        readme = readme_path.read_text(encoding="utf-8")
    except OSError as exc:
        LOG.error("cannot read %s: %s", readme_path, exc)
        return 2

    sources = discover_sources(readme)
    if not sources:
        LOG.error("no catalogued datasets found above %s in %s", BLOCK_START, readme_path)
        return 2

    token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    if not token:
        LOG.warning(
            "no GH_TOKEN/GITHUB_TOKEN in the environment -- unauthenticated GitHub "
            "API calls are limited to 60 per hour"
        )

    published = parse_published_rows(readme)
    LOG.info("refreshing %d dataset(s) with %d worker(s)", len(sources), args.jobs)
    records = collect(sources, token, published, args.jobs)

    degraded = [record for record in records if record.error]
    lost = [record for record in degraded if not record.has_data]
    for record in degraded:
        _annotate(
            "error" if record in lost else "warning",
            f"{record.source.filename}: {record.error}"
            + ("" if record in lost else " (kept published values)"),
        )

    table = render_table([record for record in records if record.has_data])
    try:
        updated = splice(readme, table)
    except ReadmeStructureError as exc:
        LOG.error("%s: %s", readme_path, exc)
        return 2

    _write_step_summary(table, degraded)

    if updated == readme:
        LOG.info("%s is already up to date", readme_path.name)
    elif args.check:
        LOG.error("%s is out of date -- rerun without --check to refresh it", readme_path.name)
        return 1
    else:
        _atomic_write(readme_path, updated)
        LOG.info("%s updated (%d rows)", readme_path.name, len(records) - len(lost))

    if lost:
        LOG.error("%d dataset(s) have no data and were omitted", len(lost))
        return 1
    if degraded and args.strict:
        LOG.error("--strict: %d dataset(s) could not be refreshed", len(degraded))
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
