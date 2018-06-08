"""Color-related functionality"""

class RGBAColor:
  """Represents a color in the RGBA model."""
  
  def __init__(self, red=0, green=0, blue=0, alpha=0):
    """Constructor
    red -- Red component. Should typically be in the interval [0, 1].
    green -- Green component. Should typically be in the interval [0, 1].
    blue -- Blue component. Should typically be in the interval [0, 1].
    alpha -- Alpha component. Should typically be in the interval [0, 1].
    """
    self.red = red
    self.green = green
    self.blue = blue
    self.alpha = alpha