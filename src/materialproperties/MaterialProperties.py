import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits import mplot3d
import csv


class MaterialProperties(object):
  """
    materialProperties = a list of M (T1, T2, df) tuples in ms/kHz
  """
  def __init__(self, materialAttr, plottingFlag=False):
    # Create options for the materials flag
    # by mapping the input value to a function
    optionsForMaterials = {'default' : self.__setDefaultMaterialProperties,
                           'bssfp'   : self.__setBSSFPMaterialProperties,
                           'fisp'    : self.__setFISPMaterialProperties,
                           'custom'  : self.__setCustomMaterialProperties }

    # Call the appropriate function to create the attributes for this class
    optionsForMaterials[materialAttr['type']](materialAttr)

    # Plot if requested      
    if plottingFlag == True:
      self.__plotThemMaterials()


  """
      DEFAULT: Sets the material tuples to GM,WM,CSF,Fat default values for 1.5T
  """
  def __setDefaultMaterialProperties(self, materialAttributes):
    # Create default GM/WM/CSF/Fat
    self.T1 = np.array([950, 600, 4500, 250])
    self.T2 = np.array([100,  80, 2200,  60])
    self.df = np.zeros((1))
    # Create the material tuples array
    self.__createSetOfTuples()

  """
      BSSFP: Sets the material tuples to T1/T2/df values from bSSFP paper
   """
  def __setBSSFPMaterialProperties(self, materialAttributes):
    # T1 ranges from 100ms to 5000ms with different timesteps
    self.T1 = np.concatenate((
          np.arange( 100,2020, 20),  # from 100ms to 2000ms dt = 20ms
          np.arange(2300,5300,300))) # from 2300ms to 5000ms dt = 300ms
    # T2 ranges from 20ms to 3000ms with different timesteps
    self.T2 = np.concatenate((
          np.arange( 20, 105,   5),  # from 20ms to 100ms dt = 5ms 
          np.arange(110, 210,  10),  # from 110ms to 200ms dt = 10ms
          np.arange(400,3200, 200))) # from 400ms to 3000ms dt = 200ms
    # Off-resonance freq from -400Hz to 400Hz with different steps
    dfTemp = np.concatenate((
          np.arange(  0, 41, 1),     # from 0Hz to 40Hz df = 1Hz
          np.arange( 42, 82, 2),     # from 42Hz to 80Hz df = 2Hz
          np.arange( 90,260,10),     # from 90Hz to 250Hz df = 10Hz
          np.arange(270,400,20)))    # from 270Hz to 400Hz df = 20Hz
    self.df = np.concatenate((
          -dfTemp[:1:-1], dfTemp))   # Add 0 and the negative side of spectrum
    # Convert kHz because kHz = ms^-1
    self.df = self.df * 1e-03;       

    # Create the material tuples array
    self.__createSetOfTuples()

  """
      FISP: Sets the material tuples to T1/T2/df values from FISP paper
  """
  def __setFISPMaterialProperties(self, materialAttributes):
    # T1 ranges from 
    self.T1 = np.concatenate((
          np.arange(  20,3010, 10),  # from   20ms to 3000ms dt =  10ms
          np.arange(3200,5200,200))) # from 3000ms to 5000ms dt = 200ms
    # T2 ranges from 
    self.T2 = np.concatenate((
          np.arange( 10, 305,   5),  # from  10ms to 300ms dt =  5ms
          np.arange(350, 550,  50))) # from 300ms to 500ms dt = 50ms
          
    # Off-resonance freq is 0
    self.df = np.zeros((1))

    # Create the material tuples array
    self.__createSetOfTuples()

  """
      Custom: Sets the material tuples to T1/T2/df values given by user
  """
  def __setCustomMaterialProperties(self, materialAttributes):
    # Set other properties
    filename = materialAttributes['filename'];
    
    # Create empty dictionary
    mat = {};
    
    # Read file
    with open(filename, 'r') as theFile:
      reader = csv.DictReader(theFile)
      # Each line
      for line in reader:
        # The keys (header of file)
        for myKey in line.keys():
          # Append to existing key
          if myKey in mat:
            mat[myKey] = np.append(mat[myKey], line[myKey]);
          # Or create new key with empty list
          else:
            mat[myKey] = [];
            mat[myKey] = np.append(mat[myKey], line[myKey]);
  
    # Populate the with the custom values
    self.T1 = [float(x) for x in np.unique(mat['T1'])];
    self.T2 = [float(x) for x in np.unique(mat['T2'])];
    self.df = [float(x) for x in np.unique(mat['df'])];
    
    # Create the material tuples array
    self.__createSetOfTuples()

  # Function that creates the set of tuples such that T2<=T1
  def __createSetOfTuples(self):
    # Calculate cardinal of each set
    N_T1 = len(self.T1); 
    N_T2 = len(self.T2);
    N_df = len(self.df);
    
    # Create placeholder for a temporary variable
    materialTuplesTemp = np.zeros((3, N_T1*N_T2*N_df))

    # Go through all tissue properties
    #  and create the material tuples such that T1 >= T2
    idx_M = 0;
    for idT1 in range(0,N_T1):       # T_1
      for idT2 in range(0,N_T2):     # T_2
        for idDf in range(0,N_df):   # df
            # Condition: T_2 <= T_1
            if self.T2[idT2] <= self.T1[idT1]:
                materialTuplesTemp[0, idx_M] = self.T1[idT1]
                materialTuplesTemp[1, idx_M] = self.T2[idT2]
                materialTuplesTemp[2, idx_M] = self.df[idDf]
                idx_M = idx_M + 1;

    print("Done")
    # Actual number of material tuples
    self.nMaterialTuples = idx_M;

    # Delete the unnecessary zeroes at the end of the array
    self.materialTuples = materialTuplesTemp[:, 0:self.nMaterialTuples]
        
    
  # Plots the material properties
  def __plotThemMaterials(self):
    print("\n~~~MATERIAL PROPERTIES~~~\n")

    # Create figure
    fig = plt.figure(figsize=(10,5))
    # Add subplot
    ax  = fig.add_subplot(111) # row-col-num
    # 3D projection
    #ax = plt.axes(projection='3d')
    # Plot the material properties
    ax.scatter(self.materialTuples[0,:], 
               self.materialTuples[1,:],
               marker=".", c="k", alpha = 0.4)
    # Make axis equal
    ax.axis('equal')
    # Set labels and limits
    ax.set(title='Material Properties',
           xlabel='T1 (ms)',
           ylabel='T2 (ms)',
           xlim=[0, np.max(self.T1)+10],
           ylim=[0, np.max(self.T2)+10])
    # Plot 
    plt.show()












