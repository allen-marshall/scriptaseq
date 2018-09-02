"""Defines a controller class for making high-level changes to the project tree."""
from PyQt5.Qt import QObject, pyqtSignal, QCoreApplication

from scriptaseq.internal.project_tree.project_tree_nodes import BaseProjectTreeNode
from scriptaseq.named_tree_node import NamedTreeNode


class ProjectTreeController(QObject):
  """Controller class for making high-level changes to a project tree.
  Supported changes include adding, deleting, and renaming project tree nodes.
  Note that this class does not internally support undo/redo functionality, so its methods that change project state
  should generally be called only from within subclasses of QUndoCommand.
  """
  
  # Signal emitted when a node has been added.
  # Arguments:
  # - Reference to the node that was added.
  node_added = pyqtSignal(BaseProjectTreeNode)
  
  # Signal emitted when a node has been deleted.
  # Arguments:
  # - Reference to the node that was deleted.
  # - Reference to the former parent of the node that was deleted.
  node_deleted = pyqtSignal(BaseProjectTreeNode, BaseProjectTreeNode)
  
  # Signal emitted when a node has been renamed.
  # Arguments:
  # - Reference to the node that was renamed.
  # - String containing the new name.
  # - String containing the old name.
  node_renamed = pyqtSignal(BaseProjectTreeNode, str, str)
  
  def __init__(self, root_node, parent=None):
    """Constructor.
    parent -- Parent QObject.
    root_node -- Root node of the project tree.
    """
    super().__init__(parent)
    
    self._root_node = root_node
    
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
  
  def add_node(self, node, parent):
    """Adds a node to the project tree.
    Raises ValueError if the operation cannot be performed.
    node -- New project tree node to add.
    parent -- Parent to which the new node will be added.
    """
    if node.parent is not None or node is self._root_node:
      raise ValueError(
        QCoreApplication.translate('ProjectTreeController', 'Cannot add a node that already exists in the project tree.'))
    
    # Notify the ProjectTreeQtModel before and after making the change.
    with self.project_tree_qt_model.begin_add_node(node, parent):
      node.parent = parent
    
    # Send out appropriate signals to notify other GUI components.
    self.node_added.emit(node)
  
  def delete_node(self, node):
    """Deletes a node from the project tree.
    Raises ValueError if the operation cannot be performed.
    node -- Project tree node to delete.
    """
    if node.parent is None:
      raise ValueError(
        QCoreApplication.translate('ProjectTreeController', 'Cannot delete root node from the project tree.'))
    
    parent_node = node.parent
    
    # Notify the ProjectTreeQtModel before and after making the change.
    with self.project_tree_qt_model.begin_delete_node(node):
      node.parent = None
    
    # Send out appropriate signals to notify other GUI components.
    self.node_deleted.emit(node, parent_node)
  
  def rename_node(self, node, new_name):
    """Performs a rename operation on a node in the project tree.
    Raises ValueError if the operation cannot be performed.
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