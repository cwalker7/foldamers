#!/usr/bin/python

from simtk import unit
from simtk.openmm.app.pdbfile import PDBFile
# foldamers utilities
import foldamers
from foldamers.src.cg_model.cgmodel import CGModel
from foldamers.src.utilities.util import *
from foldamers.src.utilities.iotools import *
from cg_openmm.src.cg_mm_tools.cg_openmm import *

# OpenMM simulation settings
output_pdb = "test_simulation.pdb"
output_data = "test_simulation.dat"
box_size = 10.00 * unit.nanometer # box width
cutoff = box_size / 2.0 * 0.99
simulation_time_step = 0.002 * unit.picosecond # Units = picoseconds
temperature = 300.0 * unit.kelvin
print_frequency = 1 # Number of steps to skip when printing output
total_simulation_time = 10.0 * unit.picosecond # Units = picoseconds

# Coarse grained model settings
backbone_length = 3 # Number of backbone beads
sidechain_length = 2 # Number of sidechain beads
sidechain_positions = [1] # Index of backbone bead on which the side chains are placed
polymer_length = 2 # Number of monomers in the polymer
mass = 12.0 * unit.amu # Mass of beads
sigma = 8.4 * unit.angstrom # Lennard-Jones interaction distance
bond_length = 1.0 * unit.angstrom # bond length
bond_force_constant = 5e6 # Units = kJ/mol/A^2
constrain_bonds = True
epsilon = 0.5 * unit.kilocalorie_per_mole # Lennard-Jones interaction strength
charge = 0.0 * unit.elementary_charge # Charge of beads

# Build a coarse grained model
cgmodel = CGModel(polymer_length=polymer_length,backbone_length=backbone_length, sidechain_length=sidechain_length, sidechain_positions = sidechain_positions, mass = mass, sigma = sigma, epsilon = epsilon, bond_length = bond_length, bond_force_constant = bond_force_constant, charge = charge,constrain_bonds=constrain_bonds)

# Confirm the validity of our trial positions
positions = cgmodel.positions
nonbonded_interactions = get_nonbonded_interaction_list(cgmodel)
distances = [distance(positions[interaction[0]],positions[interaction[1]]) for interaction in nonbonded_interactions]
print(distances)
exit()

# Write the initial coordinates to a PDB file
pdb_file = "init_coord.pdb"
write_pdbfile(cgmodel,pdb_file)

# Build a topology using the PDB file as input
pdb_mm_obj = PDBFile(pdb_file)
topology = pdb_mm_obj.getTopology()
#print("Number of bonds is: "+str(topology.getNumBonds()))
test_file = open("test.pdb",'w')
PDBFile.writeFile(topology,cgmodel.positions,test_file)
test_file.close()

# Build an OpenMM simulation object
simulation = build_mm_simulation(topology,cgmodel.system,cgmodel.positions,temperature=temperature,simulation_time_step=simulation_time_step,total_simulation_time=simulation_time_step*print_frequency,output_pdb=output_pdb,output_data=output_data,print_frequency=print_frequency)

if constrain_bonds: simulation.context.applyConstraints(unit.Quantity(0.1,unit.angstrom))
# Test the construction of our simulation object

# Figure out how many terms we have in the energy function

# Verify the non-bonded energy
nonbonded_interactions = get_nonbonded_interaction_list(cgmodel)
sum_nonbonded_energies = unit.Quantity(0.0,cgmodel.epsilon.unit)
for interaction in nonbonded_interactions:
 dist = distance(positions[interaction[0]],positions[interaction[1]])
 nonbonded_energy = calculate_nonbonded_energy(cgmodel,particle1=interaction[0],particle2=interaction[1])
 sum_nonbonded_energies = sum_nonbonded_energies.__add__(nonbonded_energy)

# Decompose the energy
state = simulation.context.getState(getEnergy=True,getForces=True,getParameters=True)
print("The nonbonded energy is: "+str(calculate_nonbonded_energy(cgmodel).in_units_of(unit.kilojoules_per_mole)))
potential_energy = state.getPotentialEnergy()
print("The potential energy is: "+str(potential_energy.in_units_of(unit.kilojoules_per_mole)))
kinetic_energy = state.getKineticEnergy()
print("The kinetic energy is: "+str(kinetic_energy.in_units_of(unit.kilojoules_per_mole)))
forces = state.getForces()
print("The forces are: "+str(forces))
energy_parameters = state.getParameters()
print("The energy parameters are: "+str(energy_parameters))
#parameter_derivatives = state.getEnergyParameterDerivatives()
#print("The energy parameter derivatives are: "+str(parameter_derivatives))

# Run the simulation
total_steps = round(total_simulation_time._value/simulation_time_step._value)
simulation.step(total_steps)
print("Finished simulation.")

# Confirm that the bond lengths were preserved
pdb_mm_obj = PDBFile(output_pdb)
num_frames = pdb_mm_obj.getNumFrames()
print(num_frames)
bond_list = cgmodel.get_bond_list()
for frame in range(num_frames):
 positions = pdb_mm_obj.getPositions(frame=frame)
 for bond in bond_list:
  dist = distance(positions[bond[0]],positions[bond[1]])
  print(dist)
  if dist < 0.8 * bond_length or dist > 1.2 * bond_length:
    print("Error: the bond is breaking between particles")
    print(str(bond[0])+" "+str(bond[1])+" in frame "+str(frame))
exit()
