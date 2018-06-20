"""Defines the main window class"""

from PyQt5.Qt import QUrl
from PyQt5.QtWidgets import QMainWindow, QUndoStack
import copy

from scriptaseq.color import RGBAColor
from scriptaseq.geom import Rectangle
from scriptaseq.internal.generated.qt_ui.main_window import Ui_MainWindow
from scriptaseq.internal.gui.project_model import ProjectModel
from scriptaseq.internal.gui.qml_types.timeline_editor.editor import TimelineEditor
from scriptaseq.internal.gui.qt_ui_types.timeline_props_editor import TimelinePropsEditor
from scriptaseq.seq_node import SeqNode
from scriptaseq.subspace import GridSettings, SpaceMarker, SubspaceSettings


class MainWindow(QMainWindow, Ui_MainWindow):
  """Main window for a sequencing project"""
  
  def __init__(self, parent=None):
    QMainWindow.__init__(self, parent)
    self.setupUi(self)
    
    # Initialize GUI.
    self.quickTimeline.setSource(QUrl('qml/TimelineDock.qml'))
    self._timeline_editor = self.quickTimeline.rootObject().findChild(TimelineEditor, 'timelineEditor')
    self._timeline_props_editor = TimelinePropsEditor(self)
    self.timelinePropsPlaceholder.addWidget(self._timeline_props_editor)
    
    # Set up menu actions.
    self._undo_stack = QUndoStack(self)
    self.actionUndo.triggered.connect(self._undo_stack.createUndoAction(self).trigger)
    self.actionRedo.triggered.connect(self._undo_stack.createRedoAction(self).trigger)
    
    self._undo_stack.canRedoChanged.connect(self._set_can_redo)
    self._undo_stack.canUndoChanged.connect(self._set_can_undo)
    self._undo_stack.cleanChanged.connect(self._set_undo_stack_clean)
    
    # Create default project.
    # TODO: Support opening a project file on startup.
    # TODO: The default project should be more generic/empty. It is currently nonempty for testing purposes.
    boundary = Rectangle(0, 0, 10, 10)
    grid_settings = GridSettings(Rectangle(0, 0, 1, 1))
    markers = [SpaceMarker(True, 0, 1, RGBAColor(1, 0.25, 0, 0.5), 'unit'),
               SpaceMarker(False, 0, 2, RGBAColor(0, 1, 0, 0.4), 'double unit')]
    subspace = SubspaceSettings(boundary, grid_settings, markers=markers)
    self._project_root = SeqNode('test', subspace)
    child0 = SeqNode('child0', copy.deepcopy(subspace), parent=self._project_root)
    SeqNode('child1', copy.deepcopy(subspace), parent=self._project_root)
    self._project_model = ProjectModel(self._project_root)
    self._project_model.active_seq_node = child0
    
    # Provide project information to the GUI components.
    self._timeline_editor.project = self._project_model
    self._timeline_props_editor.project = self._project_model
    
    # Route undo commands from GUI components to the application undo stack.
    self._timeline_props_editor.undo_command_started.connect(self._push_undo_command)
  
  def _set_can_redo(self, can_redo):
    """Called when the status of whether we have an action to redo changes.
    can_redo -- Boolean indicating whether we can currently redo.
    """
    self.actionRedo.setEnabled(can_redo)
    # TODO: Don't hard-code the command text.
    self.actionRedo.setText('&Redo {}'.format(self._undo_stack.redoText()) if can_redo else '&Redo')
  
  def _set_can_undo(self, can_undo):
    """Called when the status of whether we have an action to undo changes.
    can_undo -- Boolean indicating whether we can currently undo.
    """
    self.actionUndo.setEnabled(can_undo)
    # TODO: Don't hard-code the command text.
    self.actionUndo.setText('&Undo {}'.format(self._undo_stack.undoText()) if can_undo else '&Undo')
  
  def _set_undo_stack_clean(self, is_clean):
    """Called when the undo stack changes clean status.
    is_clean -- Boolean indicating whether the undo stack is currently in a clean state.
    """
    self.actionSaveProject.setEnabled(not is_clean)
    # TODO: Don't hard-code the title, and probably include project filename when possible.
    self.setWindowTitle('ScriptASeq' if is_clean else 'ScriptASeq*')
  
  def _push_undo_command(self, command):
    """Pushes an undo command onto the undo stack
    command -- Undo command to push
    """
    self._undo_stack.push(command)
