"""Defines a controller class for making high-level changes to sequence component trees."""

from PyQt5.Qt import QObject, pyqtSignal, QCoreApplication

from scriptaseq.internal.seq_component_tree.component_tree_nodes import SequenceComponentNode
from scriptaseq.named_tree_node import NamedTreeNode


# TODO: Figure out if it is possible to reduce code duplication between SequenceComponentTreeController and
# ProjectTreeController.
class SequenceComponentTreeController(QObject):
  """Controller class for making high-level changes to sequence component trees.
  Note that this class does not internally support undo/redo functionality, so its methods that change project state
  should generally be called only from within subclasses of QUndoCommand.
  """
  
  # Signal emitted when a sequence component node has been added.
  # Arguments:
  # - Reference to the SequenceComponentNode that was added.
  node_added = pyqtSignal(SequenceComponentNode)
  
  # Signal emitted when a sequence component node has been deleted.
  # Arguments:
  # - Reference to the SequenceComponentNode that was deleted.
  # - Reference to the former parent of the node that was deleted.
  node_deleted = pyqtSignal(SequenceComponentNode, SequenceComponentNode)
  
  # Signal emitted when a sequence component node has been renamed.
  # Arguments:
  # - Reference to the SequenceComponentNode that was renamed.
  # - String containing the new name.
  # - String containing the old name.
  node_renamed = pyqtSignal(SequenceComponentNode, str, str)
  
  # Signal emitted when a sequence component node has been reparented.
  # Arguments:
  # - Reference to the SequenceComponentNode that was reparented.
  # - Reference to the new parent to which the node was added.
  # - Reference to the old parent from which the node was removed.
  node_reparented = pyqtSignal(SequenceComponentNode, SequenceComponentNode, SequenceComponentNode)
  
  def __init__(self, parent=None):
    """Constructor.
    parent -- Parent QObject.
    """
    super().__init__(parent)
    
    self._seq_component_tree_qt_model = None
  
  @property
  def seq_component_tree_qt_model(self):
    """Property containing a reference to the application's SeqComponentTreeQtModel.
    This reference is needed because the SeqComponentTreeQtModel has to be notified before certain changes take place,
    and thus Qt signals are not sufficient to keep the SeqComponentTreeQtModel up to date. It is recommended that this
    property be set immediately once the application's SeqComponentTreeQtModel has been constructed.
    """
    return self._seq_component_tree_qt_model
  
  @seq_component_tree_qt_model.setter
  def seq_component_tree_qt_model(self, seq_component_tree_qt_model):
    self._seq_component_tree_qt_model = seq_component_tree_qt_model
  
  def add_node(self, node, parent):
    """Adds a node to a sequence component tree.
    Raises ValueError if the operation cannot be performed.
    node -- New sequence component tree node to add.
    parent -- Parent to which the new node will be added.
    """
    if node.parent is not None or node is node.owning_project_tree_node.root_seq_component_node:
      raise ValueError(
        QCoreApplication.translate('SequenceComponentTreeController', 'Cannot add a node that already exists in the sequence component tree.'))
    if node.owning_project_tree_node is not parent.owning_project_tree_node:
      raise ValueError(
        QCoreApplication.translate('SequenceComponentTreeController', "Cannot mix sequence component nodes from different project tree nodes."))
    
    # Notify the SeqComponentTreeQtModel before and after making the change.
    with self.seq_component_tree_qt_model.begin_add_node(node, parent):
      node.parent = parent
    
    # Send out appropriate signals to notify other GUI components.
    self.node_added.emit(node)
  
  def delete_node(self, node):
    """Deletes a node from a sequence component tree.
    Raises ValueError if the operation cannot be performed.
    node -- Sequence component tree node to delete.
    """
    if node.parent is None:
      raise ValueError(
        QCoreApplication.translate('SequenceComponentTreeController', 'Cannot delete root node from the sequence component tree.'))
    
    parent_node = node.parent
    
    # Notify the SeqComponentTreeQtModel before and after making the change.
    with self.seq_component_tree_qt_model.begin_delete_node(node):
      node.parent = None
    
    # Send out appropriate signals to notify other GUI components.
    self.node_deleted.emit(node, parent_node)
  
  def rename_node(self, node, new_name):
    """Performs a rename operation on a node in a sequence component tree.
    Raises ValueError if the operation cannot be performed.
    node -- Sequence component tree node to rename.
    new_name -- New name for the node.
    """
    # Do nothing if the node already has the specified name.
    if node.name == new_name:
      return
    
    # Check that the name is valid and available before notifying the SeqComponentTreeQtModel.
    if node.parent is not None:
      node.parent.verify_child_name_available(new_name)
    else:
      NamedTreeNode.verify_name_valid(new_name)
    
    old_name = node.name
    
    # Notify the SeqComponentTreeQtModel before and after making the change.
    with self.seq_component_tree_qt_model.begin_rename_node(node, new_name):
      node.name = new_name
    
    # Send out appropriate signals to notify other GUI components.
    self.node_renamed.emit(node, new_name, old_name)
  
  def reparent_node(self, node, new_parent):
    """Performs a reparent operation on a node in a sequence component tree.
    Raises ValueError if the operation cannot be performed.
    node -- Sequence component tree node to reparent.
    new_parent -- New parent for the node.
    """
    # Do nothing if the node already has the specified parent.
    if node.parent is new_parent:
      return
    
    # Check that the operation is valid before notifying the SeqComponentTreeQtModel.
    if node.parent is None:
      raise ValueError(
        QCoreApplication.translate('SequenceComponentTreeController', 'Cannot reparent root sequence component tree node.'))
    if new_parent is None:
      raise ValueError(
        QCoreApplication.translate('SequenceComponentTreeController', 'Cannot make a new root sequence component tree node.'))
    new_parent.verify_can_add_as_child(node)
    
    old_parent = node.parent
    
    # Notify the SeqComponentTreeQtModel before and after making the change.
    with self.seq_component_tree_qt_model.begin_reparent_node(node, new_parent):
      node.parent = new_parent
    
    # Send out appropriate signals to notify other GUI components.
    self.node_reparented.emit(node, new_parent, old_parent)