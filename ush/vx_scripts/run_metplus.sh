#!/bin/bash -l
set -x

#metplus_ROOT is set by loading metplus module, which should be done already
export METPLUS_ROOT=$metplus_ROOT
echo "Using METPLUS in $metplus_ROOT"

# Import variables from var_defns.yaml
. source_yaml.sh
sections=(
  hafs
  platform
  user
  verification
  workflow
)
for sect in ${sections[*]} ; do
  source_yaml ${VAR_DEFNS_FP} ${sect}
done

# Set conf file names here
CONF_FILE="${METPLUSTOOLNAME}.conf"

# Set the input and output directories here
INPUT_DIR=${CDNOSCRUB}/${SUBEXPT}
OUTPUT_DIR=${EXPTDIR}/${START_DATE}

# Since tasks are set up to run once per cycle, the START_DATE will always equal the END_DATE
END_DATE=${START_DATE}
OUTPUT_INC_HR=$(($OUTPUT_INC / 3600))

# Format for A-deck forecast track file
ADECK_TEMPLATE="${STORM_ID}l.{init?fmt=%Y%m%d%H}.hfsa.trak.atcfunix"

# We need to know if this is a HAFS-A or HAFS-B run; this comes from the HAFS "RUN" variable (how wonderfully descriptive)
# The carets (^^) make the string all-caps
MODEL=${RUN^^}

# Export the variables needed for conf files
export INPUT_DIR
export OUTPUT_DIR
export START_DATE
export FCST_LEN_HRS
export OUTPUT_INC_HR
export BASIN
export STORM_ID
export ADECK_TEMPLATE
export BEST_TRACK
export LOG_MET_VERBOSITY
export LOG_LEVEL
export MODEL
export FORECAST_DIR
export VX_FCST_INPUT_BASEDIR
export FCST_FN_TEMPLATE

# Create experiment dir and run specified metplus tool
mkdir -p ${OUTPUT_DIR}/${METPLUSTOOLNAME}
cd ${OUTPUT_DIR}/${METPLUSTOOLNAME}

python ${METPLUS_ROOT}/ush/run_metplus.py -c ${SCRIPTSdir}/${CONF_FILE}
