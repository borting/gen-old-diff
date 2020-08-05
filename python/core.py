#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright 2020, Borting Chen <bortingchen@gmail.com>
#
# This file is licensed under the GPL v2.
#

import git
import gitdb
import tarfile
import tempfile
import zipfile
from enum import IntEnum
from pathlib import Path

class GitRepoException(Exception):
    def __init__(self, msg):
        super().__init__(msg)

class CommitIdException(Exception):
    def __init__(self, msg):
        super().__init__(msg)

class GOD():
    def __init__(self, repoPath, newCmt, oldCmt=None):

        # Check git repos is valid
        try:
            if isinstance(repoPath, Path):
                self._repo = git.Repo(str(repoPath))
            else:
                self._repo = git.Repo(repoPath)
        except git.exc.InvalidGitRepositoryError as err:
            raise GitRepoException("Error: {} is not a git repository".format(err))
        except git.exc.NoSuchPathError as err:
            raise GitRepoException("Error: {} does not exist".format(err))

        # Check commit IDs are valid
        self._newCmt = self._checkCommit(newCmt)
        if oldCmt:
            self._oldCmt = self._checkCommit(oldCmt)
        else:
            try:
                self._oldCmt = self._newCmt.parents[0]
            except IndexError as err:
                raise CommitIdException("Error: {} is the first commit".format(newCmt))

    def _checkCommit(self, rev):
        try:
            commit = self._repo.commit(rev)
        except ValueError as err:   # the input 40-digit hex number string is invalid
            raise CommitIdException("Error: {} is not a valid commit ID".format(rev))
        except gitdb.exc.BadName as err:    # the input commit ID (after parsing) is invalid
            raise CommitIdException("Error: {} is not a valid commit ID".format(rev))
        return commit

    def _getFileFromBlob(self, mode, blob, path):
        # Create parent dir
        path.parents[0].mkdir(parents=True, exist_ok=True)
    
        # Write blob content to file
        with path.open(mode="wb") as f:
            blob.stream_data(f)
            
        # Change file permission
        path.chmod(mode & 0o777)
    
    def generate(self, action, oldDirName="old", newDirName="new"):
        # Create temp dir
        with tempfile.TemporaryDirectory() as tmp:
            tmpDir = Path(tmp)
            oldDir = tmpDir/oldDirName
            newDir = tmpDir/newDirName

            # Get raw diff b/w two commits and save files in difference to tmpDir
            for diffIdx in self._oldCmt.diff(self._newCmt):
                #print(diffIndex.change_type)
                if diffIdx.a_mode:
                    self._getFileFromBlob(diffIdx.a_mode, diffIdx.a_blob, oldDir/diffIdx.a_path)
                if diffIdx.b_mode:
                    self._getFileFromBlob(diffIdx.b_mode, diffIdx.b_blob, newDir/diffIdx.b_path)

            # Handle files in difference
            action(tmpDir)

def genDiffDirs(outFile):
    def action(tmpDir):
        for path in tmpDir.glob("*"):
            path.rename(outFile/path.name)
    return action
    
def genTarCompress(outFile, mode):
    def action(tmpDir):
        with tarfile.open(str(outFile), mode) as tf:
            for path in tmpDir.glob("**/*"):
                if path.is_file():
                    tf.add(str(path), str(path.relative_to(tmpDir)))
    return action

def genZipCompress(outFile):
    def action(tmpDir):
        with zipfile.ZipFile(str(outFile), "w", zipfile.ZIP_DEFLATED) as zf:
            for path in tmpDir.glob("**/*"):
                if path.is_file():
                    zf.write(str(path), str(path.relative_to(tmpDir)))
    return action

if __name__ == "__main__":
    pass

