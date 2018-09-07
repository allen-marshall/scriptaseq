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
  
  # Signal emitted when the active node in the project tree has changed.
  # Arguments:
  # - Reference to the new active project tree node, or None if there is no active project tree node.
  active_node_changed = pyqtSignal(object)
  
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
  
  # Signal emitted when a node has been reparented.
  # Arguments:
  # - Reference to the node that was reparented.
  # - Reference to the new parent to which the node was added.
  # - Reference to the old parent from which the node was removed.
  node_reparented = pyqtSignal(BaseProjectTreeNode, BaseProjectTreeNode, BaseProjectTreeNode)
  
  def __init__(self, root_node, parent=None):
    """Constructor.
    root_node -- Root node of the project tree.
    parent -- Parent QObject.
    """
    super().__init__(parent)
    
    self._root_node = root_node
    self._active_node = None
    
    self._project_tree_qt_model = None
    self._seq_component_tree_qt_model = None
  
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
  
  @property
  def seq_component_tree_qt_model(self):
    """Property containing a reference to the application's SequenceComponentTreeQtModel.
    This reference is needed because the SequenceComponentTreeQtModel has to be notified before certain changes take
    place, and thus Qt signals are not sufficient to keep the SequenceComponentTreeQtModel up to date. It is recommended
    that this property be set immediately once the application's SequenceComponentTreeQtModel has been constructed.
    """
    return self._seq_component_tree_qt_model
  
  @seq_component_tree_qt_model.setter
  def seq_component_tree_qt_model(self, seq_component_tree_qt_model):
    self._seq_component_tree_qt_model = seq_component_tree_qt_model
  
  @property
  def active_node(self):
    """Property containing a reference to the active project tree node.
    A value of None means there is no active project tree node.
    """
    return self._active_node
  
  @active_node.setter
  def active_node(self, active_node):
    # Notify the SequenceComponentTreeQtModel before and after the change.
    with self.seq_component_tree_qt_model.begin_change_active_project_tree_node():
      self._active_node = active_node
    
    # Send out appropriate signals to notify other GUI components.
    self.active_node_changed.emit(active_node)
  
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
    
    # Reset the active node first, if it or one of its ancestors is being deleted.
    if self.active_node is not None and (node is self.active_node or node in self.active_node.ancestors):
      self.active_node = None
    
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
  
  def reparent_node(self, node, new_parent):
    """Performs a reparent operation on a node in the project tree.
    Raises ValueError if the operation cannot be performed.
    node -- Project tree node to reparent.
    new_parent -- New parent for the project tree node.
    """
    # Do nothing if the node already has the specified parent.
    if node.parent is new_parent:
      return
    
    # Check that the operation is valid before notifying the ProjectTreeQtModel.
    if node.parent is None:
      raise ValueError(QCoreApplication.translate('ProjectTreeController', 'Cannot reparent root project tree node.'))
    if new_parent is None:
      raise ValueError(QCoreApplication.translate('ProjectTreeController', 'Cannot make a new root project tree node.'))
    new_parent.verify_can_add_as_child(node)
    
    old_parent = node.parent
    
    # Notify the ProjectTreeQtModel before and after making the change.
    with self.project_tree_qt_model.begin_reparent_node(node, new_parent):
      node.parent = new_parent
    
    # Send out appropriate signals to notify other GUI components.
    self.node_reparented.emit(node, new_parent, old_parent)