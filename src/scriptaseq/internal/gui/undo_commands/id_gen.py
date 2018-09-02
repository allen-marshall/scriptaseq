"""Functionality for generating IDs for undo command classes."""
from PyQt5.Qt import QUndoCommand


_next_id = 1
def gen_undo_id():
  """Generates an undo command class ID."""
  global _next_id
  result = _next_id
  _next_id += 1
  return result

class UndoCommandWithClassBasedID(QUndoCommand):
  """Base class for QUndoCommands with IDs based on their classes.
  Subclasses should define a class-level attribute called undo_id indicating the ID number to use for instances of that
  class.
  """
  
  undo_id = gen_undo_id()
  
  def id(self):
    return self.__class__.undo_id