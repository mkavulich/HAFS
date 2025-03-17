help([[
This module loads python environment for running HAFS METplus verification tasks on
the NOAA RDHPC machine Hera
]])

whatis([===[Loads libraries needed for running HAFS METplus verification tasks on Hera ]===])
load ("contrib")
load ("noaatools")
prepend_path("MODULEPATH", "/work/noaa/epic/role-epic/spack-stack/orion/spack-stack-1.6.0/envs/fms-2024.01/install/modulefiles/")
load ("Core/stack-intel/2021.9.0")
load ("stack-intel-oneapi-mpi/2021.9.0")
load ("metplus/6.0.0")

load("rocoto")

load("conda")

if mode() == "load" then
   LmodMsgRaw([===[Please do the following to activate conda:
       > conda activate hafs_vx
]===])
end
