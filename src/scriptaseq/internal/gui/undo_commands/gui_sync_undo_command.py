"""Contains a base class for QUndoCommands that use a GUISyncManager to keep the GUI up to date with their changes"""
from PyQt5.Qt import QUndoCommand


class GUISyncUndoCommand(QUndoCommand):
  """Base class for QUndoCommands that use a GUISyncManager to keep the GUI up to date with their changes"""
  
  def __init__(self, gui_sync_manager, parent=None):
    """Constructor
    gui_sync_manager -- The GUISyncManager to use for keeping the GUI synchronized with changes made by this undo
      command.
    parent -- Parent QUndoCommand.
    """
    super().__init__(parent)
    self.gui_sync_manager = gui_sync_manager