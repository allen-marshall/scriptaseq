"""Undo commands that alter certain properties of the active Sequence Node"""

import copy
from sortedcontainers.sortedset import SortedSet

from scriptaseq.internal.gui.undo_commands.gui_sync_undo_command import GUISyncUndoCommand
from scriptaseq.internal.gui.undo_commands.id_gen import gen_undo_id


class RenameNodeCommand(GUISyncUndoCommand):
  """Undo command for modifying a Sequence Node's name"""
  
  _undo_id = gen_undo_id()
  
  def __init__(self, gui_sync_manager, node, new_name, parent=None):
    """Constructor
    Raises ValueError if it is determined that the command will fail.
    gui_sync_manager -- GUISyncManager in charge of keeping the GUI up to date.
    node -- Sequence Node to rename.
    new_name -- New name for the Sequence Node.
    parent -- Parent QUndoCommand.
    """
    super().__init__(gui_sync_manager, parent)
    
    # Check if the operation can be performed.
    self._node_to_rename = node
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
    self.gui_sync_manager.rename_node(self._node_to_rename, self._new_name)
  
  def undo(self):
    self.gui_sync_manager.rename_node(self._node_to_rename, self._old_name)

class AddNodeCommand(GUISyncUndoCommand):
  """Undo command for adding a Sequence Node to the node tree"""
  
  _undo_id = gen_undo_id()
  
  def __init__(self, gui_sync_manager, parent_node, new_node, parent=None):
    """Constructor
    Raises ValueError if it is determined that the command will fail.
    gui_sync_manager -- GUISyncManager in charge of keeping the GUI up to date.
    parent_node-- Parent Sequence Node to which the new node will be attached.
    new_node -- Sequence Node to add to the tree. Must not already have a parent.
    parent -- Parent QUndoCommand.
    """
    super().__init__(gui_sync_manager, parent)
    
    # Check if the operation can be performed.
    if new_node.parent is not None:
      raise ValueError('Cannot add a node that already has a parent')
    self._parent_node = parent_node
    if new_node.name in self._parent_node.children:
      raise ValueError("Parent node already has a child named '{}'".format(new_node.name))
    self._new_node = new_node
    
    self.setText("Add new node '{}'".format(new_node.name))
  
  def id(self):
    return self.__class__._undo_id
  
  def redo(self):
    self.gui_sync_manager.add_node(self._parent_node, self._new_node)
  
  def undo(self):
    self.gui_sync_manager.remove_node(self._new_node)

class RemoveNodeCommand(GUISyncUndoCommand):
  """Undo command for removing a Sequence Node from the node tree"""
  
  _undo_id = gen_undo_id()
  
  def __init__(self, gui_sync_manager, node, parent=None):
    """Constructor
    Raises ValueError if it is determined that the command will fail.
    gui_sync_manager -- GUISyncManager in charge of keeping the GUI up to date.
    node -- Sequence Node to be removed.
    parent -- Parent QUndoCommand.
    """
    super().__init__(gui_sync_manager, parent)
    
    # Check if the operation can be performed.
    self._node_to_remove = node
    if self._node_to_remove.parent is None:
      raise ValueError('Cannot remove root node')
    self._parent_node = self._node_to_remove.parent
    
    self.setText("Remove node '{}'".format(self._node_to_remove.name))
  
  def id(self):
    return self.__class__._undo_id
  
  def redo(self):
    self.gui_sync_manager.remove_node(self._node_to_remove)
  
  def undo(self):
    self.gui_sync_manager.add_node(self._parent_node, self._node_to_remove)

class SetNodeTagsCommand(GUISyncUndoCommand):
  """Undo command for setting a Sequence Node's tags."""
  
  _undo_id = gen_undo_id()
  
  def __init__(self, gui_sync_manager, node, tags, parent=None):
    """Constructor
    gui_sync_manager -- GUISyncManager in charge of keeping the GUI up to date.
    node -- Sequence Node whose tags are to be changed.
    tags -- Iterable containing the new tags for the Sequence Node.
    parent -- Parent QUndoCommand.
    """
    super().__init__(gui_sync_manager, parent)
    
    self._node = node
    self._new_tags = SortedSet(tags)
    self._old_tags = copy.deepcopy(node.tags)
    
    self.setText("Update Tags (Node '{}')".format(node.name))
    self.setObsolete(self._new_tags == self._old_tags)
  
  def id(self):
    return self.__class__._undo_id
  
  def redo(self):
    self.gui_sync_manager.set_node_tags(self._node, self._new_tags)
  
  def undo(self):
    self.gui_sync_manager.set_node_tags(self._node, self._old_tags)