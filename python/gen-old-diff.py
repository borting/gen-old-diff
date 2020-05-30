#!/usr/bin/env python3

import git
import os
import stat
import sys
from pathlib import Path

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

def check_output(path):
    out_file = path.name
    # TODO: use try ... except (FileExistsError, FileNotFoundError)
    if path.parents[0].exists():
        out_dir = path.parents[0].mkdir(parents=True, exist_ok=True)
    out_dir = path.parents[0]

    return out_dir, out_file


if __name__ == "__main__":
    if len(sys.argv) != 3 and len(sys.argv) != 4:
        print("RUN: gen-old-diff.py PATH_TO_OUTPUT_FILE COMMIT_1 [COMMIT_2]")

    # FIXME: check cwd is a git repo
    cwd = os.getcwd()
    repo = git.Repo(cwd)

    # Parse and check output directoy and output file name
    out_dir, out_file = check_output(Path(sys.argv[1]).absolute())
    print(out_dir, out_file)

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

