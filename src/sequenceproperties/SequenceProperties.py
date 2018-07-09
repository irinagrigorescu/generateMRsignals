import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits import mplot3d
import csv

class SequenceProperties(object):
  """
  sequenceProperties = a python dictionary of N  FA (deg),
                                                 PA (deg),
                                                 TR  (ms),
                                                 TE  (ms)
  """
  def __init__(self, sequenceAttr, plottingFlag=False):
    # Create options for the sequence
    # by mapping the input value to a function
    optionsForSequence = {'sinu'   : self.__setSinusoidalSequenceProperties,
                          'rand'   : self.__setRandomSequenceProperties,
                          'custom'  : self.__setCustomSequenceProperties }

    # Call the appropriate function to create the attributes for this class
    optionsForSequence[sequenceAttr['type']](sequenceAttr)

    # Plot if requested
    if plottingFlag == True:
      self.__plotThemSequenceProperties()


  """
      Read sequence properties from file
  """
  def __setCustomSequenceProperties(self, sequenceAttributes):
    # Set other properties:
    filename = sequenceAttributes['filename'];
    
    # Create empty dictionary
    seq = {};
    
    # Read file
    with open(filename, 'r' ) as theFile:
      reader = csv.DictReader(theFile)
      # Each line
      for line in reader:
        # The keys (header of the file)
        for myKey in line.keys():
          # Append to existing key
          if myKey in seq:
            seq[myKey] = np.append(seq[myKey], line[myKey]);
          # Or create new key with empty list
          else:
            seq[myKey] = [];
            seq[myKey] = np.append(seq[myKey], line[myKey]);

    # Populate attributes
    self.FA = [float(x) for x in seq['FA'].tolist()];
    self.PA = [float(x) for x in seq['PA'].tolist()];
    self.TR = [float(x) for x in seq['TR'].tolist()];
    self.TE = [float(x) for x in seq['TE'].tolist()];
    self.nROPoints = len(seq['TE'].tolist());


  """
      Generate random values
  """
  def __setRandomSequenceProperties(self, sequenceAttributes):
    # Set other properties:
    maxVal=85
    minVal=5
    N = int(sequenceAttributes['N'])
                      
    # Create random arrays
    self.FA = np.random.uniform(minVal, maxVal, N).tolist();
    self.PA = np.zeros(N).tolist();
    self.TR = np.random.uniform(10, 15, N).tolist();
    self.TE = [x / 2 for x in self.TR]
    
    # Set number of readout points
    self.nROPoints = N

  """
      Generate sinusoidal values
  """
  def __setSinusoidalSequenceProperties(self, sequenceAttributes):
    # Set other properties:
    Nrep=200
    maxVal=85
    minVal=5
    N = int(sequenceAttributes['N'])
    
    # Generate sinusoidal values for the FAs and TRs
    FAs = [];
    for i in range(0, int(np.ceil(N/Nrep))):
      FAs = np.append(FAs, np.sin(np.arange(0, Nrep) * np.pi / Nrep) * (np.random.uniform(minVal, maxVal, 1)))
    
    # Populate the arrays
    self.FA = FAs[0:N].tolist();
    self.PA = np.zeros(N).tolist();
    self.TR = [x + 15 for x in np.zeros(N).tolist()];
    self.TE = [x / 2 for x in self.TR];
   
    # Set number of readout points
    self.nROPoints = N


  """
      Plots the material properties
  """
  def __plotThemSequenceProperties(self):
    print("\n~~~SEQUENCE PROPERTIES~~~\n")

    # Create figure
    fig = plt.figure(figsize=(15,10))
    # Add subplot 1 - FAs
    ax1  = fig.add_subplot(221) # row-col-num
    # Plot the sequence properties
    ax1.plot(np.arange(0,self.nROPoints),
                self.FA,
                marker=".", c="k", alpha = 0.4)
    # Set labels and limits
    ax1.set(title='FAs',
            xlabel='#timepoints',
            ylabel='FA(deg)',
            ylim=[0,91])
    
    # Add subplot 2 - PAs
    ax2  = fig.add_subplot(222) # row-col-num
    # Plot the sequence
    ax2.plot(np.arange(0,self.nROPoints),
                self.PA,
                marker=".", c="k", alpha = 0.4)
    # Set labels and limits
    ax2.set(title='PAs',
            xlabel='#timepoints',
            ylabel='PA(deg)',
            ylim=[0,91])
            
    # Add subplot 3 - TRs
    ax3  = fig.add_subplot(223) # row-col-num
    # Plot the sequence
    ax3.plot(np.arange(0,len(self.FA)),
                self.TR,
                marker=".", c="k", alpha = 0.4)
    # Set labels and limits
    ax3.set(title='TRs',
            xlabel='#timepoints',
            ylabel='TR(ms)',
            ylim=[0,20])
    
    # Add subplot 4 - TEs
    ax4  = fig.add_subplot(224) # row-col-num
    # Plot the sequence
    ax4.plot(np.arange(0,self.nROPoints),
                self.TE,
                marker=".", c="k", alpha = 0.4)
    # Set labels and limits
    ax4.set(title='TEs',
            xlabel='#timepoints',
            ylabel='TE(ms)',
            ylim=[0,20])
    # Plot
    plt.show()
    print("\n\n")
