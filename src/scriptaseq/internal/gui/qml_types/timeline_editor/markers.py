"""QML types for displaying markers on a timeline"""
from PyQt5.Qt import QQuickItem, QSGGeometryNode, QSGNode, QSGGeometry, QSGVertexColorMaterial
import copy


class TimelineMarkers(QQuickItem):
  """Displays the timeline markers in the timeline editor"""
  
  def __init__(self, parent=None, seq_node=None):
    """Constructor
    parent -- The parent Qt Quick item.
    seq_node -- The Sequence Node currently being edited in the timeline editor.
    """
    super().__init__(parent)
    self.seq_node = seq_node
    self.setFlag(QQuickItem.ItemHasContents)
    
    # Variables to keep track of previous settings so we don't update unnecessarily.
    self.prev_zoom = None
    self.prev_markers = None
    
    # These will be initialized in the first paint update, and reused after that.
    self.qsg_node = None
    self.qsg_geom = None
    self.qsg_mat = None
  
  def updatePaintNode(self, old_node, update_data):
    # Only update if we have a Sequence Node.
    if self.seq_node is None:
      return old_node
    
    # Initialize QSG objects.
    if self.qsg_node is None:
      self.qsg_node = QSGGeometryNode()
      self.qsg_node.setFlag(QSGNode.OwnsGeometry)
      self.qsg_node.setFlag(QSGNode.OwnsMaterial)
    if self.qsg_mat is None:
      self.qsg_mat = QSGVertexColorMaterial()
      self.qsg_node.setMaterial(self.qsg_mat)
    
    # Update marker lines if zoom or markers have changed.
    if self.prev_zoom != self.seq_node.subspace.zoom_settings or self.prev_markers != self.seq_node.subspace.markers:
      
      # Compute geometry.
      vertices = []
      for marker in self.seq_node.subspace.markers:
        vertices += self._build_marker_vertices(marker)
      
      # Allocate geometry space.
      if self.qsg_geom is None:
        self.qsg_geom = QSGGeometry(QSGGeometry.defaultAttributes_ColoredPoint2D(), len(vertices))
        self.qsg_geom.setDrawingMode(QSGGeometry.DrawLines)
        # TODO: Maybe don't hard-code the line width.
        self.qsg_geom.setLineWidth(4)
        self.qsg_node.setGeometry(self.qsg_geom)
      else:
        self.qsg_geom.allocate(len(vertices))
      
      # Build geometry.
      qsg_vertices = self.qsg_geom.vertexDataAsColoredPoint2D()
      for idx, vertex in enumerate(vertices):
        qsg_vertices[idx].set(*vertex[0:2], *[round(comp * 255) for comp in vertex[2:]])
      self.qsg_node.markDirty(QSGNode.DirtyGeometry)
      
      self.prev_zoom = copy.deepcopy(self.seq_node.subspace.zoom_settings)
      self.prev_markers = copy.deepcopy(self.seq_node.subspace.markers)
    
    return self.qsg_node
  
  def _build_marker_vertices(self, marker):
    # Handle case where only one line needs to be drawn.
    if marker.repeat_dist is None:
      return self._build_marker_line(marker, marker.marked_value)
    
    # Find where to start and stop.
    boundary = self.seq_node.subspace.boundary
    first_value = marker.marked_value % marker.repeat_dist
    stop_value = boundary.height if marker.is_horizontal else boundary.width
    
    # Build the lines.
    result = []
    next_value = first_value
    while next_value <= stop_value:
      result += self._build_marker_line(marker, next_value)
      next_value += marker.repeat_dist
    
    return result
  
  def _build_marker_line(self, marker, value):
    # Do nothing if the value is out of range.
    boundary = self.seq_node.subspace.boundary
    if marker.is_horizontal:
      if not (boundary.y <= value <= boundary.y + boundary.height):
        return []
    else:
      if not (boundary.x <= value <= boundary.x + boundary.width):
        return []
    
    # Compute color_tuple with premultiplied alpha.
    alpha = marker.color.alpha
    color_tuple = (marker.color.red * alpha, marker.color.green * alpha, marker.color.blue * alpha, alpha)
    
    zoom = self.seq_node.subspace.zoom_settings
    if marker.is_horizontal:
      left = 0
      right = boundary.width * zoom[0]
      # Conversion here is a little odd because we are converting from a coordinate system where +y is up to one where
      # +y is down.
      vertical = (boundary.height + boundary.y - value) * zoom[1]
      return [(left, vertical) + color_tuple, (right, vertical) + color_tuple]
    else:
      top = 0
      bottom = boundary.width * zoom[1]
      horizontal = (value - boundary.x) * zoom[0]
      return [(horizontal, top) + color_tuple, (horizontal, bottom) + color_tuple]
