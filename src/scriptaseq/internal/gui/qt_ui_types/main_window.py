"""Defines the main window class"""

from PyQt5.QtWidgets import QMainWindow, QUndoStack

from scriptaseq.internal.generated.qt_ui.main_window import Ui_MainWindow
from scriptaseq.internal.gui.qt_ui_types.node_props_widget import NodePropsWidget
from scriptaseq.internal.gui.qt_ui_types.node_tree_widget import NodeTreeWidget
from scriptaseq.internal.gui.qt_ui_types.prop_val_widget import PropValWidget
from scriptaseq.prop_binder import PropBinder, STRING_PROP_TYPE, PropBindCriterion, SCRIPTED_VAL_PROP_TYPE, \
  SCRIPT_PROP_TYPE
from scriptaseq.seq_node import SeqNode
from scriptaseq.internal.gui.gui_sync_manager import GUISyncManager


class MainWindow(QMainWindow, Ui_MainWindow):
  """Main window for a sequencing project"""
  
  def __init__(self, parent=None):
    QMainWindow.__init__(self, parent)
    self.setupUi(self)
    
    # Create default project.
    # TODO: Support opening a project file on startup.
    # TODO: Decide what the default project should look like. For now, we just construct a test project.
    project_root = SeqNode('root')
    project_root.prop_binders.append(PropBinder('TestProp', SCRIPT_PROP_TYPE,
      bind_criterion=PropBindCriterion(['TopTag'])))
    project_root.tags.add('Root')
    project_root.tags.add('TheRoot')
    child0 = SeqNode('child0')
    child0.add_child(SeqNode('grandchild0'))
    child0.prop_binders.append(PropBinder('Test0', STRING_PROP_TYPE,
      bind_criterion=PropBindCriterion(['TagB', 'TagA'])))
    child0.prop_binders.append(PropBinder('Test1', SCRIPTED_VAL_PROP_TYPE, use_def_val=False,
      prop_val='script = lambda: 5', bind_criterion=PropBindCriterion([])))
    project_root.add_child(child0)
    project_root.add_child(SeqNode('child1'))
    
    # Set up menu actions and undo stack.
    self._undo_stack = QUndoStack(self)
    self.actionUndo.triggered.connect(self._undo_stack.createUndoAction(self).trigger)
    self.actionRedo.triggered.connect(self._undo_stack.createRedoAction(self).trigger)
    
    self._undo_stack.canRedoChanged.connect(self._set_can_redo)
    self._undo_stack.canUndoChanged.connect(self._set_can_undo)
    self._undo_stack.cleanChanged.connect(self._set_undo_stack_clean)
    
    # Initialize GUI components.
    
    # Initialize Node Tree dockable.
    self._node_tree_widget = NodeTreeWidget(self.dockNodeTree)
    self.nodeTreePlaceholder.addWidget(self._node_tree_widget)
    
    # Initialize Node Properties dockable.
    self._node_props_widget = NodePropsWidget(self.dockNodeProps)
    self._node_props_widget.undo_stack = self._undo_stack
    self.nodePropsPlaceholder.addWidget(self._node_props_widget)
    
    # Initialize Property Value Editor dockable.
    self._prop_val_widget = PropValWidget(self.dockPropVal)
    self.propValPlaceholder.addWidget(self._prop_val_widget)
    
    self._gui_sync_manager = GUISyncManager(project_root, self._undo_stack, self._node_tree_widget,
      self._node_props_widget, self._prop_val_widget, self)
  
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
