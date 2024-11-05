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

# Set the input and output directories here
INPUT_DIR=${CDNOSCRUB}/HAFS_rt_hfsa_dev_ww3/
OUTPUT_DIR=${EXPTDIR}/${START_DATE}

# Since TCPairs is set up to run once per cycle, the START_DATE will always equal the END_DATE
END_DATE=${START_DATE}
INC=3600
#MODEL='OFCL'

# We need to know if this is a HAFS-A or HAFS-B run; this comes from the HAFS "RUN" variable (how wonderfully descriptive)
# The carets (^^) make the string all-caps
MODEL=${RUN^^}

# Format for A-deck forecast track file
ADECK_TEMPLATE='{cyclone}l.{init?fmt=%Y%m%d%H}.hfsa.trak.atcfunix'

# Export the variables
export INPUT_DIR
export OUTPUT_DIR
export START_DATE
export END_DATE
export INC
export BASIN
export STORM_ID
export ADECK_TEMPLATE
export BEST_TRACK
export LOG_MET_VERBOSITY
export LOG_LEVEL
export MODEL

# Create experiment dir and run tcpairs
mkdir -p ${OUTPUT_DIR}/tcpairs
cd ${OUTPUT_DIR}/tcpairs

python ${METPLUS_ROOT}/ush/run_metplus.py -c ${SCRIPTSdir}/${TCVX_CONF}
