function source_util_funcs() {
#
#-----------------------------------------------------------------------
#
# Set necessary directory variables. NOTE: The "USHdir" should be provided
# as an argument
#
#-----------------------------------------------------------------------
#
  local bashutils_dir="${1}/bash_utils"
#
#-----------------------------------------------------------------------
#
# Source the file that sources YAML files as if they were bash
#
#-----------------------------------------------------------------------
#
  . ${bashutils_dir}/source_yaml.sh
}
source_util_funcs $USHdir


