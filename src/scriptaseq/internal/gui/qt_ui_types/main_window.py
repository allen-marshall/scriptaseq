"""Defines the main window class"""

from PyQt5.Qt import QCoreApplication
from PyQt5.QtWidgets import QMainWindow, QUndoStack

from scriptaseq.internal.generated.qt_ui.main_window import Ui_MainWindow
from scriptaseq.internal.gui.qt_models.project_tree_qt_model import ProjectTreeQtModel
from scriptaseq.internal.gui.qt_models.seq_component_custom_props_qt_model import SequenceComponentCustomPropsQtModel
from scriptaseq.internal.gui.qt_models.seq_component_tree_qt_model import SequenceComponentTreeQtModel
from scriptaseq.internal.gui.qt_ui_types.project_tree_widget import ProjectTreeWidget
from scriptaseq.internal.gui.qt_ui_types.seq_component_props_widget import SequenceComponentPropsWidget
from scriptaseq.internal.gui.qt_ui_types.seq_component_tree_widget import SequenceComponentTreeWidget
from scriptaseq.internal.project_change_controllers.project_tree_controller import ProjectTreeController
from scriptaseq.internal.project_change_controllers.seq_component_node_controller import SequenceComponentNodeController
from scriptaseq.internal.project_change_controllers.seq_component_tree_controller import SequenceComponentTreeController
from scriptaseq.internal.project_tree.project_tree_nodes import DirProjectTreeNode, SequenceProjectTreeNode
from scriptaseq.internal.seq_component_tree.component_tree_nodes import SequenceComponentNode, \
  CustomSequenceComponentPropValue
from scriptaseq.internal.seq_component_tree.component_types import NoteSequenceComponentType, \
  AutomationSequenceComponentType, WaveTableSequenceComponentType


class MainWindow(QMainWindow, Ui_MainWindow):
  """Main window for a sequencing project"""
  
  def __init__(self, parent=None):
    """Constructor.
    parent -- Parent QObject.
    """
    QMainWindow.__init__(self, parent)
    self.setupUi(self)
    
    # Set up menu actions and undo stack.
    self._undo_stack = QUndoStack(self)
    self.actionUndo.triggered.connect(self._undo_stack.createUndoAction(self).trigger)
    self.actionRedo.triggered.connect(self._undo_stack.createRedoAction(self).trigger)
    
    self._undo_stack.canRedoChanged.connect(self._set_can_redo)
    self._undo_stack.canUndoChanged.connect(self._set_can_undo)
    self._undo_stack.cleanChanged.connect(self._set_undo_stack_clean)
    
    # TODO: Create default project or load project. For now, a test project is created instead.
    project_tree_root = DirProjectTreeNode('root')
    child_dir_0 = DirProjectTreeNode('childDir0', project_tree_root)
    DirProjectTreeNode('childDir1', project_tree_root)
    grandchild_seq = SequenceProjectTreeNode('grandchildSequence', child_dir_0)
    child_note = SequenceComponentNode('childNote', grandchild_seq, component_type=NoteSequenceComponentType)
    child_note.parent = grandchild_seq.root_seq_component_node
    SequenceComponentNode('childAutomation', grandchild_seq, component_type=AutomationSequenceComponentType).parent = \
      grandchild_seq.root_seq_component_node
    SequenceComponentNode('childWaveTable', grandchild_seq, component_type=WaveTableSequenceComponentType).parent = \
      grandchild_seq.root_seq_component_node
    child_note.custom_props['prop0'] = CustomSequenceComponentPropValue('val0', False)
    child_note.custom_props['prop1'] = CustomSequenceComponentPropValue('[1, 2]', True)
    child_note.custom_props['prop2'] = CustomSequenceComponentPropValue('val2', False)
    
    # Set up project change controllers.
    project_tree_controller = ProjectTreeController(self)
    seq_component_tree_controller = SequenceComponentTreeController(self)
    seq_component_node_controller = SequenceComponentNodeController(self)
    
    # Set up Qt model objects.
    project_tree_qt_model = ProjectTreeQtModel(project_tree_root, self._undo_stack, project_tree_controller, self)
    seq_component_tree_qt_model = SequenceComponentTreeQtModel(self._undo_stack, project_tree_controller,
      seq_component_tree_controller, seq_component_node_controller, self)
    seq_component_custom_props_qt_model = SequenceComponentCustomPropsQtModel(self._undo_stack,
      seq_component_tree_controller, seq_component_node_controller, self)
    
    # Set up GUI.
    project_tree_widget = ProjectTreeWidget(self._undo_stack, project_tree_qt_model, project_tree_controller, self)
    self.projectTreePlaceholder.addWidget(project_tree_widget)
    seq_component_tree_widget = SequenceComponentTreeWidget(self._undo_stack, seq_component_tree_qt_model,
      project_tree_controller, seq_component_tree_controller, seq_component_node_controller, self)
    self.seqComponentTreePlaceholder.addWidget(seq_component_tree_widget)
    seq_component_props_widget = SequenceComponentPropsWidget(self._undo_stack, seq_component_custom_props_qt_model,
      self)
    self.seqComponentPropsPlaceholder.addWidget(seq_component_props_widget)
    
    # Give project change controllers the necessary references to Qt model objects.
    project_tree_controller.project_tree_qt_model = project_tree_qt_model
    project_tree_controller.seq_component_tree_qt_model = seq_component_tree_qt_model
    seq_component_tree_controller.seq_component_tree_qt_model = seq_component_tree_qt_model
    seq_component_tree_controller.seq_component_custom_props_qt_model = seq_component_custom_props_qt_model
  
  def _set_can_redo(self, can_redo):
    """Called when the status of whether we have an action to redo changes.
    can_redo -- Boolean indicating whether we can currently redo.
    """
    self.actionRedo.setEnabled(can_redo)
    redo_action_text = QCoreApplication.translate('MainWindow', '&Redo')
    self.actionRedo.setText(
      redo_action_text + ' {}'.format(self._undo_stack.redoText()) if can_redo else redo_action_text)
  
  def _set_can_undo(self, can_undo):
    """Called when the status of whether we have an action to undo changes.
    can_undo -- Boolean indicating whether we can currently undo.
    """
    self.actionUndo.setEnabled(can_undo)
    undo_action_text = QCoreApplication.translate('MainWindow', '&Undo')
    self.actionUndo.setText(
      undo_action_text + ' {}'.format(self._undo_stack.undoText()) if can_undo else undo_action_text)
  
  def _set_undo_stack_clean(self, is_clean):
    """Called when the undo stack changes clean status.
    is_clean -- Boolean indicating whether the undo stack is currently in a clean state.
    """
    self.actionSaveProject.setEnabled(not is_clean)
    window_title = QCoreApplication.translate('MainWindow', 'ScriptASeq')
    self.setWindowTitle(window_title if is_clean else window_title + '*')
