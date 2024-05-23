import datetime
import os
import re
from abc import ABC, abstractmethod
from collections import namedtuple
from pathlib import Path
from typing import Iterable

import pandas as pd
import requests
from dotenv import load_dotenv
from git import Repo

load_dotenv()

GH_TOKEN = os.getenv("GH_TOKEN")

FileInfo = namedtuple("FileInfo", ("name", "last_modified", "row_count"))


class BaseData(ABC):
    def __init__(self, file: str):
        self.file = file

    @property
    @abstractmethod
    def pattern(self) -> str:
        return ""

    def get_links(self) -> Iterable[str]:
        for line in self.file.splitlines():
            if url := re.match(self.pattern, line):
                yield url.group(1)

    @abstractmethod
    def get_last_modified(self, url: str) -> datetime.datetime | None: ...

    @abstractmethod
    def get_info(self) -> Iterable[FileInfo]: ...


def validate_git_file_path(url: str) -> str:
    a, b = url.split("/")[-2:]
    if a in ("master", "main"):
        return b
    else:
        return f"{a}/{b}"


class GitHubData(BaseData):
    def _get_gh_link(self, url: str) -> re.Match[str] | None:
        groups = r"(?P<base>https:.+\/.+\.com\/)(?P<user>\w+)\/(?P<repo>\w+(-)?\w+?)\/"
        return re.match(groups, url)

    def get_last_modified(self, url: str) -> datetime.datetime | None:
        if match := self._get_gh_link(url):
            match = match.groupdict()
            user, repo = match.get("user"), match.get("repo")
            file = validate_git_file_path(url)
            api_url = f"https://api.github.com/repos/{user}/{repo}/commits?path={file}"
            headers = {"Authorization": f"Bearer {GH_TOKEN}"}
            res = requests.get(api_url, headers=headers if GH_TOKEN else None)
            if res.status_code == 200:
                return datetime.datetime.fromisoformat(
                    res.json()[0]["commit"]["author"]["date"]
                )
            else:
                print(f"got {res.status_code}: {res.text}")

    def read(self) -> Iterable[pd.DataFrame]:
        for url in self.get_links():
            yield self.get_last_modified(url).date()

    def get_info(self) -> Iterable[FileInfo]:
        for url in self.get_links():
            filename = url.split("/")[-1]
            file_markdown = f"[{filename}]({url})"
            last_modified = self.get_last_modified(url)
            row_count = len(pd.read_csv(url))

            yield FileInfo(file_markdown, last_modified, row_count)


class GitHubCSVData(GitHubData):
    pattern = r".+(https://raw.+/.+\.csv)"


class GitHubDatData(GitHubData):
    pattern = r".+(https://raw.+/.+\.dat)"


if __name__ == "__main__":
    readme = Path.cwd() / "README.md"
    f = readme.read_text()
    pattern = r"(.*?)(?=\n# Data Metadata)"
    f = re.search(pattern, f, re.DOTALL)
    f = f.group(0)

    datas = [GitHubCSVData(f), GitHubDatData(f)]
    df = pd.concat(
        [
            pd.DataFrame(data.get_info()).sort_values("last_modified", ascending=False)
            for data in datas
        ],
        axis=0,
    )
    df["last_modified"] = df.last_modified.dt.strftime("%F %T")
    df["row_count"] = df.row_count.apply(lambda x: f"{x:,}")

    push = False

    # Updating Metadata Table on README.md
    with open(readme, "r+") as f:
        line = f.readline()
        while line:
            if line == "# Data Metadata\n":
                pos = f.tell()
                f.truncate(pos)
                f.seek(pos)
                f.write("\n" + df.to_markdown(index=False))
                print("will push")
                push = True
                break
            line = f.readline()

    if push:
        # Commit and push
        current_repo = Repo(Path.cwd())
        current_repo.index.add(["README.md"])
        current_repo.index.commit(
            f"Auto: {datetime.datetime.now():%F} - Update data metadata"
        )
        origin = current_repo.remote(name="origin")
        origin.push()
