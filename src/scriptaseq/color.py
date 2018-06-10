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
  
  def __eq__(self, other):
    return isinstance(other, self.__class__) \
      and self.red == other.red \
      and self.green == other.green \
      and self.blue == other.blue \
      and self.alpha == other.alpha