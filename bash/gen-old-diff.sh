#!/bin/bash
# Copyright 2020, Borting Chen <bortingchen@gmail.com>
#
# This file is licensed under the GPL v2,
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
ERR_SHAID=3
ERR_DEST=4
ERR_TEMP=5
ERR_GIT=6
ERR_ZIP=7
ERR_USR=8

# Configure the name of output diff directories
OLD_DIR=${OLD_DIR:-old}
NEW_DIR=${NEW_DIR:-new}

# Configure tool for diff checking
DIRDIFFTOOL=${DIRDIFFTOOL:-}

# Check current folder is tracked by git
if !(git status -u no &> /dev/null); then
	echo "ERROR: ${PWD} is not tracked by git"
	exit ${ERR_VCS}
fi

# Check the number of input parameters
if [ $# -ne 2 ]  && [ $# -ne 3 ] ; then
	echo "RUN: `basename "$0"` PATH_TO_OUTPUT_FILE COMMIT_1 [COMMIT_2]"
    exit ${ERR_INPUT}
fi

COMMIT_1=$2
COMMIT_2=$3
# If COMMIT_2 is empty, generate diff b/w {COMMIT_1}~1 and {COMMIT_1}
if [ -z ${COMMIT_2} ]; then
	COMMIT_2=${COMMIT_1}
	COMMIT_1="${COMMIT_1}~1"
fi

# Check commit IDs are valid
if !(git cat-file -e ${COMMIT_1} &> /dev/null); then
	echo "Error: COMMIT_1 is no a valid commit object"
    exit ${ERR_SHAID}
fi
if !(git cat-file -e ${COMMIT_2} &> /dev/null); then
	echo "Error: COMMIT_2 is no a valid commit object"
    exit ${ERR_SHAID}
fi

# Check output directory is valid
OUT_FILE=$(basename $1)
if [[ $1 == /* ]]; then
	OUT_DIR=$(dirname $1)
else
	OUT_DIR=`pwd`/$(dirname $1)
fi
if !(mkdir -p ${OUT_DIR} &> /dev/null); then
	echo "Error: create ${OUT_DIR} failed"
	exit ${ERR_DEST}
fi

# Create temporary directory
TEMP_DIR=
function gen_temp_dir()
{
	TEMP_DIR=`mktemp -d`
	if [ ! -d "${TEMP_DIR}" ]; then
		echo "Error: failed to create temporary directory"
		return ${ERR_TEMP}
	fi

	# Create old and new directories
	OLD_DIR=${TEMP_DIR}/${OLD_DIR}
	NEW_DIR=${TEMP_DIR}/${NEW_DIR}
	mkdir -p ${OLD_DIR} ${NEW_DIR}
	return 0
}

# Get file from git blob object
# Parameters:
#	$1: file mode
#	$2: SHA-1 key of blob object
#	$3: file path
function get_file()
{
	# Create parent folder
	mkdir -p "$(dirname "$3")"

	# Obtain file from blob object and change file mode
	git cat-file blob ${2//.} > $3
	chmod ${1:3:6} $3
}

# Extract files having difference and store them into OLD_DIR and NEW_DIR
function gen_diff_files_to_dirs() {
	# Obtain git diff results between two commits 
	DIFF_RESULTS=`git diff --raw ${COMMIT_1} ${COMMIT_2}`
	
	# Parse git diff results line by line and generate files from blob objects
	while IFS=$'\t :' read -r -a DIFF_FILE ; do
		DIFF_TYPE=${DIFF_FILE[5]}
		case "${DIFF_TYPE::1}" in
			M)	# Modified
				#echo "(M)odify ${DIFF_FILE[6]}"
				get_file ${DIFF_FILE[1]} ${DIFF_FILE[3]} $OLD_DIR/${DIFF_FILE[6]}
				get_file ${DIFF_FILE[2]} ${DIFF_FILE[4]} $NEW_DIR/${DIFF_FILE[6]}
				;;
			R)	# Renamed
				#echo "(R)ename ${DIFF_FILE[6]} to ${DIFF_FILE[7]}"
				get_file ${DIFF_FILE[1]} ${DIFF_FILE[3]} $OLD_DIR/${DIFF_FILE[6]}
				get_file ${DIFF_FILE[2]} ${DIFF_FILE[4]} $NEW_DIR/${DIFF_FILE[7]}
				;;
			D)	# Deleted
				#echo "(D)elete ${DIFF_FILE[6]}"
				get_file ${DIFF_FILE[1]} ${DIFF_FILE[3]} $OLD_DIR/${DIFF_FILE[6]}
				;;
			C)	# Copied
				#echo "(C)opy ${DIFF_FILE[6]} to ${DIFF_FILE[7]}"
				get_file ${DIFF_FILE[2]} ${DIFF_FILE[4]} $NEW_DIR/${DIFF_FILE[7]}
				;;
			A)	# Added
				#echo "(A)dd ${DIFF_FILE[6]}"
				get_file ${DIFF_FILE[2]} ${DIFF_FILE[4]} $NEW_DIR/${DIFF_FILE[6]}
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
}

# Check diff results
function check_diff_files() {
	if [ ! -z ${DIRDIFFTOOL} ]; then
		${DIRDIFFTOOL} ${1} ${2} || { echo "Abort diff generation."; return 1; }
	fi

	return 0
}

# Check compression command is supported
function has()
{
	which $1 > /dev/null \
		&& return 0 || { echo "Error: $1 is not supported"; return 1; }
}

# Execute diff generation and compression
function run()
{
	local RETVAL=0

	# Create temporary directory
	gen_temp_dir || return $ERR_TEMP

	# Generate old-school diff to temporary directory
	gen_diff_files_to_dirs || { rm -rf ${TEMP_DIR}; return $ERR_GIT; }

	# Check generated diff results
	check_diff_files ${OLD_DIR} ${NEW_DIR} || { rm -rf ${TEMP_DIR}; return $ERR_USR; }
	
	# Run compresiion if method is specified
	if [ $# -ne 0 ]; then
		cd ${TEMP_DIR}
		${1} ${OUT_DIR}/${OUT_FILE} * || RETVAL=$ERR_ZIP
		cd -
	else
		mv ${TEMP_DIR} ${OUT_DIR}/${OUT_FILE}
	fi

	# Remove temporary directory
	rm -rf ${TEMP_DIR}

	return $RETVAL
}

# Run compression
if [[ "${OUT_FILE}" == *.tar.gz ]] || [[ "${OUT_FILE}" == *.tgz ]]; then
	has tar && has gzip || exit $ERR_ZIP
	run "tar czf"
elif [[ "${OUT_FILE}" == *.tar.xz ]] || [[ "${OUT_FILE}" == *.txz ]]; then
	has tar && has xz || exit $ERR_ZIP
	run "tar cJf"
elif [[ "${OUT_FILE}" == *.tar.bz2 ]] || [[ "${OUT_FILE}" == *.tbz2 ]]; then
	has tar && has bzip2 || exit $ERR_ZIP
	run "tar cjf"
elif [[ "${OUT_FILE}" == *.tar.Z ]]; then
	has tar && has compress || exit $ERR_ZIP
	run "tar cZf"
elif [[ "${OUT_FILE}" == *.zip ]]; then
	has zip || exit $ERR_ZIP
	run "zip -r"
elif [[ "${OUT_FILE}" == *.7z ]]; then
	has 7z || exit $ERR_ZIP
	run "7z a -r"
elif [[ "${OUT_FILE}" == *.rar ]]; then
	has rar || exit $ERR_ZIP
	run "rar a -r"
else
	run
fi

exit $?
