"""Contains QUndoCommand subclasses related to high-level operations on the project tree."""

from scriptaseq.internal.gui.undo_commands.id_gen import gen_undo_id, UndoCommandWithClassBasedID
from scriptaseq.named_tree_node import NamedTreeNode
from PyQt5.Qt import QCoreApplication


class BaseProjectTreeUndoCommand(UndoCommandWithClassBasedID):
  """Base class for QUndoCommands related to high-level operations on the project tree."""
  
  undo_id = gen_undo_id()
  
  def __init__(self, project_tree_controller, parent=None):
    """Constructor.
    project_tree_controller -- Reference to the ProjectTreeController in charge of making high-level changes to the
      project tree.
    parent -- Parent QUndoCommand.
    """
    super().__init__(parent)
    self.project_tree_controller = project_tree_controller

class AddProjectTreeNodeCommand(BaseProjectTreeUndoCommand):
  """QUndoCommand class for adding a new node to the project tree."""
  
  undo_id = gen_undo_id()
  
  def __init__(self, project_tree_controller, node, parent_node, parent=None):
    """Constructor.
    Raises ValueError if it is determined that the addition operation would fail.
    project_tree_controller -- Reference to the ProjectTreeController in charge of making high-level changes to the
      project tree.
    node -- New ProjectTreeNode to add.
    parent_node -- Parent ProjectTreeNode to which the new node will be added.
    parent -- Parent QUndoCommand.
    """    
    super().__init__(project_tree_controller, parent)
    
    if node.parent is not None:
      raise ValueError(
        QCoreApplication.translate('AddProjectTreeNodeCommand', 'Cannot add a node that already exists in the project tree.'))
    
    self._new_node = node
    self._parent_node = parent_node
    
    self.setText(QCoreApplication.translate('AddProjectTreeNodeCommand', "Create '{}'").format(node.name))
  
  def redo(self):
    self.project_tree_controller.add_node(self._new_node, self._parent_node)
  
  def undo(self):
    self.project_tree_controller.delete_node(self._new_node)

class DeleteProjectTreeNodeCommand(BaseProjectTreeUndoCommand):
  """QUndoCommand class for deleting a node from the project tree."""
  
  undo_id = gen_undo_id()
  
  def __init__(self, project_tree_controller, node, parent=None):
    """Constructor.
    Raises ValueError if it is determined that the deletion operation would fail.
    project_tree_controller -- Reference to the ProjectTreeController in charge of making high-level changes to the
      project tree.
    node -- ProjectTreeNode to delete.
    parent -- Parent QUndoCommand.
    """    
    super().__init__(project_tree_controller, parent)
    
    if node.parent is None:
      raise ValueError(
        QCoreApplication.translate('DeleteProjectTreeNodeCommand', 'Cannot delete root node from project tree.'))
    
    self._node = node
    self._parent_node = node.parent
    
    self.setText(QCoreApplication.translate('DeleteProjectTreeNodeCommand', "Delete '{}'").format(node.name))
  
  def redo(self):
    self.project_tree_controller.delete_node(self._node)
  
  def undo(self):
    self.project_tree_controller.add_node(self._node, self._parent_node)

class RenameProjectTreeNodeCommand(BaseProjectTreeUndoCommand):
  """QUndoCommand class for renaming a node in the project tree."""
  
  undo_id = gen_undo_id()
  
  def __init__(self, project_tree_controller, node, new_name, parent=None):
    """Constructor.
    Raises ValueError if it is determined that the rename operation would fail.
    project_tree_controller -- Reference to the ProjectTreeController in charge of making high-level changes to the
      project tree.
    node -- ProjectTreeNode to rename.
    new_name -- New name for the ProjectTreeNode.
    parent -- Parent QUndoCommand.
    """    
    super().__init__(project_tree_controller, parent)
    
    # Check that the operation is valid.
    if node.parent is not None:
      node.parent.verify_child_name_available(new_name)
    else:
      NamedTreeNode.verify_name_valid(new_name)
    
    self._node = node
    self._old_name = node.name
    self._new_name = new_name
    
    self.setText(
      QCoreApplication.translate('RenameProjectTreeNodeUndoCommand', "Rename '{}' to '{}'").format(self._old_name, new_name))
    self.setObsolete(self._old_name == self._new_name)
  
  def redo(self):
    self.project_tree_controller.rename_node(self._node, self._new_name)
  
  
  def undo(self):
    self.project_tree_controller.rename_node(self._node, self._old_name)