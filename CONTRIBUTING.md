# Contributing

Thanks for helping grow the list! Additions of open-source aviation projects,
tools and datasets are all welcome.

## Adding an entry

1. Find the right section in [README.md](README.md), or add a new one and list
   it under **Contents**.
2. Add a bullet in the existing style:

   ```markdown
   * [name](https://example.com/project) - Short description of what it offers.
   ```

3. Keep entries alphabetical-ish within a section, prefer the project's canonical
   URL, and say what makes the resource useful rather than restating its name.
4. Open a pull request. Please keep one logical addition per PR so it is easy to
   review.

Entries should be freely accessible. Resources that require a paid plan or an
approval process to get any data at all are out of scope.

## The Data Metadata table

The table at the bottom of the README is generated. **Do not edit it by hand** —
your changes will be overwritten by the next scheduled run.

Any `raw.githubusercontent.com` link ending in `.csv` or `.dat` that you add to
the curated lists is picked up automatically on the next refresh. Nothing else
is required.

To track a new format, add its suffix to `CATALOGUED_SUFFIXES` in
[`scripts/update_metadata.py`](scripts/update_metadata.py), mapping it to whether
the first record is a header row.

## Refreshing the metadata table

The refresh script is a single [PEP 723](https://peps.python.org/pep-0723/) file
with no third-party dependencies. With [uv](https://docs.astral.sh/uv/)
installed:

```bash
# Refresh README.md in place
uv run --script scripts/update_metadata.py

# Report whether the table is stale, without writing (exit 1 if it is)
uv run --script scripts/update_metadata.py --check

# Useful flags
uv run --script scripts/update_metadata.py --jobs 12 --verbose
uv run --script scripts/update_metadata.py --strict   # fail on any fetch error
```

Exit codes: `0` success, `1` a dataset could not be resolved (or the table is
stale under `--check`), `2` the README is missing its generated block.

### GitHub API rate limits

The script queries the GitHub commits API once per dataset. Unauthenticated
calls are capped at 60 per hour, which is enough today but will not scale. Export
a token with no scopes to raise the limit:

```bash
export GH_TOKEN=ghp_...   # GITHUB_TOKEN is also honoured
```

CI passes the workflow's built-in `GITHUB_TOKEN` automatically.

### Resilience

A dataset that cannot be fetched keeps the values already published in the table
and is reported as a warning, so a transient upstream outage never deletes a row.
If a dataset has no previously published values to fall back on, the run exits
non-zero rather than quietly shipping an incomplete table.

## Licensing of contributions

By opening a pull request you agree to release your contribution under
[CC0-1.0](LICENSE), the same public domain dedication that covers the rest of
the repository. This applies to list entries and to code alike.

## Running the checks

```bash
uv run --no-project --with pytest==9.1.1 --python 3.12 pytest -q tests/
uvx ruff@0.16.3 check .
uvx ruff@0.16.3 format --check .
```

The tests are offline: the network layer is exercised through injected failures,
so the suite runs in well under a second.
