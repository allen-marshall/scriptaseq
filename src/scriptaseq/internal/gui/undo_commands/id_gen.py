"""Functionality for generating IDs for undo command classes."""

_next_id = 1
def gen_undo_id():
  """Generates an undo command class ID."""
  global _next_id
  result = _next_id
  _next_id += 1
  return result