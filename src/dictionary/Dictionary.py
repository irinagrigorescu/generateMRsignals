from sequenceproperties.SequenceProperties import SequenceProperties
from materialproperties.MaterialProperties import MaterialProperties

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
  def __init__(self, materialProperties=None, sequenceProperties=None):
    ### Create objects for material properties and sequence properties
    if materialProperties == None:
      self.materialProperties = MaterialProperties(materialsFlag='FISP', plottingFlag=True)
    if sequenceProperties == None:
      self.sequenceProperties = SequenceProperties(sequenceFlag='bSSFP', plottingFlag=True)

    ### Material Properties
    # Populate attribute for number of material properties
    self.M = self.materialProperties.nMaterialTuples

    ### Sequence Properties
    # Populate attribute for number of readout points
    self.N = self.sequenceProperties.nROPoints

    


