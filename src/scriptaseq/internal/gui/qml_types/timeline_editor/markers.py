"""QML types for displaying markers on a timeline"""
from PyQt5.Qt import QQuickItem, QSGGeometryNode, QSGNode, QSGGeometry, QSGVertexColorMaterial, QObject
import copy


# Number of pixels away from a marker that the mouse can be while still showing the marker's label.
LABEL_THRESHOLD_DIST_PX = 4

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
    self.setAcceptHoverEvents(True)
    
    # Create child references to be initialized later.
    self._marker_text_h = None
    self._marker_text_v = None
    
    # Variables to keep track of previous settings so we don't update unnecessarily.
    self.prev_zoom = None
    self.prev_markers = None
    
    # These will be initialized in the first paint update, and reused after that.
    self.qsg_node = None
    self.qsg_geom = None
    self.qsg_mat = None
  
  def _init_children(self):
    """Initializes child objects, if they have not been initialized.
    This cannot be done in the constructor because the children are not created and attached at that point.
    """
    if self._marker_text_h is None:
      self._marker_text_h = self.findChild(QObject, 'markerTextH')
    if self._marker_text_v is None:
      self._marker_text_v = self.findChild(QObject, 'markerTextV')
  
  def update(self):
    self._init_children()
    super().update()
  
  def hoverMoveEvent(self, event):
    super().hoverMoveEvent(event)
    if self.seq_node is not None and self._marker_text_h is not None and self._marker_text_v is not None:
      # Find all markers that the mouse is close to.
      zoom = self.seq_node.subspace.zoom_settings
      boundary = self.seq_node.subspace.boundary
      mouse_pos_px = event.pos()
      mouse_pos = (mouse_pos_px.x() / zoom[0], boundary.height + boundary.y - mouse_pos_px.y() / zoom[1])
      threshold_dists = [dist / zoom[idx] for idx, dist in
        enumerate((LABEL_THRESHOLD_DIST_PX, LABEL_THRESHOLD_DIST_PX))]
      def close_enough(marker):
        dist = marker.dist_from(mouse_pos)
        threshold = threshold_dists[1 if marker.is_horizontal else 0]
        return dist <= threshold
      close_markers_h = [marker for marker in self.seq_node.subspace.markers if
        close_enough(marker) and marker.is_horizontal]
      close_markers_v = [marker for marker in self.seq_node.subspace.markers if
        close_enough(marker) and not marker.is_horizontal]
      
      # Update the marker label.
      self._marker_text_h.setProperty('visible', len(close_markers_h) > 0)
      self._marker_text_v.setProperty('visible', len(close_markers_v) > 0)
      if len(close_markers_h) > 0:
        self._marker_text_h.setProperty('text', '; '.join([marker.label for marker in close_markers_h]))
        self._marker_text_h.setY(mouse_pos_px.y())
      if len(close_markers_v) > 0:
        self._marker_text_v.setProperty('text', '; '.join([marker.label for marker in close_markers_v]))
        self._marker_text_v.setX(mouse_pos_px.x())
  
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