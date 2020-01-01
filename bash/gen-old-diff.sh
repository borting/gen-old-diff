#!/bin/bash
#
# Input parameters:
#	$1:	SHA-1 key of commit 1
#	$2:	SHA-1 key of commit 2
#	$3: folder for storing diff files
#
# Types of git diff result:
#	https://git-scm.com/docs/git-diff#Documentation/git-diff.txt---diff-filterACDMRTUXB82308203
#
# Types of git object
#	https://git-scm.com/book/en/v2/Git-Internals-Git-Objects

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
else
	OLD_DIR=$3/old
	NEW_DIR=$3/new
fi

# Generate file from blob object
# Parameters:
#	$1: file mode
#	$2: SHA-1 key of blob object
#	$3: file path
function gen_file()
{
	# Create parent folder
	mkdir -p "$(dirname "$3")"

	# Obtain file from blob object and change file mode
	git cat-file blob $2 > $3
	chmod ${1:3:6} $3
}

# Obtain git diff results between two commits 
DIFF_RESULTS=`git diff --raw $1 $2`

# Parse git diff results line by line and generate files from blob objects
while IFS=$'\t :' read -r -a DIFF_FILE ; do
	DIFF_TYPE=${DIFF_FILE[5]}
	case "${DIFF_TYPE::1}" in
		M)	# Modified
			#echo "(M)odify ${DIFF_FILE[6]}"
			gen_file ${DIFF_FILE[1]} ${DIFF_FILE[3]} $OLD_DIR/${DIFF_FILE[6]}
			gen_file ${DIFF_FILE[2]} ${DIFF_FILE[4]} $NEW_DIR/${DIFF_FILE[6]}
			;;
		R)	# Renamed
			#echo "(R)ename ${DIFF_FILE[6]} to ${DIFF_FILE[7]}"
			gen_file ${DIFF_FILE[1]} ${DIFF_FILE[3]} $OLD_DIR/${DIFF_FILE[6]}
			gen_file ${DIFF_FILE[2]} ${DIFF_FILE[4]} $NEW_DIR/${DIFF_FILE[7]}
			;;
		D)	# Deleted
			#echo "(D)elete ${DIFF_FILE[6]}"
			gen_file ${DIFF_FILE[1]} ${DIFF_FILE[3]} $OLD_DIR/${DIFF_FILE[6]}
			;;
		C)	# Copied
			#echo "(C)opy ${DIFF_FILE[6]} to ${DIFF_FILE[7]}"
			gen_file ${DIFF_FILE[2]} ${DIFF_FILE[4]} $NEW_DIR/${DIFF_FILE[7]}
			;;
		A)	# Added
			#echo "(A)dd ${DIFF_FILE[6]}"
			gen_file ${DIFF_FILE[2]} ${DIFF_FILE[4]} $NEW_DIR/${DIFF_FILE[6]}
			;;
#		T)	# Changed
#			#echo "(U)Change ${DIFF_FILE[6]}"
#			;;
#		U)	# Unmerged
#			#echo "(U)nmerge ${DIFF_FILE[6]}"
#			;;
		*)
			echo -e "\e[0;31mWARNING: ${DIFF_FILE[1]} ${DIFF_FILE[2]} ${DIFF_FILE[3]} "\
				"${DIFF_FILE[4]} ${DIFF_FILE[5]}\t${DIFF_FILE[6]}\t${DIFF_FILE[7]}\e[0m"
			;;
	esac
done <<< "${DIFF_RESULTS}"

