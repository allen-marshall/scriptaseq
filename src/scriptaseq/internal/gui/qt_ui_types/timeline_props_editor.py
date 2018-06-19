"""Widget class for timeline_props_editor"""
from PyQt5.Qt import pyqtProperty, QWidget, pyqtSignal, QUndoCommand

from scriptaseq.internal.generated.qt_ui.timeline_props_editor import Ui_TimelinePropsEditor
from scriptaseq.internal.gui.qt_ui_types.rectangle_editor import RectEditor
from scriptaseq.internal.gui.undo_commands.subspace import SetBoundaryCommand, SetGridCellCommand, SetGridSnapCommand, \
  SetGridDisplayCommand
from scriptaseq.seq_node import SeqNode


class TimelinePropsEditor(QWidget, Ui_TimelinePropsEditor) :
  """Handles interaction with the Timeline Properties editor in the GUI"""
  
  # Emitted when the editor has generated an undo command that should be added to the undo stack.
  undo_command_started = pyqtSignal(QUndoCommand)
  
  def __init__(self, parent=None):
    """Constructor
    project -- The ProjectModel containing the project to be edited.
    """
    QWidget.__init__(self, parent)
    self.setupUi(self)
    
    # Initialize GUI.
    self._boundary_editor = RectEditor(self)
    self._grid_cell_editor = RectEditor(self)
    self.boundsPlaceholder.addWidget(self._boundary_editor)
    self.gridCellPlaceholder.addWidget(self._grid_cell_editor)
    
    self._boundary_editor.rect_edited.connect(self._boundary_edited)
    self._grid_cell_editor.rect_edited.connect(self._grid_cell_edited)
    self.snapHCheckBox.stateChanged.connect(self._snap_edited)
    self.snapVCheckBox.stateChanged.connect(self._snap_edited)
    self.showHCheckBox.stateChanged.connect(self._line_display_edited)
    self.showVCheckBox.stateChanged.connect(self._line_display_edited)
    
    self._project = None
    
    self.update_form()
  
  @pyqtProperty(SeqNode)
  def project(self):
    """Property representing the project to be edited"""
    return self._project
  
  @project.setter
  def project(self, project):
    # Disconnect from previous project's signals, if any.
    if self._project is not None:
      self._project.timeline_props_display_changed.disconnect(self.update_form)
    self._project = project
    # Connect to project's signals.
    if project is not None:
      project.timeline_props_display_changed.connect(self.update_form)
    self.update_form()
  
  def update_form(self):
    """Updates values in the form to match the active Sequence Node's settings"""
    if self.project is not None:
      self._boundary_editor.rect = self.project.subspace_boundary
      self._grid_cell_editor.rect = self.project.grid_cell
      grid_snap = self.project.grid_snap
      grid_show = self.project.grid_display
      self.snapHCheckBox.setChecked(grid_snap[0])
      self.snapVCheckBox.setChecked(grid_snap[1])
      self.showHCheckBox.setChecked(grid_show[0])
      self.showVCheckBox.setChecked(grid_show[1])
  
  def _can_apply_edits(self):
    """Checks if this editor has the necessary pointers to apply changes made through the GUI."""
    return self.project is not None
  
  def _boundary_edited(self):
    """Called when the timeline boundary is edited in the GUI."""
    if self._can_apply_edits():
      command = SetBoundaryCommand(self.project, self._boundary_editor.rect)
      self.undo_command_started.emit(command)
  
  def _grid_cell_edited(self):
    """Called when the grid cell origin and/or dimensions are edited in the GUI."""
    if self._can_apply_edits():
      command = SetGridCellCommand(self.project, self._grid_cell_editor.rect)
      self.undo_command_started.emit(command)
  
  def _snap_edited(self):
    """Called when the grid snapping settings are edited in the GUI."""
    if self._can_apply_edits():
      command = SetGridSnapCommand(self.project, (self.snapHCheckBox.isChecked(), self.snapVCheckBox.isChecked()))
      self.undo_command_started.emit(command)
  
  def _line_display_edited(self):
    """Called when the grid line display settings are edited in the GUI."""
    if self._can_apply_edits():
      command = SetGridDisplayCommand(self.project, (self.showHCheckBox.isChecked(), self.showVCheckBox.isChecked()))
      self.undo_command_started.emit(command)
