#!/bin/bash

#
#-----------------------------------------------------------------------
#
# This script loads the workflow modulefile and conda environment for a
# given machine. It is a central place for all other scripts, so any
# general or machine-specific changes to the process for loading the
# environment should be done here.
#
#-----------------------------------------------------------------------
#

function usage() {
  cat << EOF_USAGE
Usage: source $0 PLATFORM MODULEDIR

OPTIONS:
   PLATFORM - name of machine you are on
      (e.g. derecho | hera | jet )
   MODULEDIR - directory where modulefiles are located
EOF_USAGE
}

# Make sure machine name is passed as first argument
if [ $# -lt 2 ]; then
  usage
  exit 1
fi

# help message
if [ "$1" == "--help" ] || [ "$1" == "-h" ]; then
  usage
  exit 0
fi

# Set machine name to lowercase
machine=${1,,}
moduledir=${2}
# Get home directory
scrfunc_fp=$( readlink -f "${BASH_SOURCE[0]}" )
scrfunc_dir=$( dirname "${scrfunc_fp}" )
HOMEdir=$( dirname "${scrfunc_dir}" )

# Source modulefile for this machine
WFLOW_MOD_FN="vx_${machine}"
module purge
module use "${moduledir}"
module load "${WFLOW_MOD_FN}" > /dev/null 2>&1 || { echo "ERROR:
Loading of platform-specific module file (WFLOW_MOD_FN) for the workflow 
task failed:
  WFLOW_MOD_FN = \"${WFLOW_MOD_FN}\""; exit 1; }

# Activate conda
[[ ${SHELLOPTS} =~ nounset ]] && has_mu=true || has_mu=false

$has_mu && set +u

if [ ! -z $(command -v conda) ]; then
  conda activate hafs_vx
fi

$has_mu && set -u

# List loaded modulefiles
module --version
module list

