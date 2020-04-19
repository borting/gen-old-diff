# gen-old-diff
Save the changes between two git commits into a pair of folders, one contains original files and the other contains changed files.

## Purpose
When backporting fixes/features to an eariler release, some engineers prefer to review patches in an ordinary diff format, putting original files in one folder and changed files in another folder.
This helps them to use comparison tools, like Meld, WinMerge and KDiff3, to merge changes back to the earlier release. 
This project provides a script to generate such an ordinary diff from two git commits.
The output structure would be like:
```
diff/
|-- old/
|   |-- fileA.c
|   |-- fileB.c
|   |-- dir1/
|       |-- fileC.c
|-- new/
    |-- fileA.c
    |-- fileB.c
    |-- dir1/
        |-- fileC.c
```

## Usage
```console
$ gen-old-diff.sh COMMIT_1 COMMIT_2 OUTPUT
```
* COMMIT_1 and COMMIT_2 are SHA-1 key of git commits.
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
The compression format that this script executes depeneds on the file extension specifed in **OUTPUT**.
If the file extension does not match any valid compression method, the results would be a folder.
Currently, the following compression formats and file extension are supported:
| Compression Format | File Extension |
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
The folder name can be configured by **OLD_DIR** and **NEW_DIR** variables.

For example, saving diff results to _original/_ and _patch/_ folders
```console
$ OLD_DIR=original NEW_DIR=patch gen-old-diff.sh c3fb102 103756c /home/user/diff_results.zip
```

### Diff Results Double-Checking
To double check diff results, specifing diff tools in **DIRDIFFTOOL** environment variable.

Example1: Use [Meld](https://meldmerge.org/) for double checking
```console
$ DIRDIFFTOLL=meld gen-old-diff.sh c3fb102 103756c /home/user/diff_results.zip
```
Example2: Using **vimdiff** with [dirdiff plugin](https://github.com/will133/vim-dirdiff) by adding the following to **_~/.bashrc_**
```
function dirdiff() {
  vim -c "set diffopt+=iwhite" -c "DirDiff ${1} ${2}"
}
export -f dirdiff
export DIRDIFFTOOL=dirdiff
```
