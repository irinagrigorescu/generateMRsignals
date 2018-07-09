from sequenceproperties.SequenceProperties import SequenceProperties
from materialproperties.MaterialProperties import MaterialProperties
import numpy as np
import time

class Dictionary(object):
  """     A class for creating the MR dictionary of signals 
    for different material properties

    Attributes:
      N = number of readout points (timepoints for each signal)
      M = number of material properties
      materialProperties = a MaterialProperties object
      sequenceProperties = a SequenceProperties object
  """
  
  # Constructor
  def __init__(self, sequenceAttr, materialAttr, type='bssfp'):
    ### Create objects for material properties and sequence properties
    self.materialProperties = MaterialProperties(materialAttr, plottingFlag=True)
    self.sequenceProperties = SequenceProperties(sequenceAttr, plottingFlag=True)

    ### Material Properties
    # Populate attribute for number of material properties
    self.M = self.materialProperties.nMaterialTuples

    ### Sequence Properties
    # Populate attribute for number of readout points
    self.N = self.sequenceProperties.nROPoints

    ### Dictionary
    # Create empty array for the dictionary M x N x 3
    self.dictionaryMRF = np.zeros((self.M, self.N, 3));

    ### Options for different algorithms
    optionsForAlgorithm = {'bssfp' : self.__runBSSFPAlgorithm,
                           'fisp'  : self.__runFISPAlgorithm };

    ### Run algorithm
    optionsForAlgorithm[type]()

  """ 
    Function that does the bSSFP algorithm
  """
  def __runBSSFPAlgorithm(self):

    # Create empty array for M vectors
    Mvec = {};
    Mvec['Mnext'] = np.zeros((3,self.M));
    Mvec['Mnext'][2,:] = 1;
    Mvec['Mro']   = np.zeros((3,self.M));

    # Precompute the RF pulses for all TRs
    RFpulses = self.__do_precompute_RFPulses()

    # Sequence id
    idxSeq = 0;

    # To time it
    start = time.time()

    # Go through every sequence block:
    for TR,TE in zip(self.sequenceProperties.TR, self.sequenceProperties.TE):
      # 1. Create rotation matrices for off-resonance effects:
      offresTE = self.__create_offresonance(TE);
      offresTR = self.__create_offresonance(TR-TE);

      # 2. Create relaxation matrices:
      relaxTE = self.__create_D_and_Dz(TE);
      relaxTR = self.__create_D_and_Dz(TR);

      # 3. Calculate Mnext and Mro for current TR block
      Mvec = self.__do_sequenceBlock(Mvec, RFpulses[idxSeq,:,:], \
                           offresTE, offresTR, relaxTE, relaxTR)
      
      # 4. Store values in the dictionary
      self.dictionaryMRF[:,idxSeq,0] = Mvec['Mro'][0,:];
      self.dictionaryMRF[:,idxSeq,1] = Mvec['Mro'][1,:];
      self.dictionaryMRF[:,idxSeq,2] = Mvec['Mro'][2,:];

      # Increment sequence block
      idxSeq = idxSeq + 1;

      print("Progress {}/{} TR blocks".format(idxSeq, self.N), end="\r")

    end = time.time()
    print("\nSimulation took " + str(end-start) + " seconds.\n")


  """
    Function that calculates the M vectors for one sequence block
  """
  def __do_sequenceBlock(self, Mvectors, RFpulse, offresTE, offresTR, relaxTE, relaxTR):
    # Get values from dictionary
    Mnext = Mvectors['Mnext']

    # 1. Do RF pulse
    Mnext = np.array(np.matrix(RFpulse) * np.matrix(Mnext));

    # 2. Do off-resonance until readout (second Mnext has lines 1 and 2 permuted)
    Mro = offresTE['Roffres1'] * Mnext + \
          offresTE['Roffres2'] * np.stack((Mnext[1,:], Mnext[0,:], Mnext[2,:]), axis=0);

    # 3. Do relaxation until readout
    Mro = relaxTE['D'] * Mro + relaxTE['Dz'];

    # 4. Do off-resoanance from readout to end of TR
    Mnext = offresTR['Roffres1'] * Mro + \
            offresTR['Roffres2'] * np.stack((Mro[1,:], Mro[0,:], Mro[2,:]), axis=0);

    # 5. Do relaxation from readout to end of TR
    Mnext = relaxTR['D'] * Mnext + relaxTR['Dz'];

    # CREATE DICTIONARY TO SEND BACK
    Moutput = {};
    Moutput['Mnext'] = Mnext;
    Moutput['Mro']   = Mro;

    return Moutput;


  """
    Function that precomputes the RF pulses
  """  
  def __do_precompute_RFPulses(self):
    # Create an Nx3x3 matrix that stores all rf pulses
    # Create empty matrix
    RFpulses = np.zeros((self.N, 3, 3));
    i = 0;

    for alpha,phi in zip(self.sequenceProperties.FA, self.sequenceProperties.PA):
      RFpulses[i,:,:] = self.__create_RFPulse((np.pi/180) * alpha, (np.pi/180) * phi)
      i = i + 1;

    return RFpulses  

  """
    Function that calculates one rf pulse
  """
  def __create_RFPulse(self, alpha, phi):
    # Create empty matrix
    RFpulse = np.zeros((3,3));

    # Populate with values
    RFpulse[0,0] =  np.cos(phi)*np.cos(phi) + np.cos(alpha)*np.sin(phi)*np.sin(phi);
    RFpulse[0,1] =  np.cos(phi)*np.sin(phi) - np.cos(alpha)*np.cos(phi)*np.sin(phi);
    RFpulse[0,2] = -np.sin(alpha)*np.sin(phi);
    RFpulse[1,0] =  np.cos(phi)*np.sin(phi) - np.cos(alpha)*np.cos(phi)*np.sin(phi);
    RFpulse[1,1] =  np.cos(alpha)*np.cos(phi)*np.cos(phi) + np.sin(phi)*np.sin(phi);
    RFpulse[1,2] =  np.cos(phi)*np.sin(alpha);
    RFpulse[2,0] =  np.sin(alpha)*np.sin(phi);
    RFpulse[2,1] = -np.cos(phi)*np.sin(alpha);
    RFpulse[2,2] =  np.cos(alpha);

    return RFpulse;

  """
    Function for the fisp algorithm
  """
  def __runFISPAlgorithm(self):
    pass


  """
    Function that creates the off-resonance matrices
  """
  def __create_offresonance(self, t_time):
    # Calculate off-resonance angle
    beta = 2 * np.pi * t_time * self.materialProperties.materialTuples[2]

    # Create off-resonance matrix 1
    Roffres1 = np.ones((3, self.M))
    Roffres1[0,:] = np.cos(beta)
    Roffres1[1,:] = Roffres1[0,:]

    # Create off-resonance matrix 2
    Roffres2 = np.zeros((3, self.M))
    Roffres2[0, :] = -np.sin(-beta)
    Roffres2[1, :] =  np.sin(-beta)

    # Create dictionary for output
    rmatrices = {}
    rmatrices['Roffres1'] = Roffres1;
    rmatrices['Roffres2'] = Roffres2;
    return rmatrices;

  """
    Function that creates the relaxation matrices
  """
  def __create_D_and_Dz(self, t_time):
    # Create E1 and E2
    E1 = np.exp(-t_time / self.materialProperties.materialTuples[0])
    E2 = np.exp(-t_time / self.materialProperties.materialTuples[1])

    # Create D array of 3xM
    D = np.zeros((3, self.M))
    D[0,:] = E2
    D[1,:] = E2
    D[2,:] = E1

    # Create Dz array of 3xM
    Dz = np.zeros((3, self.M))
    Dz[2,:] = 1-E1

    # Create dictionary for output
    dmatrices = {}
    dmatrices['D'] = D;
    dmatrices['Dz'] = Dz;
    return dmatrices;











