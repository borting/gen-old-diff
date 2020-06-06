#!/usr/bin/env python3
#
# Copyright 2020, Borting Chen <bortingchen@gmail.com>
#
# This file is licensed under the GPL v2.
#

import git
import gitdb
import stat
import sys
import tempfile
from enum import IntEnum
from pathlib import Path

def get_file_from_blob(mode, blob, path):
    # Create sub-dir is necessary
    path.parents[0].mkdir(parents=True, exist_ok=True)

    # Write blob content to file
    with path.open(mode="wb") as f:
        blob.stream_data(f)
        
    # Change file permission
    path.chmod(mode & 0o777)
    print(path)

def gen_diff_files(diffIdx, dir_old, dir_new, gen_old=None, gen_new=None):
    if gen_old:
        get_file_from_blob(diffIdx.a_mode, diffIdx.a_blob, dir_old.joinpath(diffIdx.a_path))
    if gen_new:
        get_file_from_blob(diffIdx.b_mode, diffIdx.b_blob, dir_new.joinpath(diffIdx.b_path))

class OutExt(IntEnum):
    DIR = 1
    TGZ = 2
    TXZ = 4
    TBZ2 = 8
    TZ = 16
    ZIP = 32
    P7Z = 64
    RAR = 128
    ERR = 0

class UnsupportCompressException(Exception):
    def __init__(self, msg):
        super().__init__(msg)

class UnknownCompressException(Exception):
    def __init__(self, msg):
        super().__init__(msg)

def check_output(path):
    # Check if parent dir exists
    # TODO: use try ... except (FileExistsError, FileNotFoundError)
    if path.parents[0].exists():
        path.parents[0].mkdir(parents=True, exist_ok=True)

    # Parse file extension
    suffixes = "".join(path.suffixes)
    out_ext = {
        "": OutExt.DIR,
        ".tar.gz": OutExt.TGZ,
        ".tgz": OutExt.TGZ,
        ".tar.xz": OutExt.TXZ,
        ".txz": OutExt.TXZ,
        ".tar.bz2": OutExt.TBZ2,
        ".tbz2": OutExt.TBZ2,
        ".tar.Z": OutExt.TZ,
        ".zip": OutExt.ZIP,
        ".7z": OutExt.P7Z,
        ".rar": OutExt.RAR
    }.get(suffixes, OutExt.ERR)

    # Unknown compression file extension
    if out_ext == OutExt.ERR:
        raise UnknownCompressException(suffixes)

    # Unsupported compression method
    if out_ext & (OutExt.TZ | OutExt.P7Z | OutExt.RAR):
        raise UnsupportCompressException(suffixes)

    return out_ext

class CommitIdException(Exception):
    def __init__(self, msg):
        super().__init__(msg)

def check_commit(repo, rev):
    try:
        commit = repo.commit(rev)
    except ValueError as err:   # the input 40-digit hex number string is invalid
        raise CommitIdException(rev)
    except gitdb.exc.BadName as err:    # the input commit ID (after parsing) is invalid
        raise CommitIdException(rev)
    return commit

if __name__ == "__main__":
    if len(sys.argv) != 3 and len(sys.argv) != 4:
        print("RUN: gen-old-diff.py PATH_TO_OUTPUT_FILE COMMIT_1 [COMMIT_2]")

    # Check current working dir is a valid repos
    try:
        repo = git.Repo(Path())
    except git.exc.InvalidGitRepositoryError as err:
        print("Error: {} is not a git repository".format(err))
        sys.exit(1)
    except git.exc.NoSuchPathError as err:
        print("Error: {} does not exist".format(err))
        sys.exit(1)

    # Check commit IDs are valid
    try:
        if len(sys.argv) == 4:
            commit_old = check_commit(repo, sys.argv[2])
            commit_new = check_commit(repo, sys.argv[3])
        else:
            commit_new = check_commit(repo, sys.argv[2])
            try:
                commit_old = commit_new.parents[0]
            except IndexError as err:
                print("Error: {} is the first commit".format(sys.argv[2]))
                sys.exit(1)
    except CommitIdException as err:
        print("Error: {} is not a valid commit ID".format(err))
        sys.exit(1)

    # Check output parent directoy and compression method
    out_file = Path(sys.argv[1]).resolve()
    out_ext = check_output(out_file)
    print(out_ext)

    with tempfile.TemporaryDirectory() as tmp_dir:
        dir_old = Path(tmp_dir + "/old/")
        dir_new = Path(tmp_dir + "/new/")

        for diffIndex in commit_old.diff(commit_new):
            #print(diffIndex.change_type)
            action = {
                    "M": {"gen_old": True, "gen_new": True},
                    "R": {"gen_old": True, "gen_new": True},
                    "D": {"gen_old": True, "gen_new": False},
                    "C": {"gen_old": False, "gen_new": True},
                    "A": {"gen_old": False, "gen_new": True}
                    }.get(diffIndex.change_type, None)
            gen_diff_files(diffIndex, dir_old, dir_new, **action)

        try:
            dir_old.rename(out_file/dir_old.name)
            dir_new.rename(out_file/dir_new.name)
        except OSError as err:
            print("Error: {} is not empty".format(err.filename2))

