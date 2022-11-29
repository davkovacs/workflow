import os
from ase.calculators.psi4 import Psi4 
from wfl.calculators import generic
from wfl.autoparallelize.autoparainfo import AutoparaInfo
from wfl.configset import ConfigSet, OutputSpec

from ase.io import read, write

ats_in = read("SP_e2.xyz", ":")
print("evaluating ", len(ats_in), "configs...")
configset = ConfigSet(ats_in)
outputspec = OutputSpec("DFT_SP_e2.xyz")

ref_parameters = dict(charge=0, # assuming charge is 0
                      multiplicity=1,
                      method="wB97M-D3BJ", basis="def2-TZVPPD", # SPICE dataset settings
                      memory='16GB', num_threads=16, # number of threads used in each DFT calculation 
                      maxiter=150,
                      task='gradient')
calculator = (Psi4, [], ref_parameters)

generic.run(
    inputs = configset, 
    outputs = outputspec, 
    calculator = calculator, 
    properties = ["energy", "forces"],
    output_prefix = "psi4_", 
    autopara_info = AutoparaInfo(
        num_python_subprocesses = 8, # number of configs evaluated in parallel
        num_inputs_per_python_subprocess=1   
    )
)

print("! DONE !")
