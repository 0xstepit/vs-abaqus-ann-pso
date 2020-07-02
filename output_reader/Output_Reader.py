# Required libraries
import numpy as np
from odbAccess import *
from abaqus import*
from abaqusConstants import*
import visualization
import os

# Modify parameter to choose the output folder to consider
mesh_size = 10
F_egv = 1
scale = 1000  # divide the force values
stacking_sequence = 'symmetric_balanced'
data_set = 'large1.65'
load_case = 'axial'
fiber_path = 'harmlin'
param = 2

# Define variables according to the load case
if load_case == 'axial':
    f_name = 'RF'  # reaction force
    f_dir = 0
    disp_name = 'U'  # linear displacement
    disp_dir = 0
if load_case == 'torsion':
    f_name = 'RM'  # reaction moment
    f_dir = 0
    disp_name = 'UR'  # angular displacement
    disp_dir = 0

# Output folder
results_folder = '../dataset/' + load_case + '/' + stacking_sequence + '/'\
                 + str(param) + 'x/' + fiber_path + '/abaqus_analysis/'

path = os.getcwd()  # path of this script
os.chdir(results_folder)  # move to output folder

# Iterate over files in the current folder
for set_tmp in os.listdir('.'):

    # If set_tmp is a folder do
    if os.path.isdir(set_tmp):

        output_name = 'output_' + set_tmp + '.csv'  # create file to store analysis

        outputFile = open(output_name, 'w')  # open output file
        outputFile.write('Model, Buckling, Stiffness \n')  # header

        os.chdir(set_tmp)  # move to the considered set folder

        # Iterate over samples' folders
        for i in range(1, len(os.listdir('.'))+1):
            sample = 'sample' + str(i)
            os.chdir(sample)

            #  Results from buckling analysis
            name_bck = 'bck_' + sample + '.odb'
            odbObject_bck = session.openOdb(name=name_bck)

            #  Extracting First Eigenvalue
            frames = odbObject_bck.steps['Buckling force step'].frames
            egv1 = frames[1].description
            dummy = egv1.split('=')[1]
            eigenvalue = float(dummy)
            F_cr = F_egv * eigenvalue

            odbObject_bck.close()

            #  Results from linear static analysis
            name_stiff = 'stiff_' + sample + '.odb'
            odbObject_stiff = session.openOdb(name=name_stiff)

            # Depending on the mesh size, the reference points for the load and constraint change,
            # N.B. the value of the node is fixed by the knowledge of the model by the author. This
            # part che be automatized by using node set in the model generation
            if mesh_size == 5:
                loadedNode = odbObject_stiff.rootAssembly.instances["ASSEMBLY_CYLINDER"].getNodeFromLabel(53535)
                clampedNode = odbObject_stiff.rootAssembly.instances["ASSEMBLY_CYLINDER"].getNodeFromLabel(53536)
            elif mesh_size == 10:
                loadedNode = odbObject_stiff.rootAssembly.instances["ASSEMBLY_CYLINDER"].getNodeFromLabel(13349)
                clampedNode = odbObject_stiff.rootAssembly.instances["ASSEMBLY_CYLINDER"].getNodeFromLabel(13350)

            #  Extracting First Eigenvalue
            frames = odbObject_stiff.steps['Linear static force step'].frames
            U = frames[-1].fieldOutputs[disp_name]
            RF = frames[-1].fieldOutputs[f_name]
            force = RF.getSubset(region=clampedNode).values[0].data[f_dir]
            displacement = U.getSubset(region=loadedNode).values[0].data[disp_dir]

            # Write on output file
            outputFile.write(sample + ', ' + str(F_cr / 1000) + ', ' + str(-force / displacement / 1000) + '\n')

            # Go back to actual set folder
            os.chdir('..')

        # Go back to the folder containing the data sets
        os.chdir('..')
