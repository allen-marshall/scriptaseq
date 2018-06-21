"""Undo commands that alter the active Sequence Node's subspace settings"""

import copy

from scriptaseq.internal.gui.undo_commands.id_gen import gen_undo_id
from scriptaseq.internal.gui.undo_commands.project_base import ProjectUndoCommand


class SetBoundaryCommand(ProjectUndoCommand):
  """Undo command for modifying the boundary rectangle of the active Sequence Node's subspace"""
  
  _undo_id = gen_undo_id()
  
  def __init__(self, project_model, new_boundary):
    """Constructor
    project_model -- Project model to which the change will be made.
    new_boundary -- New boundary rectangle for the active Sequence Node.
    """
    super().__init__(project_model)
    
    self._old_boundary = copy.deepcopy(self.active_seq_node.subspace.boundary)
    self._new_boundary = copy.deepcopy(new_boundary)
    
    self.setText('Boundary change ({})'.format(self.active_seq_node.name))
    
    # Keep track of any children that will be removed by the boundary change.
    self._clipped_children = set()
    for name in self.active_seq_node.clipped_child_names(new_boundary):
      self._clipped_children.add(self.active_seq_node.children[name])
  
  def id(self):
    return self.__class__._undo_id
  
  def redo(self):
    for child in self._clipped_children:
      self.project_model.remove_child(self.active_seq_node, child.name)
    self.project_model.set_subspace_boundary(self.active_seq_node, self._new_boundary)
  
  def undo(self):
    self.project_model.set_subspace_boundary(self.active_seq_node, self._old_boundary)
    for child in self._clipped_children:
      self.project_model.add_child(self.active_seq_node, child)
  
  def mergeWith(self, command):
    # Merge consecutive boundary edits to the same Sequence Node.
    should_merge = isinstance(command, self.__class__) and command.active_seq_node is self.active_seq_node
    if should_merge:
      self._new_boundary = command._new_boundary
      self._clipped_children.update(command._clipped_children)
    return should_merge

class SetGridCellCommand(ProjectUndoCommand):
  """Undo command for modifying the grid cell rectangle of the active Sequence Node's subspace"""
  
  _undo_id = gen_undo_id()
  
  def __init__(self, project_model, new_cell):
    """Constructor
    project_model -- Project model to which the change will be made.
    new_cell -- New grid cell rectangle for the active Sequence Node.
    """
    super().__init__(project_model)
    
    self._old_cell = copy.deepcopy(self.active_seq_node.subspace.grid_settings.first_cell)
    self._new_cell = copy.deepcopy(new_cell)
    
    self.setText('Grid cell change ({})'.format(self.active_seq_node.name))
  
  def id(self):
    return self.__class__._undo_id
  
  def redo(self):
    self.project_model.set_grid_cell(self.active_seq_node, self._new_cell)
  
  def undo(self):
    self.project_model.set_grid_cell(self.active_seq_node, self._old_cell)
  
  def mergeWith(self, command):
    # Merge consecutive grid cell edits to the same Sequence Node.
    should_merge = isinstance(command, self.__class__) and command.active_seq_node is self.active_seq_node
    if should_merge:
      self._new_cell = command._new_cell
    return should_merge

class SetGridSnapCommand(ProjectUndoCommand):
  """Undo command for modifying the grid snap settings of the active Sequence Node's subspace"""
  
  _undo_id = gen_undo_id()
  
  def __init__(self, project_model, new_snap):
    """Constructor
    project_model -- Project model to which the change will be made.
    new_snap -- New grid snap settings for the active Sequence Node.
    """
    super().__init__(project_model)
    
    self._old_snap = copy.deepcopy(self.active_seq_node.subspace.grid_settings.snap_settings)
    self._new_snap = copy.deepcopy(new_snap)
    
    self.setText('Grid snap change ({})'.format(self.active_seq_node.name))
  
  def id(self):
    return self.__class__._undo_id
  
  def redo(self):
    self.project_model.set_grid_snap(self.active_seq_node, self._new_snap)
  
  def undo(self):
    self.project_model.set_grid_snap(self.active_seq_node, self._old_snap)
  
  def mergeWith(self, command):
    # Merge consecutive grid snap edits to the same Sequence Node.
    should_merge = isinstance(command, self.__class__) and command.active_seq_node is self.active_seq_node
    if should_merge:
      self._new_snap = command._new_snap
    return should_merge

class SetGridDisplayCommand(ProjectUndoCommand):
  """Undo command for modifying the grid line display settings of the active Sequence Node's subspace"""
  
  _undo_id = gen_undo_id()
  
  def __init__(self, project_model, new_display):
    """Constructor
    project_model -- Project model to which the change will be made.
    new_display -- New grid display settings for the active Sequence Node.
    """
    super().__init__(project_model)
    
    self._old_display = copy.deepcopy(self.active_seq_node.subspace.grid_settings.line_display_settings)
    self._new_display = copy.deepcopy(new_display)
    
    self.setText('Grid line display change ({})'.format(self.active_seq_node.name))
  
  def id(self):
    return self.__class__._undo_id
  
  def redo(self):
    self.project_model.set_grid_display(self.active_seq_node, self._new_display)
  
  def undo(self):
    self.project_model.set_grid_display(self.active_seq_node, self._old_display)
  
  def mergeWith(self, command):
    # Merge consecutive grid display edits to the same Sequence Node.
    should_merge = isinstance(command, self.__class__) and command.active_seq_node is self.active_seq_node
    if should_merge:
      self._new_display = command._new_display
    return should_merge
