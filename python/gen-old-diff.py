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
from pathlib import Path

def get_file_from_blob(mode, blob, path):
    # Create sub-dir is necessary
    path.parents[0].mkdir(parents=True, exist_ok=True)

    # Write blob content to file
    with path.open(mode="wb") as f:
        blob.stream_data(f)
        
    # Change file permission
    path.chmod(mode & 0o777)

def gen_diff_files(diffIdx, dir_old, dir_new, gen_old=None, gen_new=None):
    if gen_old:
        get_file_from_blob(diffIdx.a_mode, diffIdx.a_blob, Path(dir_old + diffIdx.a_path))
    if gen_new:
        get_file_from_blob(diffIdx.b_mode, diffIdx.b_blob, Path(dir_new + diffIdx.b_path))

def check_output(path):
    out_file = path.name
    # TODO: use try ... except (FileExistsError, FileNotFoundError)
    if path.parents[0].exists():
        out_dir = path.parents[0].mkdir(parents=True, exist_ok=True)
    out_dir = path.parents[0]

    return out_dir, out_file

class CommitIdException(Exception):
    def __init__(self, msg):
        super().__init__(msg)

def check_commit(repo, rev):
    try:
        commit = repo.commit(rev)
#    except gitdb.exc.BadName as err:
#        print("Error: {} is not a valid commit ID".format(err.args[0]))
#        raise CommitIdException(rev)
#    except ValueError as err:
#        print("Error: {} is not a valid commit ID".format(err.args[5:45]))
#        raise CommitIdException(rev)
    except Exception as err:
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
    if len(sys.argv) == 4:
        commit_old = repo.commit(sys.argv[2])
        commit_new = repo.commit(sys.argv[3])
    else:
        commit_new = repo.commit(sys.argv[2])
        try:
            commit_old = commit_new.parents[0]
        except IndexError as err:
            print("Error: {} is the first commit".format(sys.argv[2]))a
            sys.exit(1)

    # Parse and check output directoy and output file name
    out_dir, out_file = check_output(Path(sys.argv[1]).absolute())
    print(out_dir, out_file)

    dir_old = sys.argv[1] + "/old/"
    dir_new = sys.argv[1] + "/new/"

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

