#!/bin/bash

#
#-----------------------------------------------------------------------
#
# This script loads the appropriate modules and conda environment for
# HAFS verification workflow tasks.
#
#-----------------------------------------------------------------------
#

if [ "$#" -ne 2 ]; then

    print_err_msg_exit "
Incorrect number of arguments specified:

  Number of arguments specified:  $#

Usage:

  ${0} machine task_script

where the arguments are defined as follows:

  machine: The name of the current platform

  task_script:
  The full path to the script to run a given task.  This
  script will launch this J-job using the \"exec\" command (which will
  first terminate this script and then launch the j-job; see man page of
  the \"exec\" command).
"

fi

# Save arguments
#
machine=${1,,}
script_to_run="$2"

# Load modules and refresh conda environment (in case user environment had a different one loaded)

module use "${MODULESdir}"
module load "vx_${machine}.lua"
set +u
conda deactivate
conda activate hafs_vx
set -u

echo "Launching job script ${script_to_run}"

source "${script_to_run}"
