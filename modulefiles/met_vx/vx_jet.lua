help([[
This module loads python environment for running HAFS METplus verification tasks on
the NOAA RDHPC machine Jet
]])

whatis([===[Loads libraries needed for running HAFS METplus verification tasks on Jet ]===])

prepend_path("MODULEPATH", "/contrib/spack-stack/spack-stack-1.6.0/envs/fms-2024.01/install/modulefiles/")
load ("Core/stack-intel/2021.5.0")
load ("stack-intel-oneapi-mpi/2021.5.1")
load ("metplus/5.1.0")

load("rocoto")

load("conda")

if mode() == "load" then
   LmodMsgRaw([===[Please do the following to activate conda:
       > conda activate hafs_vx
]===])
end
