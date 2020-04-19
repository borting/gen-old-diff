# gen-old-diff
Save the changes between two git commits into a pair of folders, one contains original files and the other contains changed files.

## Purpose
When backporting fixes/features to an eariler release, some engineers prefer to review patches by putting original files in one folder and changed files to another folder, and comparing them using tools, like Meld, WinMerge, etc.
This project provides a script to generate such a patch from two git commits.
The structure of output would be like:
```
diff/
|--- old/
  |--- fileA.c
  |--- dir1/
    |-- fileB.c
|--- new/
  |--- fileA.c
  |--- dir1/
    |-- fileB.c
```

## Usage
```console
$ gen-old-diff.sh COMMIT_1 COMMIT_2 OUTPUT
```
* COMMIT_1 and COMMIT_2 are SHA-1 key of commits.
* OUTPUT could be a folder or a compressed file, depends on the file extension user specified.

Example1: Put diff results to a folder
```console
$ gen-old-diff.sh c3fb102 103756c /home/user/diff_results
```
Example2: Compress diff results to a gzip file
```console
$ gen-old-diff.sh c3fb102 103756c /home/user/diff_results.tar.gz
```

### Supported Compression Format
The compression method that this script executes depeneds on the file extension specifed in **OUTPUT**.
If the file extension does not match any valid compression method, the results would be a folder.
Currently, the following compression methods and file extension are supported:
| Compression Method  | File Extension |
| :------------------ | :------------- |
| gzip | .tar.gz, .tgz |
| xz | .tar.xz, .txz |
| bzip2 | .tar.bz2, .tbz2 |
| compress | .tar.Z |
| Zip | .zip |
| 7-Zip | .7z |
| RAR | .rar |

### Name of Result Folders
By default, the script saves the original files to **_old/_** folder and the changed files to **_new/_** folder.
The folder name can be configured by the following environment variables:
```
OLD_DIR=old_dir_name
NEW_DIR=new_dir_name
```
For example, saving diff results to _original/_ and _patch/_
```console
$ OLD_DIR=original NEW_DIR=patch gen-old-diff.sh c3fb102 103756c /home/user/diff_results.zip
```

### Diff Results Double-Checking
To double check diff results, specifing diff tools in **DIRDIFFTOOL** environment variable.

Example1: Use [Meld](https://meldmerge.org/) for double checking
```console
$ DIRDIFFTOLL=meld gen-old-diff.sh c3fb102 103756c /home/user/diff_results.zip
```
Example2: Using **vimdiff** with [dirdiff plugin](https://github.com/will133/vim-dirdiff) by adding following to **_~/.bashrc_**
```
function dirdiff() {
  vim -c "set diffopt+=iwhite" -c "DirDiff ${1} ${2}"
}
export -f dirdiff
export DIRDIFFTOOL=dirdiff
```
