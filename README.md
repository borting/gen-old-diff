# Generate Old Diff
Save the changes between two git commits into a pair of folders, one contains modified files and the other contains their original copy, and archive the folders to a compressed file.
The file structure in the output would be like:
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
$ gen-old-diff.sh OUTPUT COMMIT_NEW [COMMIT_OLD]
```
* OUTPUT could be a folder or a compressed file, depends on the specified file extension. If the file extension does not match any valid compression method, the results would be a folder.
* COMMIT_NEW and COMMIT_OLD could be commit IDs or tags. If COMMIT_OLD is omitted, then difference between COMMIT_NEW and COMMIT_NEW~1 are generated.

### Supported Compression Format
Currently, the script supports following compression formats and file extension:
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
By default, the script saves the original files to **_old/_** folder and the modified files to **_new/_** folder.
The folder name can be configured by **OLD_DIR** and **NEW_DIR** environment variables.

For example, saving diff results to _original/_ and _modified/_ folders
```console
$ OLD_DIR=original NEW_DIR=modified gen-old-diff.sh /home/user/diff_results.zip c3fb102 103756c
```

### Diff Results Double Checking
To double check diff results, specifing diff tools in **DIRDIFFTOOL** environment variable.

Example1: Using **vimdiff** with [dirdiff plugin](https://github.com/will133/vim-dirdiff) by adding the following to **_~/.bashrc_**
```
function dirdiff() {
  vim -c "set diffopt+=iwhite" -c "DirDiff ${1} ${2}"
}
export -f dirdiff
export DIRDIFFTOOL=dirdiff
```
-- This also supports aborting diff generation by typing ":cq" on exit.

Example2: Use [Meld](https://meldmerge.org/) for double checking
```console
$ DIRDIFFTOLL=meld gen-old-diff.sh /home/user/diff_results.zip c3fb102 103756c
```
