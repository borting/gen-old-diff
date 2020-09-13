#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright 2020, Borting Chen <bortingchen@gmail.com>
#
# This file is licensed under the GPL v2.
#

import argparse
import sys
from core import *
from pathlib import Path

def _parseSysArgv(argv):
    parser = argparse.ArgumentParser(prog=Path(argv[0]).name)
    #parser.add_argument('-p', '--preview', type=str, help="Path to the tool for diff results preview", dest="preview", metavar="PREVIEW_TOOL")
    parser.add_argument('-r', '--repos', type=str, help="Path to Git repository", default="", dest="repos", metavar="GIT_REPOS")
    parser.add_argument('--new', type=str, help="Name of the dir saving modified files", default="new", dest="newDir", metavar="DIR_NAME")
    parser.add_argument('--old', type=str, help="Name of the dir saving original files", default="old", dest="oldDir", metavar="DIR_NAME")
    parser.add_argument('OUTPUT', type=str, help="Path to output dir/file")
    parser.add_argument('COMMIT_NEW', type=str, help=" ID/tag of modified commit")
    parser.add_argument('COMMIT_OLD', nargs='?', type=str, help="ID/tag of original commit")

    return vars(parser.parse_args(argv[1:]))

def main(sysArgv):
    argv = _parseSysArgv(sysArgv)

    try:
        god = GOD(Path(argv["repos"]).resolve(), argv["COMMIT_NEW"], argv["COMMIT_OLD"])
    except GitRepoException as err:
        print(err)
        sys.exit(1)
    except CommitIdException as err:
        print(err)
        sys.exit(1)

    # Check output file/dir
    outFile = Path(argv["OUTPUT"])
    ext = "".join(outFile.suffixes)

    if not ext:
        outFile.mkdir(parents=False, exist_ok=False)
    elif ext in [".tgz", ".tar.gz", ".tbz2", ".tar.bz2", ".txz", ".tar.xz", ".zip"]:
        outFile.touch(exist_ok=False)
    else:
        print("Error: Not supported compression format {}".format(ext))
        sys.exit(1)

    try:
        if (ext == ".tar.gz") or (ext == ".tgz"):
            action = genTarCompress(outFile, "w:gz")
        elif (ext == ".tar.xz") or (ext == ".txz"):
            action = genTarCompress(outFile, "w:xz")
        elif (ext == ".tar.bz2") or (ext == ".tbz2"):
            action = genTarCompress(outFile, "w:bz2")
        elif (ext == ".zip"):
            action = genzipCompress(outFile)
        else:
            action = genDiffDirs(outFile)
    except FileExistsError as err:
        print("Error: File already exists: '{}'".format(err.filename))
        sys.exit(1)
    except FileNotFoundError as err:
        print("Error: No such directory '()'".format(Path(err.filename).parents[0]))
        sys.exit(1)

    # Generate diff files to output
    god.generate(action)

if __name__ == "__main__":
    main(sys.argv)
