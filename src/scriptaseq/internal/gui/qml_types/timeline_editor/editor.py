"""Main QML type for the timeline editor"""

from PyQt5.Qt import QQuickItem, pyqtProperty, QObject

from scriptaseq.geom import Rectangle
from scriptaseq.internal.gui.qml_types.timeline_editor.grid import TimelineGrid
from scriptaseq.internal.gui.qt_util import fit_item_to_region
from scriptaseq.seq_node import SeqNode
from scriptaseq.internal.gui.qml_types.timeline_editor.markers import TimelineMarkers


class TimelineEditor(QQuickItem):
  """Main item for the timeline editor.
  Note: This item may expand to large sizes depending on the Sequence Node being edited, so it should typically be
  placed inside a scroll pane.
  """
  
  def __init__(self, parent=None, seq_node=None, padding=16):
    """Constructor
    parent -- The parent Qt Quick item.
    seq_node -- The Sequence Node currently being edited in the timeline editor.
    padding -- Amount of padding to display around the editing area, in pixels.
    """
    super().__init__(parent)
    
    # Create child references to be initialized later.
    self._grid = None
    self._bg_rect = None
    self._markers = None
    
    self._seq_node = seq_node
    self._padding = padding
  
  def _init_children(self):
    """Initializes child objects, if they have not been initialized.
    This cannot be done in the constructor because the children are not created and attached at that point.
    """
    if self._grid is None:
      self._grid = self.findChild(TimelineGrid, 'grid')
      self._grid.seq_node = self.seq_node
    if self._markers is None:
      self._markers = self.findChild(TimelineMarkers, 'markers')
      self._markers.seq_node = self.seq_node
    if self._bg_rect is None:
      self._bg_rect = self.findChild(QObject, 'bgRect')
  
  @pyqtProperty(int)
  def padding(self):
    """Amount of padding to display around the editing area, in pixels"""
    return self._padding
  
  @padding.setter
  def padding(self, padding):
    self._padding = padding
    self.update()
  
  @pyqtProperty(SeqNode)
  def seq_node(self):
    """The Sequence Node currently being edited"""
    return self._seq_node
  
  @seq_node.setter
  def seq_node(self, seq_node):
    self._seq_node = seq_node
    if self._grid is not None:
      self._grid.seq_node = seq_node
    if self._markers is not None:
      self._markers.seq_node = seq_node
    self.update()
  
  def update(self):
    self._init_children()
    self._update_size()
    super().update()
    self._grid.update()
    self._markers.update()
  
  def _compute_edit_region(self):
    """Computes the edit region, as a rectangle object with dimensions in pixels."""
    if self.seq_node is None:
      return Rectangle(self.padding, self.padding, 0, 0)
    else:
      zoom = self.seq_node.subspace.zoom_settings
      edit_region = self.seq_node.subspace.boundary
      return Rectangle(self.padding, self.padding, zoom[0] * edit_region.width, zoom[1] * edit_region.height)
  
  def _update_size(self):
    """Updates the item's dimensions and child positioning based on current editing region, zoom, etc."""
    edit_region = self._compute_edit_region()
    padded_region = Rectangle(edit_region.x - self.padding, edit_region.y - self.padding,
      edit_region.width + 2 * self.padding, edit_region.height + 2 * self.padding)
    fit_item_to_region(self._grid, edit_region)
    fit_item_to_region(self._markers, edit_region)
    fit_item_to_region(self._bg_rect, edit_region)
    fit_item_to_region(self, padded_region)
