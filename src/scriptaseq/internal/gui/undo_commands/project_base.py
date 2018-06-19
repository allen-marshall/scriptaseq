"""Base functionality for undo commands that interact with a ProjectModel"""
from PyQt5.Qt import QUndoCommand

class ProjectUndoCommand(QUndoCommand):
  """Base class for undo commands that interact with a ProjectModel"""
  
  def __init__(self, project_model):
    """Constructor
    project_model -- The ProjectModel associated with this command
    """
    super().__init__()
    self.project_model = project_model
    self.active_seq_node = project_model.active_seq_node