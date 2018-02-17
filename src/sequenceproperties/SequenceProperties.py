import numpy as np

class SequenceProperties(object):
  """
  sequenceProperties = a dictionary of N  FA (deg), 
                                          PA (deg), 
                                          TR  (ms), 
                                          TE  (ms) 
  """
  def __init__(self, flagType='bSSFP'):
    self.typeOfSequence = flagType
    self.nROPoints = 0

  