"""Undo commands that alter certain properties of the active Sequence Node"""

import copy

from scriptaseq.internal.gui.undo_commands.id_gen import gen_undo_id
from scriptaseq.internal.gui.undo_commands.project_base import ProjectUndoCommand

class SetActiveNameCommand(ProjectUndoCommand):
  """Undo command for modifying the active Sequence Node's name"""
  
  _undo_id = gen_undo_id()
  
  def __init__(self, project_model, new_name):
    """Constructor
    project_model -- Project model to which the change will be made.
    new_name -- New name for the active Sequence Node.
    """
    super().__init__(project_model)
    
    self._old_name = copy.deepcopy(project_model.active_seq_node_name)
    self._new_name = copy.deepcopy(new_name)
    
    self.setText('Rename ({})'.format(self._old_name))
  
  def id(self):
    return self.__class__._undo_id
  
  def redo(self):
    self.project_model.active_seq_node_name = self._new_name
  
  def undo(self):
    self.project_model.active_seq_node_name = self._old_name
