import numpy as np

class SequenceProperties(object):
  """
  sequenceProperties = a dictionary of N  FA (deg), 
                                          PA (deg), 
                                          TR  (ms), 
                                          TE  (ms) 
  """
  def __init__(self, sequenceFlag='bSSFP', plottingFlag=False):
    self.typeOfSequence = sequenceFlag
    self.nROPoints = 0

    self.FA = __generateSinusoidalValues();

    # Plot if requested      
    if plottingFlag == True:
      self.__plotThemMaterials()

  
  # Generate sinusoidal values
  def __generateSinusoidalValues(self, N=1000, Nrep=200, maxVal=85, minVal=5):
    # Create empty array
    FAs = [];
    print FAs
    # Add values to the array
    for i in range(0, np.ceil(N/Nrep)):
      FAs = np.append(FAs, np.sin(np.arange(0, Nrep) * np.pi / Nrep) * (np.random.uniform(minVal, maxVal, 1)))
    
    return FAs


  # Plots the material properties
  def __plotThemSequenceProperties(self):
    # Create figure
    fig = plt.figure()
    # Add subplot
    ax  = fig.add_subplot(111) # row-col-num
    # 3D projection
    #ax = plt.axes(projection='3d')
    # Plot the material properties
    ax.scatter(np.arange(0,len(self.FA)),
               self.FA,
               marker=".", c="k", alpha = 0.4)
    # Make axis equal
    ax.axis('equal')
    # Set labels and limits
    ax.set(title='Material Properties',
           xlabel='#timepoints',
           ylabel='FA(deg)')
    # Plot 
    plt.show()
