"""Functionality for modeling a Property Binders table in Qt"""

from PyQt5 import QtCore
from PyQt5.Qt import QAbstractTableModel, QStyledItemDelegate, QComboBox, QModelIndex

from scriptaseq.internal.gui.undo_commands.prop_binder import SetPropBinderNameCommand, SetPropBinderTypeCommand
from scriptaseq.prop_binder import SUPPORTED_PROP_TYPES
from scriptaseq.util.scripts import UserScriptError


# Separator string for displaying binding filters as strings.
BIND_FILTER_SEPARATOR = ','

class PropBindersTableModel(QAbstractTableModel):
  """Qt table model for a table of Property Binders"""
  
  # Fixed list of column headers for this table model.
  _COLUMN_HEADERS = ['Name', 'Type', 'Filter', 'Value']
  
  # Column index for the property name column.
  _PROP_NAME_COLUMN_IDX = 0
  
  # Column index for the property type column.
  _PROP_TYPE_COLUMN_IDX = 1
  
  # Column index for the binding filter column.
  _BIND_FILTER_COLUMN_IDX = 2
  
  # Column index for the property value column.
  _PROP_VALUE_COLUMN_IDX = 3
  
  def __init__(self, node_tree_sel_model, undo_stack, parent=None):
    """Constructor
    node_tree_sel_model -- QItemSelectionModel from which the selected node will be determined.
    undo_stack -- QUndoStack to receive undo commands generated through the model.
    parent -- Parent QObject for the model.
    """
    super().__init__(parent)
    self._node_tree_sel_model = node_tree_sel_model
    self._undo_stack = undo_stack
    
    # Connect signals to update the table when the selected node changes.
    self._node_tree_sel_model.currentChanged.connect(lambda current, previous: self._update_selected_node())
    
    # Initialize selected node.
    self._update_selected_node()
  
  def _update_selected_node(self):
    """Updates the model's internal reference to the currently selected sequence node."""
    self.beginResetModel()
    self._selected_node = self._node_tree_sel_model.model().seq_node_from_qt_index(
      self._node_tree_sel_model.currentIndex())
    self.endResetModel()
  
  def _emit_data_changed(self, row, column):
    """Emits a data changed signal for the item at the specified row and column."""
    changed_index = self.index(row, column)
    self.dataChanged.emit(changed_index, changed_index)
  
  def set_prop_name(self, node, binder_idx, new_prop_name):
    """Sets the property name for a Property Binder.
    Note: This method generally should only be called from within a QUndoCommand, as the user will not be able to undo
    it otherwise.
    node -- Sequence Node that owns the Property Binder.
    binder_idx -- Index of the binder in the node's Property Binder list.
    new_prop_name -- New property name for the binder.
    """
    node.prop_binders[binder_idx].prop_name = new_prop_name
    
    # If the node we are changing is the selected node, update the GUI table.
    if self._selected_node is node:
      self._emit_data_changed(binder_idx, self.__class__._PROP_NAME_COLUMN_IDX)
  
  def set_prop_type(self, node, binder_idx, new_prop_type):
    """Sets the property type for a Property Binder.
    Note: Changing a Property Binder's property type may also affect its property value, so QUndoCommands that call this
    method should generally store the old property value as well as the old property type.
    Note: This method generally should only be called from within a QUndoCommand, as the user will not be able to undo
    it otherwise.
    node -- Sequence Node that owns the Property Binder.
    binder_idx -- Index of the binder in the node's Property Binder list.
    new_prop_type -- New PropType for the binder.
    """
    node.prop_binders[binder_idx].prop_type = new_prop_type
    
    # If the node we are changing is the selected node, update the GUI table.
    if self._selected_node is node:
      self._emit_data_changed(binder_idx, self.__class__._PROP_TYPE_COLUMN_IDX)
      self._emit_data_changed(binder_idx, self.__class__._PROP_VALUE_COLUMN_IDX)
  
  def set_prop_val(self, node, binder_idx, new_prop_val):
    """Sets the property value for a Property Binder.
    Note: This method generally should only be called from within a QUndoCommand, as the user will not be able to undo
    it otherwise.
    node -- Sequence Node that owns the Property Binder.
    binder_idx -- Index of the binder in the node's Property Binder list.
    new_prop_val -- New property value for the binder.
    """
    node.prop_binders[binder_idx].prop_val = new_prop_val
    
    # If the node we are changing is the selected node, update the GUI table.
    if self._selected_node is node:
      self._emit_data_changed(binder_idx, self.__class__._PROP_VALUE_COLUMN_IDX)
  
  def set_bind_filter(self, node, binder_idx, new_filter):
    """Sets the binding filter for a Property Binder.
    Note: This method generally should only be called from within a QUndoCommand, as the user will not be able to undo
    it otherwise.
    node -- Sequence Node that owns the Property Binder.
    binder_idx -- Index of the binder in the node's Property Binder list.
    new_filter -- New binding filter for the binder.
    """
    node.prop_binders[binder_idx].bind_criterion = new_filter
    
    # If the node we are changing is the selected node, update the GUI table.
    if self._selected_node is node:
      self._emit_data_changed(binder_idx, self.__class__._BIND_FILTER_COLUMN_IDX)
  
  def rowCount(self, parent=QModelIndex()):
    if parent.isValid():
      return 0
    
    if self._selected_node is None:
      return 0
    else:
      return len(self._selected_node.prop_binders)
  
  def columnCount(self, parent=QModelIndex()):
    if parent.isValid() or self._selected_node is None:
      return 0
    else:
      return len(self.__class__._COLUMN_HEADERS)
  
  def headerData(self, section, orientation, role):
    if role == QtCore.Qt.DisplayRole and orientation == QtCore.Qt.Horizontal \
    and 0 <= section < len(self.__class__._COLUMN_HEADERS):
      return self.__class__._COLUMN_HEADERS[section]
    
    # If there is no header at the specified location, return an invalid value.
    return None

  def data(self, index, role):
    if index.isValid() and 0 <= index.row() < self.rowCount() and 0 <= index.column() < self.columnCount() \
    and self._selected_node is not None:
      binder = self._selected_node.prop_binders[index.row()]
      
      # Display role
      if role == QtCore.Qt.DisplayRole:
        if index.column() == self.__class__._PROP_NAME_COLUMN_IDX:
          return binder.prop_name
        
        elif index.column() == self.__class__._PROP_TYPE_COLUMN_IDX:
          return binder.prop_type.name
        
        elif index.column() == self.__class__._BIND_FILTER_COLUMN_IDX:
          return BIND_FILTER_SEPARATOR.join(binder.bind_criterion.bind_tags)
        
        elif index.column() == self.__class__._PROP_VALUE_COLUMN_IDX:
          # If the value is scripted, try to run the script and display the generated value. Otherwise, just get the
          # stored value.
          try:
            prop_val = binder.extract_val()
          except UserScriptError:
            return 'Script Error'
          
          return str(prop_val)
      
      # Edit role
      elif role == QtCore.Qt.EditRole:
        if index.column() == self.__class__._PROP_NAME_COLUMN_IDX:
          return binder.prop_name
        
        elif index.column() == self.__class__._PROP_TYPE_COLUMN_IDX:
          # TODO: This could probably be made more efficient.
          return SUPPORTED_PROP_TYPES.index(binder.prop_type)
       
        elif index.column() == self.__class__._BIND_FILTER_COLUMN_IDX:
          return BIND_FILTER_SEPARATOR.join(binder.bind_criterion.bind_tags)
    
    # If no data was found, return an invalid value.
    return None
  
  def setData(self, index, value, role):
    if index.isValid() and 0 <= index.row() < self.rowCount() and 0 <= index.column() < self.columnCount():
      if role == QtCore.Qt.EditRole:
        if index.column() == self.__class__._PROP_NAME_COLUMN_IDX:
          undo_command = SetPropBinderNameCommand(self, self._selected_node, index.row(), value)
          self._undo_stack.push(undo_command)
          return True
        
        elif index.column() == self.__class__._PROP_TYPE_COLUMN_IDX:
          new_prop_type = SUPPORTED_PROP_TYPES[value]
          undo_command = SetPropBinderTypeCommand(self, self._selected_node, index.row(), new_prop_type)
          self._undo_stack.push(undo_command)
          return True
     
    # Return false if the change could not be made.
    return False
  
  def flags(self, index):
    result = QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable
    
    # Support editing in some columns.
    if index.column() in [self.__class__._PROP_NAME_COLUMN_IDX, self.__class__._PROP_TYPE_COLUMN_IDX,
    self.__class__._BIND_FILTER_COLUMN_IDX]:
      result |= QtCore.Qt.ItemIsEditable
    
    return result

class PropBindersTableDelegate(QStyledItemDelegate):
  """Qt table delegate for a table of Property Binders"""
  
  def __init__(self, parent):
    """Constructor
    parent -- Parent QObject for the delegate.
    """
    super().__init__(parent)
  
  def createEditor(self, parent, option, index):
    # For the property type column, use a combo box with the allowed property types.
    if index.column() == PropBindersTableModel._PROP_TYPE_COLUMN_IDX:
      editor = QComboBox(parent)
      for cb_idx, prop_type in enumerate(SUPPORTED_PROP_TYPES):
        editor.addItem(prop_type.name, cb_idx)
      return editor
    
    # Use default editor for other cases.
    return super().createEditor(parent, option, index)
  
  def setEditorData(self, editor, index):
    # For the property type column, set the selected index of the combo box.
    if index.column() == PropBindersTableModel._PROP_TYPE_COLUMN_IDX:
      editor.setProperty('currentIndex', index.data(QtCore.Qt.EditRole))
    
    # Use default behavior for other cases.
    else:
      return super().setEditorData(editor, index)
  
  def setModelData(self, editor, model, index):
    # For the property type column, use the property type index from the combo box.
    if index.column() == PropBindersTableModel._PROP_TYPE_COLUMN_IDX:
      new_data = editor.currentData()
      model.setData(index, new_data, QtCore.Qt.EditRole)
    
    # Use default behavior for other cases.
    else:
      return super().setModelData(editor, model, index)