"""QML types for use in the timeline editor"""

from PyQt5.QtQuick import QQuickItem, QSGGeometry, QSGNode

from scriptaseq.internal.gui.qt_util import make_or_reuse_geom_node, make_or_reuse_geom, make_or_reuse_flat_mat, \
  make_qcolor


class TimelineGrid(QQuickItem):
  """Displays the grid in the timeline editor."""
  
  def __init__(self, seq_node=None):
    """Constructor
    seq_node -- The Sequence Node currently being edited in the timeline editor.
    """
    super().__init__()
    self.seq_node = seq_node
    self.setFlag(QQuickItem.ItemHasContents)
  
  def updatePaintNode(self, old_node, update_data):
    # Make or reuse geometry node.
    node = make_or_reuse_geom_node(old_node)
    node.setFlag(QSGNode.OwnsGeometry)
    node.setFlag(QSGNode.OwnsMaterial)
    
    # Compute grid lines.
    lines = []
    if self.seq_node is not None:
      if self.seq_node.subspace_settings.grid_settings.line_display_settings[0]:
        lines += self._build_h_lines()
      if self.seq_node.subspace_settings.grid_settings.line_display_settings[1]:
        lines += self._build_v_lines()
    
    # Make or reuse geometry object.
    geom = make_or_reuse_geom(old_node, QSGGeometry.defaultAttributes_Point2D(), len(lines) * 2)
    geom.setDrawingMode(QSGGeometry.DrawLines)
    geom.setLineWidth(1)
    
    # Build geometry.
    vertices = geom.vertexDataAsPoint2D()
    for idx, line in enumerate(lines):
      vertices[idx * 2].set(*line[0])
      vertices[idx * 2 + 1].set(*line[1])
    node.setGeometry(geom)
    node.markDirty(QSGNode.DirtyGeometry)
    
    # TODO: Maybe don't hard-code the material.
    mat = make_or_reuse_flat_mat(old_node)
    mat.setColor(make_qcolor(1, 1, 1, 0.5))
    node.setMaterial(mat)
    
    return node
  
  def _build_h_lines(self):
    # TODO
    return [((0, 0), (1000, 1000))]
  
  def _build_v_lines(self):
    # TODO
    return [((0, 1000), (1000, 0))]