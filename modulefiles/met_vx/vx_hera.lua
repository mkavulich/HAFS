help([[
This module loads python environment for running HAFS METplus verification tasks on
the NOAA RDHPC machine Hera
]])

whatis([===[Loads libraries needed for running HAFS METplus verification tasks on Hera ]===])

load("rocoto")

load("conda")

if mode() == "load" then
   LmodMsgRaw([===[Please do the following to activate conda:
       > conda activate hafs_vx
]===])
end
