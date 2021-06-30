#!/usr/bin/env python

import dataclasses
import os
import pathlib
import sqlite3
from dataclasses import dataclass

from icecream import ic


@dataclass(frozen=True)
class RawFileInfo:
    path: str
    dirname: str
    basename: str
    suffix: str
    is_dir: bool
    prefix: str
    # UNIX file mode e.g. "chmod 700"
    # mode: int
    inode: int
    size_bytes: int
    nlinks: int


def fs_entries(root_path):
    with os.scandir(root_path) as scanner:
        for e in scanner:
            prefix, full_suffix = os.path.splitext(e.name)
            suffix = full_suffix.lstrip(".")
            is_dir = e.is_dir(follow_symlinks=False)
            fstat = os.stat(e.path)
            entry = RawFileInfo(
                basename="" if is_dir else e.name,
                dirname=e.path if is_dir else os.path.dirname(e.path),
                path=e.path,
                is_dir=is_dir,
                prefix=prefix,
                suffix="" if is_dir else suffix,
                inode=e.inode(),
                size_bytes=fstat.st_size,
                nlinks=fstat.st_nlink,
            )

            yield entry
            if e.is_dir():
                yield from fs_entries(e)


def init_db(fname: os.PathLike) -> sqlite3.Connection:
    con = sqlite3.connect(fname)
    try:
        with con:
            con.execute(
                """
                CREATE TABLE raw_file_info (
                    basename TEXT,
                    dirname TEXT,
                    path TEXT PRIMARY KEY,
                    suffix TEXT,
                    is_dir INTEGER,
                    prefix TEXT,
                    inode INTEGER,
                    size_bytes INTEGER,
                    nlinks INTEGER
                )
            """
            )
            con.execute(
                """
                CREATE VIEW IF NOT EXISTS duplicates AS
                SELECT file.path, COUNT(file.inode), file.inode, file.nlinks
                FROM raw_file_info file
                GROUP BY file.inode
                HAVING COUNT(file.inode) > 1
            """
            )
    except sqlite3.OperationalError as err:
        ic("The db was inited already")

    return con


def main():
    root_path = pathlib.Path(".").absolute()
    all_entries = fs_entries(root_path)
    import itertools

    # all_entries = itertools.islice(all_entries, 22)

    con = init_db("files.db")

    for count, entry in enumerate(all_entries):
        if count % 100 == 0:
            ic(count)
        with con:
            con.execute(
                """
                INSERT INTO raw_file_info
                VALUES (:basename, :dirname, :path, :suffix, :is_dir, :prefix, :inode, :size_bytes, :nlinks)
                """,
                dataclasses.asdict(entry),
            )


if __name__ == "__main__":
    main()
