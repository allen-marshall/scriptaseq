"""Undo commands that alter certain properties of the active Sequence Node"""

from PyQt5.Qt import QUndoCommand
import copy
from sortedcontainers.sortedset import SortedSet

from scriptaseq.internal.gui.undo_commands.id_gen import gen_undo_id


class RenameNodeCommand(QUndoCommand):
  """Undo command for modifying a Sequence Node's name"""
  
  _undo_id = gen_undo_id()
  
  def __init__(self, node_tree_model, node_path, new_name, parent=None):
    """Constructor
    Raises ValueError if it is determined that the command will fail.
    node_tree_model -- SeqNodeTreeModel that owns the node tree.
    node_path -- Path to the Sequence Node to rename.
    new_name -- New name for the Sequence Node.
    parent -- Parent QUndoCommand.
    """
    super().__init__(parent)
    
    self._node_tree_model = node_tree_model
    
    # Check if the operation can be performed.
    self._node_to_rename = node_tree_model.root_node.follow_name_path(node_path)
    self._old_name = copy.deepcopy(self._node_to_rename.name)
    self._new_name = copy.deepcopy(new_name)
    if self._node_to_rename.parent is None:
      raise ValueError('Cannot rename root node')
    if not self._node_to_rename.can_be_renamed_to(new_name):
      raise ValueError("Name '{}' unavailable.".format(new_name))
    
    self.setObsolete(self._old_name == self._new_name)
    self.setText("Rename '{}' to '{}'".format(self._old_name, self._new_name))
  
  def id(self):
    return self.__class__._undo_id
  
  def redo(self):
    self._node_tree_model.rename_node(self._node_to_rename, self._new_name)
  
  def undo(self):
    self._node_tree_model.rename_node(self._node_to_rename, self._old_name)

class AddNodeCommand(QUndoCommand):
  """Undo command for adding a Sequence Node to the node tree"""
  
  _undo_id = gen_undo_id()
  
  def __init__(self, node_tree_model, parent_node_path, new_node, parent=None):
    """Constructor
    Raises ValueError if it is determined that the command will fail.
    node_tree_model -- SeqNodeTreeModel that owns the node tree.
    parent_node_path -- Path to the parent Sequence Node to which the new node will be attached.
    new_node -- Sequence Node to add to the tree. Must not already have a parent.
    parent -- Parent QUndoCommand.
    """
    super().__init__(parent)
    
    self._node_tree_model = node_tree_model
    
    # Check if the operation can be performed.
    if new_node.parent is not None:
      raise ValueError('Cannot add a node that already has a parent')
    self._parent_node = node_tree_model.root_node.follow_name_path(parent_node_path)
    if new_node.name in self._parent_node.children:
      raise ValueError("Parent node already has a child named '{}'".format(new_node.name))
    self._new_node = new_node
    
    self.setText("Add new node '{}'".format(new_node.name))
  
  def id(self):
    return self.__class__._undo_id
  
  def redo(self):
    self._node_tree_model.add_node(self._parent_node, self._new_node)
  
  def undo(self):
    self._node_tree_model.remove_node(self._new_node)

class RemoveNodeCommand(QUndoCommand):
  """Undo command for removing a Sequence Node from the node tree"""
  
  _undo_id = gen_undo_id()
  
  def __init__(self, node_tree_model, node_path, parent=None):
    """Constructor
    Raises ValueError if it is determined that the command will fail.
    node_tree_model -- SeqNodeTreeModel that owns the node tree.
    node_path -- Path to the Sequence Node to be removed.
    parent -- Parent QUndoCommand.
    """
    super().__init__(parent)
    
    self._node_tree_model = node_tree_model
    
    # Check if the operation can be performed.
    self._node_to_remove = node_tree_model.root_node.follow_name_path(node_path)
    if self._node_to_remove.parent is None:
      raise ValueError('Cannot remove root node')
    self._parent_node = self._node_to_remove.parent
    
    self.setText("Remove node '{}'".format(self._node_to_remove.name))
  
  def id(self):
    return self.__class__._undo_id
  
  def redo(self):
    self._node_tree_model.remove_node(self._node_to_remove)
  
  def undo(self):
    self._node_tree_model.add_node(self._parent_node, self._node_to_remove)

class SetNodeTagsCommand(QUndoCommand):
  """Undo command for setting a Sequence Node's tags."""
  
  _undo_id = gen_undo_id()
  
  def __init__(self, node_props_widget, node, tags, parent=None):
    """Constructor
    node_props_widget -- NodePropsWidget in charge of node tags.
    node -- Sequence Node whose tags are to be changed.
    tags -- Iterable containing the new tags for the Sequence Node.
    parent -- Parent QUndoCommand.
    """
    super().__init__(parent)
    
    self._node_props_widget = node_props_widget
    self._node = node
    self._new_tags = SortedSet(tags)
    self._old_tags = copy.deepcopy(node.tags)
    
    self.setText("Update Tags (Node '{}')".format(node.name))
    self.setObsolete(self._new_tags == self._old_tags)
  
  def id(self):
    return self.__class__._undo_id
  
  def redo(self):
    self._node.tags.clear()
    self._node.tags.update(self._new_tags)
    if self._node_props_widget.selected_node is self._node:
      self._node_props_widget.update_tag_display()
  
  def undo(self):
    self._node.tags.clear()
    self._node.tags.update(self._old_tags)
    if self._node_props_widget.selected_node is self._node:
      self._node_props_widget.update_tag_display()