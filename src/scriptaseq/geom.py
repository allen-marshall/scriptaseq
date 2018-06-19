"""Geometry-related functionality"""

class LineSeg:
  """Represents a line segment in 2D space.
  A LineSeg is directed, in that one point is designated as the 'start' and the other as the 'end'. It is valid for both
  points to be the same, in which case the segment has zero length."""
  
  def __init__(self, start_x=0, start_y=0, end_x=0, end_y=0):
    """Constructor
    start_x -- Horizontal position of the start point.
    start_y -- Vertical position of the start point.
    end_x -- Horizontal position of the end point.
    end_y -- Vertical position of the end point.
    """
    self.start_x = start_x
    self.start_y = start_y
    self.end_x = end_x
    self.end_y = end_y
  
  def is_in_rect(self, rect):
    """Checks if this line segment is contained in the specified rectangle
    rect -- The query rectangle
    """
    return rect.x <= self.start_x <= rect.x + rect.width and rect.x <= self.end_x <= rect.x + rect.width \
      and rect.y <= self.start_y <= rect.y + rect.height and rect.y <= self.end_y <= rect.y + rect.height
  
  def __eq__(self, other):
    return isinstance(other, self.__class__) \
      and self.start_x == other.start_x \
      and self.start_y == other.start_y \
      and self.end_x == other.end_x \
      and self.end_y == other.end_y

class Rectangle:
  """Represents a rectangle in 2D space."""
  
  def __init__(self, x, y, width, height):
    """Constructor
    x -- Horizontal position of the origin corner.
    y -- Vertical position of the origin corner.
    width -- Width of the rectangle. If negative, the rectangle will be "flipped" horizontally so that width is
      nonnegative.
    height -- Height of the rectangle. If negative, the rectangle will be "flipped" vertically so that height is
      nonnegative.
    """
    x_start = min(x, x + width)
    x_end = max(x, x + width)
    y_start = min(y, y + height)
    y_end = max(y, y + height)
    
    self.x = x_start
    self.y = y_start
    self.width = x_end - x_start
    self.height = y_end - y_start
  
  def __eq__(self, other):
    return isinstance(other, self.__class__) \
      and self.x == other.x \
      and self.y == other.y \
      and self.width == other.width \
      and self.height == other.height
