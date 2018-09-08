"""Defines a Qt model for visualizing a sequence component tree node's custom properties."""

from PyQt5 import QtCore
from PyQt5.Qt import QAbstractTableModel, QModelIndex, QVariant

from scriptaseq.internal.gui.qt_models.qt_model_notifiers import ResetModelNotifier


class SequenceComponentCustomPropsQtModel(QAbstractTableModel):
  """Qt model class for visualizing a sequence component tree node's custom properties.
  Despite the name, this class is designed to fit most closely into the View role of the MVC pattern.
  """
  
  # Information about the columns in this class.
  _COLUMN_HEADERS = ('Name', 'Value', 'Eval')
  _NAME_COLUMN = 0
  _VALUE_COLUMN = 1
  _EVAL_COLUMN = 2
  
  def __init__(self, undo_stack, seq_component_tree_controller, seq_component_node_controller, parent=None):
    """Constructor.
    undo_stack -- QUndoStack to receive commands generated through user interaction with this Qt model.
    seq_component_tree_controller -- Reference to the SequenceComponentTreeController in charge of high-level changes to
      sequence component trees.
    seq_component_node_controller -- Reference to the SequenceComponentNodeController in charge of making changes to
      individual nodes in sequence component trees.
    parent -- Parent QObject.
    """
    super().__init__(parent)
    
    self._undo_stack = undo_stack
    self._seq_component_tree_controller = seq_component_tree_controller
    self._seq_component_node_controller = seq_component_node_controller
  
  def begin_change_active_seq_component_tree_node(self):
    """Notifies the SequenceComponentCustomPropsQtModel that the active sequence component tree node is about to change.
    Returns a notifier object that implements operations required before and after the change in its __enter__ and
    __exit__ methods, and therefore can be used in a with statement. The actual change should be performed inside the
    with statement; this function does not perform it.
    """
    return ResetModelNotifier(self)
  
  def rowCount(self, parent=QModelIndex()):
    # Don't allow hierarchy since this is a table model.
    if parent.isValid():
      return 0
    
    # No rows if there is no active sequence component tree node.
    if self._seq_component_tree_controller.active_node is None:
      return 0
    
    return len(self._seq_component_tree_controller.active_node.custom_props)
  
  def columnCount(self, parent=QModelIndex()):
    # Don't allow hierarchy since this is a table model.
    if parent.isValid():
      return 0
    
    return len(SequenceComponentCustomPropsQtModel._COLUMN_HEADERS)
  
  def data(self, index, role=QtCore.Qt.DisplayRole):
    if index.isValid() and self._seq_component_tree_controller.active_node is not None:
      if role == QtCore.Qt.DisplayRole:
        prop_entry = self._seq_component_tree_controller.active_node.custom_props.peekitem(index.row())
        if index.column() == SequenceComponentCustomPropsQtModel._NAME_COLUMN:
          return prop_entry[0]
        elif index.column() == SequenceComponentCustomPropsQtModel._VALUE_COLUMN:
          return prop_entry[1].value_str
        elif index.column() == SequenceComponentCustomPropsQtModel._EVAL_COLUMN:
          return prop_entry[1].is_expr
    
    # Return an invalid QVariant if the data could not be found.
    return QVariant()
  
  def headerData(self, section, orientation, role=QtCore.Qt.DisplayRole):
    if orientation == QtCore.Qt.Horizontal:
      if role == QtCore.Qt.DisplayRole:
        return SequenceComponentCustomPropsQtModel._COLUMN_HEADERS[section]
    
    # Return an invalid QVariant if the data could not be found.
    return QVariant()