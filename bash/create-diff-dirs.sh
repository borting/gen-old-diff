#!/bin/bash
# Input parameters:
#	$1:	SHA-1 ID of commit 1
#	$2:	SHA-1 ID of commit 2
#	$3: folder for storing diff files
# Types of git diff result
#	https://git-scm.com/docs/git-diff#Documentation/git-diff.txt---diff-filterACDMRTUXB82308203

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

# Obtain git diff results between two commits
DIFF_RESULTS=`git diff --name-status ${1} ${2}`
#DIFF_RESULTS=`git diff -C --name-status ${1} ${2}`

while IFS=$'\t' read -r -a DIFF_FILE ; do
	DIFF_TYPE=${DIFF_FILE[0]}
	case "${DIFF_TYPE::1}" in
		M)	# Modified
			echo "${DIFF_FILE[1]} is modified";;
		R)	# Renamed
			echo "Move ${DIFF_FILE[1]} to ${DIFF_FILE[2]}";;
		D)	# Deleted
			echo "${DIFF_FILE[1]} is deleted";;
		C)	# Copied
			echo "Copy ${DIFF_FILE[1]} to ${DIFF_FILE[2]}";;
		A)	# Added
			echo "${DIFF_FILE[1]} is added";;
		T)
			echo "${DIFF_FILE[1]} is changed";;
		*)
			echo -e "Unknown diff type:\t${DIFF_FILE[0]}\t${DIFF_FILE[1]}\t${DIFF_FILE[2]}"
	esac
done <<< "${DIFF_RESULTS}"

