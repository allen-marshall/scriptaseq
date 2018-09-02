"""Defines a controller class for making high-level changes to the project tree."""
from PyQt5.Qt import QObject, pyqtSignal

from scriptaseq.named_tree_node import NamedTreeNode
from scriptaseq.internal.project_tree.project_tree_nodes import BaseProjectTreeNode


class ProjectTreeController(QObject):
  """Controller class for making high-level changes to a project tree.
  Supported changes include adding, deleting, and renaming project tree nodes.
  Note that this class does not internally support undo/redo functionality, so its methods that change project state
  should generally be called only from within subclasses of QUndoCommand.
  """
  
  # Signal emitted when a node is renamed.
  # Arguments:
  # - Reference to the node that was renamed.
  # - String containing the new name.
  # - String containing the old name.
  node_renamed = pyqtSignal(BaseProjectTreeNode, str, str)
  
  def __init__(self, parent=None):
    """Constructor.
    parent -- Parent QObject.
    """
    super().__init__(parent)
    
    self.project_tree_qt_model = None
  
  @property
  def project_tree_qt_model(self):
    """Property containing a reference to the application's ProjectTreeQtModel.
    This reference is needed because the ProjectTreeQtModel has to be notified before certain changes take place, and
    thus Qt signals are not sufficient to keep the ProjectTreeQtModel up to date. It is recommended that this property
    be set immediately once the application's ProjectTreeQtModel has been constructed.
    """
    return self._project_tree_qt_model
  
  @project_tree_qt_model.setter
  def project_tree_qt_model(self, project_tree_qt_model):
    self._project_tree_qt_model = project_tree_qt_model
  
  def rename_node(self, node, new_name):
    """Performs a rename operation on a node in the project tree.
    Raises ValueError if the node cannot be renamed due to invalidity of the new name or existence of a sibling with the
    same name.
    node -- Project tree node to rename.
    new_name -- New name for the project tree node.
    """
    # Do nothing if the node already has the specified name.
    if node.name == new_name:
      return
    
    # Check that the name is valid and available before notifying the ProjectTreeQtModel.
    if node.parent is not None:
      node.parent.verify_child_name_available(new_name)
    else:
      NamedTreeNode.verify_name_valid(new_name)
    
    old_name = node.name
    
    # Notify the ProjectTreeQtModel before and after making the change.
    with self.project_tree_qt_model.begin_rename_node(node, new_name):
      node.name = new_name
    
    # Send out appropriate signals to notify other GUI components.
    self.node_renamed.emit(node, new_name, old_name)