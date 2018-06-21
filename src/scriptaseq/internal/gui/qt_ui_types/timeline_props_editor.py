"""Widget class for timeline_props_editor"""
from PyQt5.Qt import pyqtProperty, QWidget, pyqtSignal, QUndoCommand, QMessageBox

from scriptaseq.internal.generated.qt_ui.timeline_props_editor import Ui_TimelinePropsEditor
from scriptaseq.internal.gui.qt_ui_types.rectangle_editor import RectEditor
from scriptaseq.internal.gui.undo_commands.subspace import SetBoundaryCommand, SetGridCellCommand, SetGridSnapCommand, \
  SetGridDisplayCommand
from scriptaseq.seq_node import SeqNode
from scriptaseq.internal.gui.undo_commands.seq_node import SetActiveNameCommand


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
    
    self.nameLineEdit.editingFinished.connect(self._name_edited)
    self._boundary_editor.rect_edited.connect(self._boundary_edited)
    self._grid_cell_editor.rect_edited.connect(self._grid_cell_edited)
    self.snapHCheckBox.clicked.connect(self._snap_edited)
    self.snapVCheckBox.clicked.connect(self._snap_edited)
    self.showHCheckBox.clicked.connect(self._line_display_edited)
    self.showVCheckBox.clicked.connect(self._line_display_edited)
    
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
      self.nameLineEdit.setText(self.project.active_seq_node.name)
      self._boundary_editor.rect = self.project.active_seq_node.subspace.boundary
      self._grid_cell_editor.rect = self.project.active_seq_node.subspace.grid_settings.first_cell
      grid_snap = self.project.active_seq_node.subspace.grid_settings.snap_settings
      grid_show = self.project.active_seq_node.subspace.grid_settings.line_display_settings
      self.snapHCheckBox.setChecked(grid_snap[0])
      self.snapVCheckBox.setChecked(grid_snap[1])
      self.showHCheckBox.setChecked(grid_show[0])
      self.showVCheckBox.setChecked(grid_show[1])
  
  def _can_apply_edits(self):
    """Checks if this editor has the necessary pointers to apply changes made through the GUI."""
    return self.project is not None
  
  def _name_edited(self):
    """Called when the active node's name is changed in the GUI."""
    if self._can_apply_edits():
      new_name = self.nameLineEdit.property('text')
      
      # Do nothing if the node already has the specified name.
      if self.project.active_seq_node.name == new_name:
        return
      
      # Make sure the parent node doesn't already have a child with the new name.
      parent_node = self.project.active_seq_node.parent
      if parent_node is not None and new_name in parent_node.children \
        and parent_node.children[new_name] is not self.project.active_seq_node:
        self.nameLineEdit.setText(self.project.active_seq_node.name)
        err_dialog = QMessageBox(QMessageBox.Critical, 'Duplicate name',
          "Parent node '{}' already has a child named '{}'".format(parent_node.name, new_name), QMessageBox.Ok, self)
        err_dialog.exec()
      
      else:
        command = SetActiveNameCommand(self.project, new_name)
        self.undo_command_started.emit(command)
  
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
