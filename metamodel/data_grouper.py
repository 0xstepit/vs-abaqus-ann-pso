"""
Author: Stefano Francesco Pitton

Mail: stefanofrancesco.pitton@polimi.it

Created: 13/04/2020

Description:
------------
Code to group inputs and outputs of the analysis into one file.

"""
# Required libraries
import numpy as np
import pandas as pd
import os
import shutil

# Modify parameter to choose the output folder to consider
fiber_path = 'harmlin'
load_case = 'torsion'
param = 4
folder_ss = 'symmetric_balanced'


# Output folder
results_folder = '../dataset/' + load_case + '/' + folder_ss + '/' + str(param) + 'x/' + fiber_path + '/'

# Read model info
info = pd.read_csv(results_folder + 'model_info.csv', sep=",")
info.index = ['Value']
eff_plies = int(info['EffectivePlies'].values)
sets = []
if 'Train' in info:
    sets.append('train')
if 'Val' in info:
    sets.append('val')
if 'Test' in info:
    sets.append('test')

# Create the folder to store the data
folder = load_case + '/' + folder_ss + '/' + str(param) + 'x/' + fiber_path
try:
    if not os.path.isdir(folder):
        os.makedirs(folder)
except OSError:
    print('Error: Creating directory. ' + folder)

for curr_set in sets:
    output_folder = results_folder + 'abaqus_analysis/'

    # Load the input features
    col_dict = {}
    for ply in range(1, eff_plies + 1):
        if fiber_path == 'harmlin':
            col_dict.update({'ply' + str(ply): ['Amplitude' + str(ply), 'PhaseShift' + str(ply), 'Omega' + str(ply),
                                                'Beta' + str(ply)]})
        elif fiber_path == 'linear':
            col_dict.update({'ply' + str(ply): ['T0_' + str(ply), 'T1_' + str(ply), 'T2_' + str(ply)]})

        elif fiber_path == 'constant':
            col_dict.update({'ply' + str(ply): ['theta_' + str(ply)]})

    for ply in range(1, eff_plies + 1):
        foo = pd.read_csv(results_folder + curr_set + '/ply' + str(ply) + '.csv',
                          names=col_dict['ply' + str(ply)], sep=",", skiprows=1)  # placeholder
        if ply == 1:
            data = foo.copy()
        else:
            data = pd.concat([data, foo], axis=1)

    data.index = ['sample' + str(i) for i in range(1, len(data) + 1)]

    target = pd.read_csv(output_folder + 'output_' + curr_set + '.csv',
                         names=['Buckling', 'Stiffness'], sep=",", skiprows=1)

    target.index = ['sample' + str(i) for i in range(1, len(data) + 1)]

    data_grouped = pd.concat([data, target], axis=1)

    if curr_set == 'train':
        D = data_grouped.copy()
    else:
        D = pd.concat([D, data_grouped], axis=0)

# Copy features boundaries
shutil.copy(results_folder + '/features_min_max.csv', folder + '/')

# Copy model info
shutil.copy(results_folder + '/model_info.csv', folder + '/')

D.to_csv(folder + '/data.csv', index=False, float_format='%.3f')
