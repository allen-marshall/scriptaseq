"""Functionality for modeling a Property Binders table in Qt"""
from PyQt5 import QtCore
from PyQt5.Qt import QAbstractTableModel, QStyledItemDelegate, QComboBox

from scriptaseq.internal.gui.undo_commands.prop_binder import SetPropBinderNameCommand, SetPropBinderTypeCommand
from scriptaseq.prop_binder import SUPPORTED_PROP_TYPES


class PropBindersTableModel(QAbstractTableModel):
  """Qt table model for a table of Property Binders"""
  
  # Fixed list of column headers for this table model.
  _COLUMN_HEADERS = ['Name', 'Type', 'Edit Value', 'Edit Binding Script']
  
  # Column index for the property type column.
  _PROP_TYPE_COLUMN_IDX = 1
  
  def __init__(self, project, undo_stack, parent=None, selected_seq_node=None):
    """Constructor
    project -- The ProjectModel representing the project.
    undo_stack -- The Qt undo stack to which actions performed on this model will be pushed.
    parent -- The parent QObject.
    selected_seq_node -- The Sequence Node whose data will be displayed in this model.
    """
    super().__init__(parent)
    self.project = project
    self.undo_stack = undo_stack
    self.selected_seq_node = selected_seq_node
  
  def rowCount(self, parent=None):
    if self.selected_seq_node is None or (parent is not None and parent.isValid()):
      return 0
    else:
      return len(self.selected_seq_node.prop_binders)
  
  def columnCount(self, parent=None):
    return 0 if (parent is not None and parent.isValid()) else len(PropBindersTableModel._COLUMN_HEADERS)
  
  def headerData(self, section, orientation, role):
    if role == QtCore.Qt.DisplayRole and orientation == QtCore.Qt.Horizontal \
    and 0 <= section < len(PropBindersTableModel._COLUMN_HEADERS):
      return PropBindersTableModel._COLUMN_HEADERS[section]
    
    # If there is no header at the specified location, return an invalid value.
    return None
  
  def data(self, index, role):
    if index.isValid() and 0 <= index.row() < self.rowCount(None) and 0 <= index.column() < self.columnCount(None):
      binder = self.selected_seq_node.prop_binders[index.row()]
      
      # Display role
      if role == QtCore.Qt.DisplayRole:
        if index.column() == 0:
          return binder.prop_name
        elif index.column() == 1:
          return binder.prop_type.name
        elif index.column() == 2:
          return ''
        elif index.column() == 3:
          return ''
      
      # Edit role
      elif role == QtCore.Qt.EditRole:
        if index.column() == 0:
          return binder.prop_name
        elif index.column() == 1:
          # TODO: This could probably be made more efficient.
          return SUPPORTED_PROP_TYPES.index(binder.prop_type)
    
    # If no data was found, return an invalid value.
    return None
  
  def setData(self, index, value, role):
    if index.isValid() and 0 <= index.row() < self.rowCount(None) and 0 <= index.column() < self.columnCount(None):
      if role == QtCore.Qt.EditRole:
        if index.column() == 0:
          undo_command = SetPropBinderNameCommand(self.project, self.selected_seq_node, value, index.row())
          self.undo_stack.push(undo_command)
          self.dataChanged.emit(index, index, [QtCore.Qt.EditRole, QtCore.Qt.DisplayRole])
          return True
        elif index.column() == 1:
          new_prop_type = SUPPORTED_PROP_TYPES[value]
          undo_command = SetPropBinderTypeCommand(self.project, self.selected_seq_node, new_prop_type, index.row())
          self.undo_stack.push(undo_command)
          self.dataChanged.emit(index, index, [QtCore.Qt.EditRole, QtCore.Qt.DisplayRole])
          return True
    
    # Return false if the change could not be made.
    return False

class PropBindersTableDelegate(QStyledItemDelegate):
  """Qt table delegate for a table of Property Binders"""
  
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
      editor.setSelectedIndex(index.data(QtCore.Qt.EditRole))
    
    # Use default behavior for other cases.
    else:
      return super().setEditorData(editor, index)
  
  def setModelData(self, editor, model, index):
    # For the property type column, use the property type index from the combo box.
    if index.column() == PropBindersTableModel._PROP_TYPE_COLUMN_IDX:
      new_data = editor.currentData
      model.setData(index, new_data, QtCore.Qt.EditRole)
    
    # Use default behavior for other cases.
    else:
      return super().setModelData(editor, model, index)