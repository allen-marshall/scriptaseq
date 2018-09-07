"""Contains QUndoCommand subclasses related to high-level operations on the sequence component tree."""

from scriptaseq.internal.gui.undo_commands.id_gen import gen_undo_id, UndoCommandWithClassBasedID
from scriptaseq.named_tree_node import NamedTreeNode
from PyQt5.Qt import QCoreApplication


class BaseSeqComponentTreeUndoCommand(UndoCommandWithClassBasedID):
  """Base class for QUndoCommands related to high-level operations on the sequence component tree."""
  
  undo_id = gen_undo_id()
  
  def __init__(self, seq_component_tree_controller, parent=None):
    """Constructor.
    seq_component_tree_controller -- Reference to the SequenceComponentTreeController in charge of making high-level
      changes to the sequence component tree.
    parent -- Parent QUndoCommand.
    """
    super().__init__(parent)
    self.seq_component_tree_controller = seq_component_tree_controller

class AddSequenceComponentTreeNodeCommand(BaseSeqComponentTreeUndoCommand):
  """QUndoCommand class for adding a new node to a sequence component tree."""
  
  undo_id = gen_undo_id()
  
  def __init__(self, seq_component_tree_controller, project_tree_node, node, parent_node, parent=None):
    """Constructor.
    Raises ValueError if it is determined that the addition operation would fail.
    seq_component_tree_controller -- Reference to the SequenceComponentTreeController in charge of making high-level
      changes to the sequence component tree.
    project_tree_node -- BaseProjectTreeNode that owns the relevant sequence component tree.
    node -- New SequenceComponentNode to add.
    parent_node -- Parent SequenceComponentNode to which the new node will be added.
    parent -- Parent QUndoCommand.
    """    
    super().__init__(seq_component_tree_controller, parent)
    
    if node.parent is not None:
      raise ValueError(
        QCoreApplication.translate('AddSequenceComponentTreeNodeCommand', 'Cannot add a node that already exists in the sequence component tree.'))
    
    self._project_tree_node = project_tree_node
    self._new_node = node
    self._parent_node = parent_node
    
    self.setText(QCoreApplication.translate('AddSequenceComponentTreeNodeCommand', "Create '{}'").format(node.name))
  
  def redo(self):
    self.seq_component_tree_controller.add_node(self._project_tree_node, self._new_node, self._parent_node)
  
  def undo(self):
    self.seq_component_tree_controller.delete_node(self._project_tree_node, self._new_node)

class DeleteSequenceComponentTreeNodeCommand(BaseSeqComponentTreeUndoCommand):
  """QUndoCommand class for deleting a node from a sequence component tree."""
  
  undo_id = gen_undo_id()
  
  def __init__(self, seq_component_tree_controller, project_tree_node, node, parent=None):
    """Constructor.
    Raises ValueError if it is determined that the deletion operation would fail.
    seq_component_tree_controller -- Reference to the SequenceComponentTreeController in charge of making high-level
      changes to the sequence component tree.
    project_tree_node -- BaseProjectTreeNode that owns the relevant sequence component tree.
    node -- SequenceComponentNode to delete.
    parent -- Parent QUndoCommand.
    """    
    super().__init__(seq_component_tree_controller, parent)
    
    if node.parent is None:
      raise ValueError(
        QCoreApplication.translate('DeleteSequenceComponentTreeNodeCommand', 'Cannot delete root node from sequence component tree.'))
    
    self._project_tree_node = project_tree_node
    self._node = node
    self._parent_node = node.parent
    
    self.setText(QCoreApplication.translate('DeleteSequenceComponentTreeNodeCommand', "Delete '{}'").format(node.name))
  
  def redo(self):
    self.seq_component_tree_controller.delete_node(self._project_tree_node, self._node)
  
  def undo(self):
    self.seq_component_tree_controller.add_node(self._project_tree_node, self._node, self._parent_node)

class RenameSequenceComponentTreeNodeCommand(BaseSeqComponentTreeUndoCommand):
  """QUndoCommand class for renaming a node in a sequence component tree."""
  
  undo_id = gen_undo_id()
  
  def __init__(self, seq_component_tree_controller, project_tree_node, node, new_name, parent=None):
    """Constructor.
    Raises ValueError if it is determined that the rename operation would fail.
    seq_component_tree_controller -- Reference to the SequenceComponentTreeController in charge of making high-level
      changes to the sequence component tree.
    project_tree_node -- BaseProjectTreeNode that owns the relevant sequence component tree.
    node -- SequenceComponentNode to rename.
    new_name -- New name for the SequenceComponentNode.
    parent -- Parent QUndoCommand.
    """    
    super().__init__(seq_component_tree_controller, parent)
    
    # Check that the operation is valid.
    if node.parent is not None:
      node.parent.verify_child_name_available(new_name)
    else:
      NamedTreeNode.verify_name_valid(new_name)
    
    self._project_tree_node = project_tree_node
    self._node = node
    self._old_name = node.name
    self._new_name = new_name
    
    self.setText(
      QCoreApplication.translate('RenameSequenceComponentTreeNodeCommand', "Rename '{}' to '{}'").format(self._old_name, new_name))
    self.setObsolete(self._old_name == self._new_name)
  
  def redo(self):
    self.seq_component_tree_controller.rename_node(self._project_tree_node, self._node, self._new_name)
  
  
  def undo(self):
    self.seq_component_tree_controller.rename_node(self._project_tree_node, self._node, self._old_name)

class ReparentSequenceComponentTreeNodeCommand(BaseSeqComponentTreeUndoCommand):
  """QUndoCommand class for reparenting a node in a sequence component tree."""
  
  undo_id = gen_undo_id()
  
  def __init__(self, seq_component_tree_controller, project_tree_node, node, new_parent, parent=None):
    """Constructor.
    Raises ValueError if it is determined that the reparent operation would fail.
    seq_component_tree_controller -- Reference to the SequenceComponentTreeController in charge of making high-level
      changes to the sequence component tree.
    project_tree_node -- BaseProjectTreeNode that owns the relevant sequence component tree.
    node -- SequenceComponentNode to reparent.
    new_parent -- New parent node for the SequenceComponentNode.
    parent -- Parent QUndoCommand.
    """    
    super().__init__(seq_component_tree_controller, parent)
    
    # Check that the operation is valid.
    if node.parent is None:
      raise ValueError(
        QCoreApplication.translate('ReparentSequenceComponentTreeNodeCommand', 'Cannot reparent root sequence component tree node.'))
    if new_parent is None:
      raise ValueError(
        QCoreApplication.translate('ReparentSequenceComponentTreeNodeCommand', 'Cannot make a new root sequence component tree node.'))
    new_parent.verify_can_add_as_child(node)
    
    self._project_tree_node = project_tree_node
    self._node = node
    self._old_parent = node.parent
    self._new_parent = new_parent
    
    self.setText(
      QCoreApplication.translate('ReparentSequenceComponentTreeNodeCommand', "Move '{}' to Parent '{}'").format(self._node.name, self._new_parent.name))
    self.setObsolete(self._old_parent is self._new_parent)
  
  def redo(self):
    self.seq_component_tree_controller.reparent_node(self._project_tree_node, self._node, self._new_parent)
  
  def undo(self):
    self.seq_component_tree_controller.reparent_node(self._project_tree_node, self._node, self._old_parent)