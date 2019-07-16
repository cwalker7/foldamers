#!/usr/bin/python

import numpy as np
import matplotlib.pyplot as pyplot
# OpenMM utilities
import mdtraj as md
from simtk import unit
# foldamers utilities
from foldamers.src.cg_model.cgmodel import basic_cgmodel
from foldamers.src.ensembles.ens_build import 
from cg_openmm.src.simulation.tools import *

def optimize_lj(cgmodel,base_epsilon=cgmodel.epsilons['bb_bb_eps'],sigma_attempts=3,epsilon_attempts=3):
        """
        Optimize the Lennard-Jones interaction potential parameters (sigma and epsilon, for all interaction types) in the model defined by a cgmodel() class object, using a combination of replica exchange simulations and re-weighting techniques.

        Parameters
        ----------

        :param cgmodel: CGModel() class object, default = None
        :type cgmodel: class.

        :param sigma_attempts: 

        Returns
        -------

        cgmodel: CGModel() class object.

        """

        # Set variable model settings
        base_sigma = cgmodel.sigmas['bb_bb_sigma'] # Lennard-Jones interaction distance
        base_epsilon = cgmodel.epsilons['bb_bb_epsilon'] # Lennard-Jones interaction strength
        sigma_list = [(base_sigma).__add__(i * base_sigma.unit) for i in [ j * 0.2 for j in range(-2,3,1)]]
        epsilon_list = [(base_epsilon).__add__(i * base_epsilon.unit) for i in [ j * 0.2 for j in range(-1,3,1)]]
        sigma_epsilon_list = np.zeros((len(sigma_list),len(epsilon_list)))

        for sigma_index in range(len(sigma_list)):
          for epsilon_index in range(len(epsilon_list)):
            sigma = sigma_list[sigma_index]
            epsilon = epsilon_list[epsilon_index]
            print("Evaluating the energy for a model with:")
            print("sigma="+str(sigma)+" and epsilon="+str(epsilon))
            # Build a coarse grained model
            cgmodel = basic_cgmodel(polymer_length=polymer_length, backbone_length=backbone_length, sidechain_length=sidechain_length, sidechain_positions=sidechain_positions, mass=mass, sigma=sigma, epsilon=epsilon, bond_length=bond_length)

            # Run replica exchange simulations with this coarse grained model.
            replica_energies,replica_temperatures = replica_exchange(cgmodel.topology,cgmodel.system,cgmodel.positions)
            print(replica_energies)

        

        return(cgmodel)

def optimize_parameter(cgmodel,optimization_parameter,optimization_range_min,optimization_range_max,steps=None):
        """
        """
        if steps == None: steps = 100
        step_size = ( optimization_range_max - optimization_range_min ) / 100
        parameter_values = [step*step_size for step in range(1,steps)]
        potential_energies = []
        for parameter in parameter_values:
          cgmodel.optimization_parameter = parameter
          positions,potential_energy,time_step =  minimize_structure(cgmodel.topology,cgmodel.system,cgmodel.positions,temperature=300.0 * unit.kelvin,simulation_time_step=None,total_simulation_time=1.0 * unit.picosecond,output_pdb='minimum.pdb',output_data='minimization.dat',print_frequency=1)
          potential_energies.append(potential_energy)

        best_value = min(potential_energies)

        return(best_value,potential_energies,parameter_values)