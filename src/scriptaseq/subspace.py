"""Functionality related to management of subspace settings in a Sequence Node"""

from scriptaseq.color import RGBAColor
from scriptaseq.geom import Rectangle
from PyQt5.Qt import QMatrix4x4

# Default zoom settings.
DEFAULT_ZOOM = (32, 32)

class GridSettings:
  """Contains settings related to background grid display and snapping."""
  
  def __init__(self, first_cell=Rectangle(0, 0, 1, 1), snap_settings=(True, True), line_display_settings=(True, True)):
    """Constructor
    first_cell -- A rectangle representing the shape and location of the first cell. Other cells will repeat relative to
      that cell. Basically defines the origin of the grid along with the width and height of each cell.
    snap_settings -- A 2-tuple of booleans indicating whether to snap horizontally and vertically, respectively.
    line_display_settings -- A 2-tuple of booleans indicating whether to display horizontal and vertical lines,
      respectively.
    """
    self.first_cell = first_cell
    self.snap_settings = snap_settings
    self.line_display_settings = line_display_settings

class SpaceMarker:
  """Represents a line marker to be shown at certain locations in a subspace."""
  
  def __init__(self, is_horizontal, marked_value, repeat_dist=None, color=RGBAColor(alpha=0), label=None):
    """Constructor
    is_horizontal -- If true, the marker shows a horizontal line, and marked_value represents a value along the vertical
      axis. Otherwise, the marker shows a vertical line, and marked_value represents a value along the horizontal axis.
    marked_value -- Vertical or horizontal position at which the marker should be shown.
    repeat_dist -- If not None, the marker will be repeated at positions (value + n * repeat_dist) for every integer n.
      May be useful for marking repeating intervals, such as musical octaves.
    color -- RGBAColor indicating the display color for the marker line. Alpha is transparency, and an alpha of zero can
      be used to show no marker line. If alpha is zero and a label is provided, the label will still be displayed.
    label -- Text label to show at the marker's position. May be useful for e.g. labeling notes in a musical scale.
    """
    self.is_horizontal = is_horizontal
    self.marked_value = marked_value
    self.repeat_dist = repeat_dist
    self.color = color
    self.label = label

class SubspaceSettings:
  """Contains the settings needed for displaying a subspace in the timeline editor."""
  
  def __init__(self, boundary, grid_settings, zoom_settings=DEFAULT_ZOOM, markers=[]):
    """Constructor
    boundary -- Rectangle giving the spatial boundaries of the subspace. Child line segments contained in the subspace
      are required to fit inside this rectangle.
    grid_settings -- GridSettings object giving the settings for the background grid when displaying this subspace in
      the timeline editor.
    zoom_settings -- 2-tuple containing horizontal and vertical zoom factors, respectively. Values should be in pixels
      per space unit.
    markers -- Iterable of SpaceMarker objects indicating what markers to show in the subspace.
    """
    self.boundary = boundary
    self.grid_settings = grid_settings
    self.zoom_settings = zoom_settings
    self.markers = list(markers)
  
  def make_zoom_matrix(self):
    """Returns a matrix representing the zoom scaling for converting from space units to pixels."""
    matrix = QMatrix4x4()
    matrix.scale(*self.zoom_settings)
    return matrix
