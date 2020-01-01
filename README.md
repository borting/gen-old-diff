# gen-old-diff
Generate old-school patch, a pair of folders containing original and changed files, from two git commits.

## Why use this
Although modern VCS, like git, suggest (and provide commands) to send diff in patch format, some tech engineers still prefer to send diff in a pair of folders, one contains original files and the other contains changed files.
(The naming of the paired folders are also various, such as old/new, origin/patch, before/after, etc.)
This project provides a shell script to quickly generate such an old-school patch from two git commits.

## How to use this
```
$ gen-old-diff.sh COMMIT_1 COMMIT_2 DEST_DIR
```
* COMMIT_1 and COMMIT_2 are SHA-1 key of commits.
* DEST_DIR is the path to the paired folders, old and new, which saves original and changed files accordingly. 
