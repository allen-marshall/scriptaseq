"""QML types for display of the grid in the timeline editor"""

from PyQt5.Qt import QSGGeometryNode, QSGFlatColorMaterial, QSGTransformNode, pyqtProperty
from PyQt5.QtQuick import QQuickItem, QSGGeometry, QSGNode
import copy

from scriptaseq.internal.gui.project_model import ProjectModel
from scriptaseq.internal.gui.qt_util import make_qcolor


class TimelineGrid(QQuickItem):
  """Displays the grid in the timeline editor."""
  
  def __init__(self, parent=None):
    """Constructor
    parent -- The parent Qt Quick item.
    project -- ProjectModel for the project currently being edited.
    """
    super().__init__(parent)
    self.setFlag(QQuickItem.ItemHasContents)
    
    # Variables to keep track of previous settings so we don't update unnecessarily.
    self.prev_zoom = None
    self.prev_grid_settings = None
    self.prev_boundary = None
    
    # These will be initialized in the first paint update, and reused after that.
    self.qsg_transform = None
    self.qsg_node = None
    self.qsg_geom = None
    self.qsg_mat = None
    
    self._project = None
  
  @pyqtProperty(ProjectModel)
  def project(self):
    """The ProjectModel currently being edited"""
    return self._project
  
  @project.setter
  def project(self, project):
    # Disconnect from previous project's signals, if any.
    if self._project is not None:
      self._project.grid_display_changed.disconnect(self.update)
    self._project = project
    # Connect to project's signals.
    if project is not None:
      project.grid_display_changed.connect(self.update)
  
  def updatePaintNode(self, old_node, update_data):
    # Only update if we have a Sequence Node.
    if self.project.active_seq_node is None:
      return old_node
    
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
    if self.prev_zoom is None or self.prev_zoom != self.project.active_seq_node.subspace.zoom_settings:
      self.qsg_transform.setMatrix(self.project.active_seq_node.subspace.make_zoom_matrix())
      self.prev_zoom = copy.deepcopy(self.project.active_seq_node.subspace.zoom_settings)
    
    # Compute grid lines if grid or boundary has changed.
    if self.prev_grid_settings is None \
      or self.prev_grid_settings != self.project.active_seq_node.subspace.grid_settings \
      or self.prev_boundary is None or self.prev_boundary != self.project.active_seq_node.subspace.boundary:
      lines = []
      if self.project.active_seq_node.subspace.grid_settings.line_display_settings[0]:
        lines += self._build_h_lines()
      if self.project.active_seq_node.subspace.grid_settings.line_display_settings[1]:
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
      self.qsg_node.markDirty(QSGNode.DirtyMaterial)
      
      self.prev_grid_settings = copy.deepcopy(self.project.active_seq_node.subspace.grid_settings)
      self.prev_boundary = copy.deepcopy(self.project.active_seq_node.subspace.boundary)
    
    return self.qsg_transform
  
  # TODO: Try to reduce code duplication between _build_h_lines and _build_v_lines.
  
  def _build_h_lines(self):
    # Find where to start and stop.
    grid_y_start = self.project.active_seq_node.subspace.grid_settings.first_cell.y
    bound_y_start = self.project.active_seq_node.subspace.boundary.y
    bound_height = self.project.active_seq_node.subspace.boundary.height
    y_delta = self.project.active_seq_node.subspace.grid_settings.first_cell.height
    y_start = (grid_y_start - bound_y_start) % y_delta
    y_end = self.project.active_seq_node.subspace.boundary.height
    x_start = 0
    x_end = self.project.active_seq_node.subspace.boundary.width
    
    # Generate the lines.
    lines = []
    y_curr = y_start
    while y_curr <= y_end:
      lines.append(((x_start, bound_height - y_curr), (x_end, bound_height - y_curr)))
      y_curr += y_delta
    
    return lines
  
  def _build_v_lines(self):
    # Find where to start and stop.
    grid_x_start = self.project.active_seq_node.subspace.grid_settings.first_cell.x
    bound_x_start = self.project.active_seq_node.subspace.boundary.x
    x_delta = self.project.active_seq_node.subspace.grid_settings.first_cell.width
    x_start = (grid_x_start - bound_x_start) % x_delta
    x_end = self.project.active_seq_node.subspace.boundary.width
    y_start = 0
    y_end = self.project.active_seq_node.subspace.boundary.height
    
    # Generate the lines.
    lines = []
    x_curr = x_start
    while x_curr <= x_end:
      lines.append(((x_curr, y_start), (x_curr, y_end)))
      x_curr += x_delta
    
    return lines