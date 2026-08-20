"""Offline tests for the metadata refresh script.

Nothing here touches the network: the HTTP layer is exercised through injected
failures so the suite stays fast and deterministic.
"""

from __future__ import annotations

import io
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
OURAIRPORTS = "https://raw.githubusercontent.com/davidmegginson/ourairports-data/main"
OPENFLIGHTS = "https://raw.githubusercontent.com/jpatokal/openflights/master/data"


# --------------------------------------------------------------------------- #
# URL parsing
# --------------------------------------------------------------------------- #


def test_parse_source_short_form(um):
    source = um.parse_source(f"{OURAIRPORTS}/airports.csv")
    assert (source.owner, source.repo, source.ref) == (
        "davidmegginson",
        "ourairports-data",
        "main",
    )
    assert source.path == "airports.csv"
    assert source.has_header is True


def test_parse_source_keeps_nested_paths(um):
    """The API needs the full path, not just the basename."""
    source = um.parse_source(f"{OPENFLIGHTS}/airports.dat")
    assert source.path == "data/airports.dat"
    assert source.filename == "airports.dat"
    assert source.has_header is False


def test_parse_source_accepts_fully_qualified_ref(um):
    source = um.parse_source(
        "https://raw.githubusercontent.com/o/r/refs/heads/main/sub/dir/file.csv"
    )
    assert (source.ref, source.path) == ("main", "sub/dir/file.csv")


@pytest.mark.parametrize(
    "url",
    [
        "https://example.com/o/r/main/file.csv",  # wrong host
        f"{OURAIRPORTS}/notes.txt",  # uncatalogued suffix
        f"{OURAIRPORTS}/README",  # no suffix
        "https://raw.githubusercontent.com/o/r/main",  # too few segments
    ],
)
def test_parse_source_rejects(um, url):
    assert um.parse_source(url) is None


def test_parse_source_is_case_insensitive_on_suffix(um):
    assert um.parse_source(f"{OURAIRPORTS}/AIRPORTS.CSV").has_header is True


# --------------------------------------------------------------------------- #
# Discovery
# --------------------------------------------------------------------------- #


def test_discover_sources_dedupes_and_keeps_order(um):
    readme = f"""
* [airports.csv]({OURAIRPORTS}/airports.csv) - first
* [runways.csv]({OURAIRPORTS}/runways.csv) - second
* [airports.csv]({OURAIRPORTS}/airports.csv) - duplicate link
"""
    assert [s.filename for s in um.discover_sources(readme)] == [
        "airports.csv",
        "runways.csv",
    ]


def test_discover_sources_ignores_the_generated_block(um):
    """The table must never feed itself, or removed links would persist."""
    readme = (
        f"* [runways.csv]({OURAIRPORTS}/runways.csv)\n"
        f"{um.BLOCK_START}\n"
        f"| [airports.csv]({OURAIRPORTS}/airports.csv) | x | y | z |\n"
        f"{um.BLOCK_END}\n"
    )
    assert [s.filename for s in um.discover_sources(readme)] == ["runways.csv"]


def test_discover_sources_strips_trailing_prose_punctuation(um):
    readme = f"See {OURAIRPORTS}/airports.csv, which is large."
    assert [s.path for s in um.discover_sources(readme)] == ["airports.csv"]


# --------------------------------------------------------------------------- #
# Record counting
# --------------------------------------------------------------------------- #


def test_count_records_excludes_header(um):
    payload = b"id,name\n1,alpha\n2,beta\n"
    assert um.count_records(io.BytesIO(payload), has_header=True) == (2, len(payload))


def test_count_records_counts_every_row_when_headerless(um):
    """Regression: .dat exports have no header and were undercounted by one."""
    payload = b'1,"Goroka Airport"\n2,"Madang Airport"\n'
    rows, _ = um.count_records(io.BytesIO(payload), has_header=False)
    assert rows == 2


def test_count_records_handles_quoted_newlines(um):
    """airport-comments.csv quotes free-text spanning several lines."""
    payload = b'id,comment\n1,"line one\nline two\nline three"\n2,"short"\n'
    rows, _ = um.count_records(io.BytesIO(payload), has_header=True)
    assert rows == 2
    assert payload.count(b"\n") == 5  # naive line counting would say 5


def test_count_records_skips_blank_lines(um):
    payload = b"id,name\n1,alpha\n\n\n2,beta\n"
    rows, _ = um.count_records(io.BytesIO(payload), has_header=True)
    assert rows == 2


def test_count_records_never_returns_negative(um):
    assert um.count_records(io.BytesIO(b""), has_header=True) == (0, 0)


def test_count_records_tolerates_invalid_utf8(um):
    rows, _ = um.count_records(io.BytesIO(b"id\n\xff\xfe\n"), has_header=True)
    assert rows == 1


def test_count_records_reports_uncompressed_size(um):
    payload = b"a,b\n" + b"1,2\n" * 1000
    _, size = um.count_records(io.BytesIO(payload), has_header=True)
    assert size == len(payload)


def test_count_records_rejects_oversized_stream(um, monkeypatch):
    monkeypatch.setattr(um, "MAX_DOWNLOAD_BYTES", 16)
    with pytest.raises(um.SourceError, match="exceeded"):
        um.count_records(io.BytesIO(b"a,b\n" + b"1,2\n" * 100), has_header=True)


# --------------------------------------------------------------------------- #
# Rendering
# --------------------------------------------------------------------------- #


def _record(um, filename, last_modified="2020-01-01 00:00:00", rows="1", size="1 B"):
    source = um.parse_source(f"{OURAIRPORTS}/{filename}")
    return um.Record(source=source, last_modified=last_modified, row_count=rows, size=size)


def test_render_table_is_rectangular(um):
    table = um.render_table([_record(um, "a.csv"), _record(um, "much-longer-name.csv")])
    lines = table.splitlines()
    assert len({len(line) for line in lines}) == 1, "rows must be padded alike"
    assert all(line.startswith("|") and line.endswith("|") for line in lines)


def test_render_table_alignment_row(um):
    table = um.render_table([_record(um, "a.csv")])
    rule = table.splitlines()[1]
    left, modified, rows, size = rule.strip("|").split("|")
    assert left.startswith(":") and modified.startswith(":")
    assert rows.endswith(":") and size.endswith(":")


def test_render_table_handles_empty_input(um):
    assert um.render_table([]).splitlines()[0].startswith("| name")


def test_sort_records_newest_first_then_by_name(um):
    records = [
        _record(um, "b.csv", "2020-01-01 00:00:00"),
        _record(um, "a.csv", "2020-01-01 00:00:00"),
        _record(um, "c.csv", "2021-01-01 00:00:00"),
    ]
    assert [r.source.filename for r in um.sort_records(records)] == [
        "c.csv",
        "a.csv",
        "b.csv",
    ]


def test_sort_records_is_idempotent(um):
    records = [
        _record(um, "b.csv", "2020-01-01 00:00:00"),
        _record(um, "a.csv", "2020-01-01 00:00:00"),
    ]
    once = [r.source.filename for r in um.sort_records(records)]
    twice = [r.source.filename for r in um.sort_records(records)]
    assert once == twice


def test_format_size(um):
    assert um.format_size(0) == "0 B"
    assert um.format_size(1023) == "1023 B"
    assert um.format_size(1024) == "1.0 KB"
    assert um.format_size(12 * 1024**2) == "12.0 MB"
    assert um.format_size(3 * 1024**4) == "3072.0 GB"


# --------------------------------------------------------------------------- #
# README round-tripping
# --------------------------------------------------------------------------- #


def _readme(um, body: str) -> str:
    return f"# Title\n\n{um.BLOCK_START}\n{body}\n{um.BLOCK_END}\n\nfooter\n"


def test_splice_replaces_only_the_block(um):
    result = um.splice(_readme(um, "old"), "new")
    assert result == _readme(um, "new")


def test_splice_is_idempotent(um):
    once = um.splice(_readme(um, "old"), "table")
    assert um.splice(once, "table") == once


def test_splice_requires_markers(um):
    with pytest.raises(um.ReadmeStructureError):
        um.splice("# Title\n\nno markers here\n", "table")


def test_parse_published_rows_reads_current_schema(um):
    readme = _readme(
        um,
        "\n".join(
            [
                "| name | last_modified | row_count | size |",
                "|:-----|:--------------|----------:|-----:|",
                f"| [airports.csv]({OURAIRPORTS}/airports.csv) "
                "| 2026-01-01 00:00:00 | 85,936 | 12.1 MB |",
            ]
        ),
    )
    published = um.parse_published_rows(readme)
    assert published[f"{OURAIRPORTS}/airports.csv"]["row_count"] == "85,936"
    assert published[f"{OURAIRPORTS}/airports.csv"]["size"] == "12.1 MB"


def test_parse_published_rows_without_block(um):
    assert um.parse_published_rows("# Title\n") == {}


# --------------------------------------------------------------------------- #
# Failure handling
# --------------------------------------------------------------------------- #


def test_build_record_carries_published_values_forward(um, monkeypatch):
    """A transient upstream failure must not delete a published row."""
    url = f"{OURAIRPORTS}/airports.csv"
    monkeypatch.setattr(
        um,
        "fetch_last_modified",
        lambda *_: (_ for _ in ()).throw(um.SourceError("HTTP 503")),
    )
    published = {
        url: {
            "last_modified": "2026-01-01 00:00:00",
            "row_count": "85,936",
            "size": "12.1 MB",
        }
    }
    record = um.build_record(um.parse_source(url), None, published)
    assert record.carried_over is True
    assert record.has_data is True
    assert (record.last_modified, record.row_count) == ("2026-01-01 00:00:00", "85,936")
    assert "503" in record.error


def test_build_record_without_published_fallback_has_no_data(um, monkeypatch):
    """A brand-new source that fails is reported, not silently invented."""
    monkeypatch.setattr(
        um,
        "fetch_last_modified",
        lambda *_: (_ for _ in ()).throw(um.SourceError("HTTP 404")),
    )
    record = um.build_record(um.parse_source(f"{OURAIRPORTS}/new.csv"), None, {})
    assert record.carried_over is False
    assert record.has_data is False


def test_retry_gives_up_and_reports_attempts(um, monkeypatch):
    monkeypatch.setattr(um.time, "sleep", lambda _: None)
    attempts = []

    def failing():
        attempts.append(1)
        raise um.RetryableError("HTTP 503")

    with pytest.raises(um.SourceError, match="after 4 attempts"):
        um._retry(failing, what="test")
    assert len(attempts) == um.MAX_ATTEMPTS


def test_retry_returns_after_a_transient_failure(um, monkeypatch):
    monkeypatch.setattr(um.time, "sleep", lambda _: None)
    calls = []

    def flaky():
        calls.append(1)
        if len(calls) < 3:
            raise um.RetryableError("timeout")
        return "ok"

    assert um._retry(flaky, what="test") == "ok"


def test_rate_limit_delay_prefers_retry_after(um):
    assert um._rate_limit_delay({"Retry-After": "12"}) == 12.0


def test_rate_limit_delay_is_capped(um):
    assert um._rate_limit_delay({"Retry-After": "99999"}) == um.MAX_RATE_LIMIT_WAIT


def test_rate_limit_delay_ignores_exhausted_reset_in_the_past(um):
    headers = {"X-RateLimit-Remaining": "0", "X-RateLimit-Reset": "1"}
    assert um._rate_limit_delay(headers) is None


def test_rate_limit_delay_none_when_quota_remains(um):
    assert um._rate_limit_delay({"X-RateLimit-Remaining": "42"}) is None


# --------------------------------------------------------------------------- #
# The shipped README
# --------------------------------------------------------------------------- #


def test_repo_readme_is_wired_up(um):
    """Guard against the markers or the dataset links being dropped."""
    readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
    assert um.BLOCK_START in readme and um.BLOCK_END in readme
    filenames = [source.filename for source in um.discover_sources(readme)]
    assert "airports.csv" in filenames
    assert "airports.dat" in filenames
    assert len(filenames) == len(set(filenames)) >= 10


# --------------------------------------------------------------------------- #
# .env handling
# --------------------------------------------------------------------------- #


def test_load_dotenv_sets_missing_variables(um, tmp_path, monkeypatch):
    env = tmp_path / ".env"
    env.write_text(
        "\n".join(
            [
                "# a comment",
                "",
                "GH_TOKEN=plain-value",
                'QUOTED="double"',
                "SINGLE='single'",
                "export EXPORTED=prefixed",
                "  SPACED  =  padded  ",
                "malformed-line-without-equals",
            ]
        )
    )
    monkeypatch.delenv("GH_TOKEN", raising=False)
    for key in ("QUOTED", "SINGLE", "EXPORTED", "SPACED"):
        monkeypatch.delenv(key, raising=False)

    um.load_dotenv(env)
    assert um.os.environ["GH_TOKEN"] == "plain-value"
    assert um.os.environ["QUOTED"] == "double"
    assert um.os.environ["SINGLE"] == "single"
    assert um.os.environ["EXPORTED"] == "prefixed"
    assert um.os.environ["SPACED"] == "padded"


def test_load_dotenv_does_not_override_the_environment(um, tmp_path, monkeypatch):
    env = tmp_path / ".env"
    env.write_text("GH_TOKEN=from-file\n")
    monkeypatch.setenv("GH_TOKEN", "from-environment")
    um.load_dotenv(env)
    assert um.os.environ["GH_TOKEN"] == "from-environment"


def test_load_dotenv_tolerates_a_missing_file(um, tmp_path):
    um.load_dotenv(tmp_path / "does-not-exist")  # must not raise


def test_rate_limit_detail_explains_an_exhausted_quota(um, monkeypatch):
    monkeypatch.setattr(um.time, "time", lambda: 1000.0)
    detail = um._rate_limit_detail({"X-RateLimit-Remaining": "0", "X-RateLimit-Reset": "3400"})
    assert "rate limit exhausted" in detail
    assert "40m" in detail
    assert "GH_TOKEN" in detail


def test_rate_limit_detail_silent_on_a_genuine_403(um):
    """A permission error must not be mislabelled as rate limiting."""
    assert um._rate_limit_detail({"X-RateLimit-Remaining": "4999"}) == ""


def test_rate_limit_detail_handles_a_missing_reset(um):
    detail = um._rate_limit_detail({"X-RateLimit-Remaining": "0"})
    assert "rate limit exhausted" in detail and "resets in" not in detail
