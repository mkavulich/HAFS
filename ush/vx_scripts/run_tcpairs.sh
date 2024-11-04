#!/bin/bash -l
#set -x

# Run these commands before running this script
#export TOP_DIR=/glade/work/dtcrt/METplus/casper/components
#module use $TOP_DIR/METplus/installations/modulefiles
#module load metplus/5.1.0


# Set the METplus location here
module use /mnt/lfs4/HFIP/hfv3gfs/role.epic/spack-stack/spack-stack-1.6.0/envs/unified-env-rocky8/install/modulefiles/
module load Core/stack-intel/2021.5.0
module load stack-intel-oneapi-mpi/2021.5.1
module load metplus/5.1.0

set -x
#metplus_ROOT is set by loading metplus module above
export METPLUS_ROOT=$metplus_ROOT

# Import variables from var_defns.yaml
. source_yaml.sh
for sect in hafs platform user verification workflow; do
  source_yaml ${VAR_DEFNS_FP} ${sect}
done
echo `env` > env.out

# Set conf file names here
TCVX_CONF='tcpairs.conf'
TCST_CONF='tcstat.conf'

# Set the input and output directories here
INPUT_DIR='/mnt/lfs5/HFIP/dtc-hurr/Michael.Kavulich/HAFS/from_bri/hafs_r2o/sample_data'
OUTPUT_DIR=${EXPTDIR}

# Set variables to export here
START_DATE=2021082612
END_DATE=2021082612
INC=21600
BASIN='AL'
STORM_ID='09'
#MODEL='OFCL'
MODEL_TMPL='HFSA'

# If statement to get proper file template
if [[ ${MODEL_TMPL} = "OFCL" ]]
then
    ADECK_TEMPLATE='a{basin}{cyclone}{init?fmt=%Y}.dat'
elif [[ ${MODEL_TMPL} = "H221" ]]
then
    ADECK_TEMPLATE='a{basin}{cyclone}{init?fmt=%Y}_{model}_HWRF_{init?fmt=%Y%m%d%H}.dat'
elif [[ ${MODEL_TMPL} = "M221" ]]
then
    ADECK_TEMPLATE='a{basin}{cyclone}{init?fmt=%Y}_{model}_HMON_{init?fmt=%Y%m%d%H}.dat'
else
    ADECK_TEMPLATE='a{basin}{cyclone}{init?fmt=%Y}_{model}_HAFS_{init?fmt=%Y%m%d%H}.dat'
fi

# Export the variables
export INPUT_DIR
export OUTPUT_DIR
export START_DATE
export END_DATE
export INC
export BASIN
export STORM_ID
export MODEL_TMPL
export ADECK_TEMPLATE
export BEST_TRACK

# Create experiment dir and run tcpairs
mkdir -p ${EXPTDIR}/tcpairs
cd ${EXPTDIR}/tcpairs

python ${METPLUS_ROOT}/ush/run_metplus.py -c ${SCRIPTSdir}/${TCVX_CONF}
