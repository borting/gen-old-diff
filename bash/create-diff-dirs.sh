#!/bin/bash
# Input parameters:
#	$1:	SHA-1 ID of commit 1
#	$2:	SHA-1 ID of commit 2
#	$3: folder for storing diff files

ERR_VCS=1
ERR_INPUT=2

# Chech current folder is tracked by git
if !(git status -u no &> /dev/null); then
	echo "ERROR: ${PWD} is not tracked by git"
	exit ${ERR_VCS}
fi

# Check input parameters
if [ -z ${3+x} ]; then
    echo "RUN: create-diff-dirs.sh SHA1 SHA2 dest_folder"
    exit ${ERR_INPUT}
fi
if !(git cat-file -e $1 &> /dev/null); then
	echo "Error: SHA1 is no a valid object"
    exit ${ERR_INPUT}
fi
if !(git cat-file -e $2 &> /dev/null); then
	echo "Error: SHA2 is no a valid object"
    exit ${ERR_INPUT}
fi
if !(mkdir -p $3 &> /dev/null); then
	echo "Error: create $3 failed"
	exit ${ERR_INPUT}
fi

echo "Alles Gut!"
