#!/bin/bash -x
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
ERR_COMPRESS=6

# Check current folder is tracked by git
if !(git status -u no &> /dev/null); then
	echo "ERROR: ${PWD} is not tracked by git"
	exit ${ERR_VCS}
fi

# Check input parameters
if [ -z ${3+x} ]; then
	echo "RUN: create-diff-dirs.sh COMMIT_1 COMMIT_2 PATH_TO_OUTPUT_FILE"
    exit ${ERR_INPUT}
fi

# Check commit ID is valid
if !(git cat-file -e $1 &> /dev/null); then
	echo "Error: COMMIT_1 is no a valid commit object"
    exit ${ERR_SHAID}
fi
if !(git cat-file -e $2 &> /dev/null); then
	echo "Error: COMMIT_2 is no a valid commit object"
    exit ${ERR_SHAID}
fi

# Check output directory is valid
OUT_DIR=$(dirname $3)
OUT_FILE=$(basename $3)
if !(mkdir -p ${OUT_DIR} &> /dev/null); then
	echo "Error: create ${OUT_DIR} failed"
	exit ${ERR_DEST}
fi

# Create temporary directory
TEMP_DIR=`mktemp -d`
if [ ! -d "${TEMP_DIR}" ]; then
	echo "Error: failed to create temporary directory"
	exit ${ERR_TEMP}
fi

# Create old and new directories
OLD_DIR=${TEMP_DIR}/old
NEW_DIR=${TEMP_DIR}/new
mkdir -p ${OLD_DIR} ${NEW_DIR}

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

# Check diff results
vim -c "set diffopt+=iwhite" -c "DirDiff ${OLD_DIR} ${NEW_DIR}"

# Check compression command is supported
function has()
{
	which $1 > /dev/null \
		&& return 0 || (echo "Error: $1 is not supported"; return 1)
}

# Macro for compression
function compress()
{
	cd ${TEMP_DIR}
	${1} ${OUT_DIR}/${OUT_FILE} * && (cd -; return 0) || (cd -; return 1)
}

# Run compression
EXIT_CODE=0
if [[ "${OUT_FILE}" == *.tar.gz ]] || [[ "${OUT_FILE}" == *.tgz ]]; then
	has tar && has gzip && compress "tar czf" || EXIT_CODE=$ERR_COMPRESS
elif [[ "${OUT_FILE}" == *.tar.xz ]] || [[ "${OUT_FILE}" == *.txz ]]; then
	has tar && has xz && compress "tar cJf" || EXIT_CODE=$ERR_COMPRESS
elif [[ "${OUT_FILE}" == *.tar.bz2 ]] || [[ "${OUT_FILE}" == *.tbz2 ]]; then
	has tar && has bzip2 && compress "tar cjf" || EXIT_CODE=$ERR_COMPRESS
elif [[ "${OUT_FILE}" == *.tar.Z ]]; then
	has tar && has compress && compress "tar cZf" || EXIT_CODE=$ERR_COMPRESS
elif [[ "${OUT_FILE}" == *.zip ]]; then
	has zip && compress "zip -r" || EXIT_CODE=$ERR_COMPRESS
elif [[ "${OUT_FILE}" == *.7z ]]; then
	has 7z && compress "7z a -r" || EXIT_CODE=$ERR_COMPRESS
elif [[ "${OUT_FILE}" == *.rar ]]; then
	has rar && compress "rar a -r" || EXIT_CODE=$ERR_COMPRESS
else
	mv ${TEMP_DIR} ${OUT_DIR}/${OUT_FILE}
fi

# Remove temporary directory
rm -rf ${TEMP_DIR}

exit ${EXIT_CODE}
