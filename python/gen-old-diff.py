#!/usr/bin/env python3

import git
import os
import pathlib
import stat
import sys

def get_file_from_blob(mode, blob, path):
    # Create sub-dir
    if not os.path.exists(os.path.dirname(path)):
        try:
            os.makedirs(os.path.dirname(path))
        except OSError as exc: # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise

    # Write blob content to file
    f = open(path, "wb")
    blob.stream_data(f)
    f.close()

    # Change file permission
    os.chmod(path, mode & (stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO))

def gen_diff_files(diffIdx, dir_old, dir_new, gen_old=None, gen_new=None):
    if gen_old:
        get_file_from_blob(diffIdx.a_mode, diffIdx.a_blob, dir_old + diffIdx.a_path)
    if gen_new:
        get_file_from_blob(diffIdx.b_mode, diffIdx.b_blob, dir_new + diffIdx.b_path)

if __name__ == "__main__":
    if len(sys.argv) != 3 and len(sys.argv) != 4:
        print("RUN: gen-old-diff.py PATH_TO_OUTPUT_FILE COMMIT_1 [COMMIT_2]")

    # FIXME: should point to the root of a git repos
    output = sys.argv[1]
    repo = git.Repo(pathlib.Path().absolute())

    dir_old = sys.argv[1] + "/old/"
    dir_new = sys.argv[1] + "/new/"

    # TODO: exception handling
    if len(sys.argv) == 4:
        commit_old = repo.commit(sys.argv[2])
        commit_new = repo.commit(sys.argv[3])
    else:
        commit_new = repo.commit(sys.argv[2])
        commit_old = commit_new.parents[0]

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

