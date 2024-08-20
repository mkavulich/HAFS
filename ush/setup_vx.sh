#!/bin/bash

# usage instructions
usage () {
cat << EOF_USAGE
Usage: $0 --platform=PLATFORM [OPTIONS] ... [TARGETS]

OPTIONS
  -h, --help
      show this help guide
  -p, --platform=PLATFORM
      name of machine you are on
      (e.g. cheyenne | hera | jet | orion | wcoss2)
  --conda-dir=CONDA_DIR
      installation location for miniconda (ush subdirectory by default)
  -v, --verbose
      build with verbose output

EOF_USAGE
}

# print usage error and exit
usage_error () {
  printf "ERROR: $1\n" >&2
  usage >&2
  exit 1
}

# print error message and exit
error () {
  printf "ERROR: $1\n" >&2
  exit 2
}


# default settings
CONDA_BUILD_DIR="conda"
VERBOSE=false

# process required arguments
if [[ ("$1" == "--help") || ("$1" == "-h") ]]; then
  usage
  exit 0
fi

# process optional arguments
while :; do
  case $1 in
    --help|-h) usage; exit 0 ;;
    --platform=?*|-p=?*) PLATFORM=${1#*=} ;;
    --platform|--platform=|-p|-p=) usage_error "$1 requires argument." ;;
    --conda-dir=?*) CONDA_BUILD_DIR=${1#*=} ;;
    --conda-dir|--conda-dir=) usage_error "$1 requires argument." ;;
    --verbose|-v) VERBOSE=true ;;
    --verbose=?*|--verbose=) usage_error "$1 argument ignored." ;;
    # unknown
    -?*|?*) usage_error "Unknown option $1" ;;
    *) break
  esac
  shift
done

if [ "${VERBOSE}" = true ] ; then
  set -x
fi
# Ensure uppercase / lowercase ============================================
PLATFORM=$(echo ${PLATFORM} | tr '[A-Z]' '[a-z]')

# Set directory paths
USH_DIR=$(cd "$(dirname "$(readlink -f -n "${BASH_SOURCE[0]}" )" )" && pwd -P)
HAFS_DIR=$(dirname "${USH_DIR}")
CONDA_BUILD_DIR="$(readlink -f "${CONDA_BUILD_DIR}")"
MODULE_DIR=${HAFS_DIR}/modulefiles/met_vx
echo ${CONDA_BUILD_DIR} > ${USH_DIR}/conda_loc

# set PLATFORM (MACHINE)
MACHINE="${PLATFORM}"
printf "PLATFORM(MACHINE)=${PLATFORM}\n" >&2

# set MODULE_FILE for this platform/compiler combination
MODULE_FILE="vx_${PLATFORM}"
if [ ! -f "${MODULE_DIR}/${MODULE_FILE}.lua" ]; then
  printf "ERROR: module file does not exist for platform\n" >&2
  printf "  MODULE_FILE=${MODULE_FILE}\n" >&2
  printf "  PLATFORM=${PLATFORM}\n" >&2
  printf "Please make sure PLATFORM is set correctly\n" >&2
  printf "See ${MODULE_DIR} for valid PLATFORM options.\n" >&2
  usage >&2
  exit 64
fi

# build conda and conda environments
CONDA_ENV_NAME=hafs_vx
if [ ! -d "${CONDA_BUILD_DIR}" ] ; then
  echo "Downloading and installing conda in local directory"
  cat ${USH_DIR}/conda_loc
  os=$(uname)
  hardware=$(uname -m)
  installer=Miniforge3-${os}-${hardware}.sh
  curl -L -O "https://github.com/conda-forge/miniforge/releases/download/23.3.1-1/${installer}"
  bash ./${installer} -bfp "${CONDA_BUILD_DIR}"  || error "Failed to install conda, see detailed error message above"
  rm ${installer}
else
  echo "Conda directory ${CONDA_BUILD_DIR} already exists"
fi

echo "Checking conda environment"
source ${CONDA_BUILD_DIR}/etc/profile.d/conda.sh
conda activate
if ! conda env list | grep -q "^${CONDA_ENV_NAME}\s" ; then
  echo "Creating ${CONDA_ENV_NAME} conda environment"
  mamba env create -n hafs_vx --file hafs_vx_environment.yml  || error "Failed to create conda environment, see detailed error message above"
else
  echo "Conda environment ${CONDA_ENV_NAME} already exists"
fi


printf "\n===================================================\n"
printf "Verification conda environment set up successfully!\n"
printf "===================================================\n\n"
echo "To start a verification workflow:"
echo "  1. module use ${MODULE_DIR}"
echo "  2. module load ${MODULE_FILE}"
echo "  3. conda activate hafs_vx"

exit 0
