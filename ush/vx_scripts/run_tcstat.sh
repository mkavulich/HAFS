#!/bin/bash -l
#set -x

#metplus_ROOT is set by loading metplus module, which should be done already
export METPLUS_ROOT=$metplus_ROOT

# Import variables from var_defns.yaml
. source_yaml.sh
for sect in hafs platform user verification workflow; do
  source_yaml ${VAR_DEFNS_FP} ${sect}
done

CONF_FILE='tcstat.conf'

# Set the input and output directories here
OUTPUT_DIR=${EXPTDIR}/${START_DATE}

# Since TCStat is set up to run once per cycle, the START_DATE will always equal the END_DATE
END_DATE=${START_DATE}
INC=3600
#MODEL='OFCL'

# We need to know if this is a HAFS-A or HAFS-B run; this comes from the HAFS "RUN" variable (how wonderfully descriptive)
# The carets (^^) make the string all-caps
MODEL=${RUN^^}

# Export the variables
export OUTPUT_DIR
export START_DATE
export END_DATE
export INC
export BASIN
export STORM_ID
export LOG_MET_VERBOSITY
export LOG_LEVEL
export MODEL

# Create experiment dir and run tcstat
mkdir -p ${OUTPUT_DIR}/tcstat
cd ${OUTPUT_DIR}/tcstat

python ${METPLUS_ROOT}/ush/run_metplus.py -c ${SCRIPTSdir}/${CONF_FILE}
