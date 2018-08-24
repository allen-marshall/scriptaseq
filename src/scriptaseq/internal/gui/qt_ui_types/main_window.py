"""Defines the main window class"""

from PyQt5.QtWidgets import QMainWindow, QUndoStack

from scriptaseq.internal.generated.qt_ui.main_window import Ui_MainWindow
from scriptaseq.internal.gui.project_model import ProjectModel
from scriptaseq.seq_node import SeqNode

class MainWindow(QMainWindow, Ui_MainWindow):
  """Main window for a sequencing project"""
  
  def __init__(self, parent=None):
    QMainWindow.__init__(self, parent)
    self.setupUi(self)
    
    # Create default project.
    # TODO: Support opening a project file on startup.
    # TODO: Decide what the default project should look like. For now, we just construct a test project.
    self._project_root = SeqNode('root')
    self._project_model = ProjectModel(self._project_root)
    
    # Set up menu actions and undo stack.
    self._undo_stack = QUndoStack(self)
    self.actionUndo.triggered.connect(self._undo_stack.createUndoAction(self).trigger)
    self.actionRedo.triggered.connect(self._undo_stack.createRedoAction(self).trigger)
    
    self._undo_stack.canRedoChanged.connect(self._set_can_redo)
    self._undo_stack.canUndoChanged.connect(self._set_can_undo)
    self._undo_stack.cleanChanged.connect(self._set_undo_stack_clean)
    
    # Initialize GUI components.
    # TODO
  
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
