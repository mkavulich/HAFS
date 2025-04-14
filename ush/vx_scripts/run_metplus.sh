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
OUTPUT_DIR=${EXPTDIR}/${START_DATE}/${METPLUSTOOLNAME}

OUTPUT_INC_HR=$(($OUTPUT_INC / 3600))

# Create experiment dir
mkdir -p ${OUTPUT_DIR}/

# Format for A-deck forecast track file
ADECK_TEMPLATE="${STORM_ID}l.{init?fmt=%Y%m%d%H}.hfsa.trak.atcfunix"

# We need to know if this is a HAFS-A or HAFS-B run; this comes from the HAFS "RUN" variable (how wonderfully descriptive)
# The carets (^^) make the string all-caps
MODEL=${RUN^^}

# Settings to substitute in METplus conf templates
settings="\
  'exptdir': '${EXPTDIR}'
  'input_dir': '${INPUT_DIR:-}'
  'output_dir': '${OUTPUT_DIR:-}'
  'start_date': '${START_DATE:-}'
  'fcst_len_hrs': '${FCST_LEN_HRS:-}'
  'output_inc_hr': '${OUTPUT_INC_HR:-}'
  'basin': '${BASIN:-}'
  'storm_id': '${STORM_ID:-}'
  'adeck_template': '${ADECK_TEMPLATE:-}'
  'best_track': '${BEST_TRACK:-}'
  'log_met_verbosity': '${LOG_MET_VERBOSITY:-}'
  'log_level': '${LOG_LEVEL:-}'
  'model': '${MODEL:-}'
  'forecast_dir': '${FORECAST_DIR:-}'
  'vx_fcst_input_basedir': '${VX_FCST_INPUT_BASEDIR:-}'
  'fcst_fn_template': '${FCST_FN_TEMPLATE:-}'
"

# Render METplus conf file from template with uwtools
tmpfile=$( readlink -f "$(mktemp ./met_plus_settings.XXXXXX.yaml)")
printf "%s" "$settings" > "$tmpfile"
uw template render \
  -i ${SCRIPTSdir}/${CONF_FILE} \
  -o ${OUTPUT_DIR}/${CONF_FILE} \
  --verbose \
  --values-file "${tmpfile}" \
  --search-path "/"

err=$?
rm $tmpfile
if [ $err -ne 0 ]; then
  echo "Error rendering template for METplus config. Contents of input are:"
  echo "$settings"
fi

# Create experiment dir and run specified metplus tool
cd ${OUTPUT_DIR}

python ${METPLUS_ROOT}/ush/run_metplus.py -c ${SCRIPTSdir}/common.conf -c ${OUTPUT_DIR}/${CONF_FILE}
