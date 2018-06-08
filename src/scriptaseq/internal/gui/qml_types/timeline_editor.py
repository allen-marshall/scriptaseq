"""QML types for use in the timeline editor"""

from PyQt5.Qt import QSGGeometryNode, QSGFlatColorMaterial
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
    
    # These will be initialized in the first paint update, and reused after that.
    self.qsg_node = None
    self.qsg_geom = None
    self.qsg_mat = None
  
  def updatePaintNode(self, old_node, update_data):
    # Initialize QSG objects.
    if self.qsg_node is None:
      self.qsg_node = QSGGeometryNode()
      self.qsg_node.setFlag(QSGNode.OwnsGeometry)
      self.qsg_node.setFlag(QSGNode.OwnsMaterial)
    if self.qsg_mat is None:
      # TODO: Maybe don't hard-code the material.
      self.qsg_mat = QSGFlatColorMaterial()
      self.qsg_mat.setColor(make_qcolor(1, 1, 1, 0.5))
      self.qsg_node.setMaterial(self.qsg_mat)
    
    # Compute grid lines.
    # TODO: Should probably skip if the grid settings have not changed.
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
    
    return self.qsg_node
  
  def _build_h_lines(self):
    # TODO
    return [((0, 0), (1000, 1000))]
  
  def _build_v_lines(self):
    # TODO
    return [((0, 1000), (1000, 0))]