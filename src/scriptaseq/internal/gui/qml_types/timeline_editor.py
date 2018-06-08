"""QML types for use in the timeline editor"""

from PyQt5.Qt import QSGGeometryNode, QSGFlatColorMaterial, QSGTransformNode
from PyQt5.QtQuick import QQuickItem, QSGGeometry, QSGNode

from scriptaseq.internal.gui.qt_util import make_qcolor


class TimelineGrid(QQuickItem):
  """Displays the grid in the timeline editor."""
  
  def __init__(self, seq_node=None):
    """Constructor
    seq_node -- The Sequence Node currently being edited in the timeline editor.
    """
    super().__init__()
    self.seq_node = seq_node
    self.setFlag(QQuickItem.ItemHasContents)
    
    # Variables to keep track of previous settings so we don't update unnecessarily.
    self.prev_zoom = None
    self.prev_grid_settings = None
    
    # These will be initialized in the first paint update, and reused after that.
    self.qsg_transform = None
    self.qsg_node = None
    self.qsg_geom = None
    self.qsg_mat = None
  
  def updatePaintNode(self, old_node, update_data):
    # Initialize QSG objects.
    if self.qsg_transform is None:
      self.qsg_transform = QSGTransformNode()
    if self.qsg_node is None:
      self.qsg_node = QSGGeometryNode()
      self.qsg_node.setFlag(QSGNode.OwnsGeometry)
      self.qsg_node.setFlag(QSGNode.OwnsMaterial)
      self.qsg_transform.appendChildNode(self.qsg_node)
    if self.qsg_mat is None:
      # TODO: Maybe don't hard-code the material.
      self.qsg_mat = QSGFlatColorMaterial()
      self.qsg_mat.setColor(make_qcolor(1, 1, 1, 0.5))
      self.qsg_node.setMaterial(self.qsg_mat)
    
    # Compute zoom transform if zoom has changed.
    if self.prev_zoom is None or self.prev_zoom != self.seq_node.subspace.zoom_settings:
      self.qsg_transform.setMatrix(self.seq_node.subspace.make_zoom_matrix())
      self.prev_zoom = self.seq_node.subspace.zoom_settings
    
    # Compute grid lines if grid has changed.
    if self.prev_grid_settings is None or self.prev_grid_settings != self.seq_node.subspace.grid_settings:
      lines = []
      if self.seq_node is not None:
        if self.seq_node.subspace.grid_settings.line_display_settings[0]:
          lines += self._build_h_lines()
        if self.seq_node.subspace.grid_settings.line_display_settings[1]:
          lines += self._build_v_lines()
      
      # Allocate geometry space.
      if self.qsg_geom is None:
        self.qsg_geom = QSGGeometry(QSGGeometry.defaultAttributes_Point2D(), len(lines) * 2)
        self.qsg_geom.setDrawingMode(QSGGeometry.DrawLines)
        # TODO: Maybe don't hard-code the line width.
        self.qsg_geom.setLineWidth(1)
        self.qsg_node.setGeometry(self.qsg_geom)
      else:
        self.qsg_geom.allocate(len(lines) * 2)
      
      # Build geometry.
      vertices = self.qsg_geom.vertexDataAsPoint2D()
      for idx, line in enumerate(lines):
        vertices[idx * 2].set(*line[0])
        vertices[idx * 2 + 1].set(*line[1])
      self.qsg_node.markDirty(QSGNode.DirtyGeometry)
      
      self.prev_grid_settings = self.seq_node.subspace.grid_settings
    
    return self.qsg_transform
  
  # TODO: Try to reduce code duplication between _build_h_lines and _build_v_lines.
  
  def _build_h_lines(self):
    # Find where to start and stop.
    grid_y_start = self.seq_node.subspace.grid_settings.first_cell.y
    bound_y_start = self.seq_node.subspace.boundary.y
    y_delta = self.seq_node.subspace.grid_settings.first_cell.height
    y_start = (grid_y_start - bound_y_start) % y_delta
    y_end = self.seq_node.subspace.boundary.height
    x_start = 0
    x_end = self.seq_node.subspace.boundary.width
    
    # Generate the lines.
    lines = []
    y_curr = y_start
    while y_curr <= y_end:
      lines.append(((x_start, y_curr), (x_end, y_curr)))
      y_curr += y_delta
    
    return lines
  
  def _build_v_lines(self):
    # Find where to start and stop.
    grid_x_start = self.seq_node.subspace.grid_settings.first_cell.x
    bound_x_start = self.seq_node.subspace.boundary.x
    x_delta = self.seq_node.subspace.grid_settings.first_cell.width
    x_start = (grid_x_start - bound_x_start) % x_delta
    x_end = self.seq_node.subspace.boundary.height
    y_start = 0
    y_end = self.seq_node.subspace.boundary.height
    
    # Generate the lines.
    lines = []
    x_curr = x_start
    while x_curr <= x_end:
      lines.append(((x_curr, y_start), (x_curr, y_end)))
      x_curr += x_delta
    
    return lines