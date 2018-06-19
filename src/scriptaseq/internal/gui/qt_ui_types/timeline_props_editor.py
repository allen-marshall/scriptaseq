"""Widget class for timeline_props_editor"""
from PyQt5.Qt import pyqtProperty, QWidget, pyqtSignal

from scriptaseq.internal.generated.qt_ui.timeline_props_editor import Ui_TimelinePropsEditor
from scriptaseq.internal.gui.qt_ui_types.rectangle_editor import RectEditor
from scriptaseq.seq_node import SeqNode


class TimelinePropsEditor(QWidget, Ui_TimelinePropsEditor) :
  """Handles interaction with the Timeline Properties editor in the GUI"""
  
  # Emitted when the timeline properties are changed through the GUI.
  props_edited = pyqtSignal()
  
  def __init__(self, parent=None, seq_node=None):
    """Constructor
    seq_node -- The Sequence Node whose timeline properties should be edited.
    """
    QWidget.__init__(self, parent)
    self.setupUi(self)
    
    # Initialize GUI.
    self._bounds_editor = RectEditor(self)
    self._grid_cell_editor = RectEditor(self)
    self.boundsPlaceholder.addWidget(self._bounds_editor)
    self.gridCellPlaceholder.addWidget(self._grid_cell_editor)
    
    self._bounds_editor.rect_edited.connect(self._props_edited)
    self._grid_cell_editor.rect_edited.connect(self._props_edited)
    self.showHCheckBox.stateChanged.connect(self._props_edited)
    self.showVCheckBox.stateChanged.connect(self._props_edited)
    
    self._seq_node = seq_node
    
    self._update_form()
  
  @pyqtProperty(SeqNode)
  def seq_node(self):
    return self._seq_node
  
  @seq_node.setter
  def seq_node(self, seq_node):
    self._seq_node = seq_node
    self._update_form()
  
  def _props_edited(self):
    """Updates the Sequence Node based on GUI changes in child widget(s)."""
    if self._seq_node is not None:
      self._seq_node.subspace.boundary = self._bounds_editor.rect
      self._seq_node.subspace.grid_settings.first_cell = self._grid_cell_editor.rect
      self._seq_node.subspace.grid_settings.snap_settings = (self.snapHCheckBox.isChecked(),
        self.snapVCheckBox.isChecked())
      self._seq_node.subspace.grid_settings.line_display_settings = (self.showHCheckBox.isChecked(),
        self.showVCheckBox.isChecked())
      
      self.props_edited.emit()
  
  def _update_form(self):
    """Updates values in the form to match the current Sequence Node's settings"""
    if self._seq_node is not None:
      self._bounds_editor.rect = self._seq_node.subspace.boundary
      self._grid_cell_editor.rect = self._seq_node.subspace.grid_settings.first_cell
      grid_snap = self._seq_node.subspace.grid_settings.snap_settings
      grid_show = self._seq_node.subspace.grid_settings.line_display_settings
      self.snapHCheckBox.setChecked(grid_snap[0])
      self.snapVCheckBox.setChecked(grid_snap[1])
      self.showHCheckBox.setChecked(grid_show[0])
      self.showVCheckBox.setChecked(grid_show[1])