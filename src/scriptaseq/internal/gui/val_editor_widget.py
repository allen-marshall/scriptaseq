"""Defines a base class for widgets to be used as property value editors"""
from PyQt5.Qt import QWidget


class ValEditorWidget(QWidget):
  """Base class for widgets to be used as property value editors"""
  
  def __init__(self, parent=None):
    """Constructor
    parent -- Parent QObject.
    """
    super().__init__(parent)
  
  def update_editor(self, node, binder_idx):
    """Updates the editor contents.
    The default implementation does nothing.
    node -- Sequence Node that owns the currently selected Property Binder. Can be None if no Property Binder is
      selected.
    binder_idx -- Index of the currently selected Property Binder, within the node's Property Binder list. Can be None
      if no Property Binder is selected.
    """
    pass