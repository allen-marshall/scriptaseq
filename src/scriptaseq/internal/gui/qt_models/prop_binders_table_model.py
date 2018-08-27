"""Functionality for modeling a Property Binders table in Qt"""

from PyQt5 import QtCore
from PyQt5.Qt import QAbstractTableModel, QStyledItemDelegate, QComboBox, QModelIndex, QMenu, QMimeData
import pickle

from scriptaseq.internal.gui.mime_data import PROP_BINDER_PATH_MEDIA_TYPE
from scriptaseq.internal.gui.undo_commands.prop_binder import SetPropBinderNameCommand, SetPropBinderTypeCommand, \
  SetPropBinderFilterCommand, AddPropBinderCommand, RemovePropBinderCommand
from scriptaseq.prop_binder import SUPPORTED_PROP_TYPES, PropBindCriterion, PropBinder, STRING_PROP_TYPE
from scriptaseq.seq_node import PropBinderPath
from scriptaseq.util.scripts import UserScriptError


# Separator string for displaying binding filters as strings.
BIND_FILTER_SEPARATOR = ','

# Initial property name to use when creating a new Property Binder.
NEW_BINDER_PROP_NAME = 'prop'

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
  
  def __init__(self, root_node, undo_stack, gui_sync_manager, parent=None):
    """Constructor
    root_node -- Root Sequence Node.
    node_tree_sel_model -- QItemSelectionModel from which the selected node will be determined.
    undo_stack -- QUndoStack to receive undo commands generated through the model.
    gui_sync_manager -- GUISyncManager in charge of keeping the GUI up to date.
    parent -- Parent QObject for the model.
    """
    super().__init__(parent)
    self._root_node = root_node
    self._undo_stack = undo_stack
    self._gui_sync_manager = gui_sync_manager
    
    self._selected_node = None
  
  def selected_node_changed(self, node):
    """Notifies the model that the selected Sequence Node has changed.
    node -- The newly selected Sequence Node.
    """
    self.beginResetModel()
    self._selected_node = node
    self.endResetModel()
  
  def binder_idx_from_qt_index(self, index):
    """Extracts the Property Binder index at the specified Qt model index.
    Returns None if the index does not point to a Property Binder.
    index -- Qt model index of the Property Binder whose index is to be retrieved.
    """
    return index.row() if index.isValid() else None
  
  def _emit_data_changed(self, row, column):
    """Emits a data changed signal for the item at the specified row and column."""
    changed_index = self.index(row, column)
    self.dataChanged.emit(changed_index, changed_index)
  
  def add_prop_binder(self, node, binder_idx, binder):
    """Adds a new Property Binder to a Sequence Node.
    Note: This method generally should only be called from within a QUndoCommand, as the user will not be able to undo
    it otherwise.
    node -- Sequence Node that will own the Property Binder.
    binder_idx -- Desired index of the binder in the node's Property Binder list.
    binder -- New binder to add to the Sequence Node.
    """
    self.beginInsertRows(QModelIndex(), binder_idx, binder_idx)
    try:
      node.prop_binders.insert(binder_idx, binder)
    finally:
      self.endInsertRows()
  
  def remove_prop_binder(self, node, binder_idx):
    """Removes a Property Binder from a Sequence Node.
    Note: This method generally should only be called from within a QUndoCommand, as the user will not be able to undo
    it otherwise.
    node -- Sequence Node that owns the Property Binder.
    binder_idx -- Index of the binder to delete in the node's Property Binder list.
    """
    self.beginRemoveRows(QModelIndex(), binder_idx, binder_idx)
    try:
      del node.prop_binders[binder_idx]
    finally:
      self.endRemoveRows()
  
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
    new_filter -- New PropBindCriterion for the binder.
    """
    node.prop_binders[binder_idx].bind_criterion = new_filter
    
    # If the node we are changing is the selected node, update the GUI table.
    if self._selected_node is node:
      self._emit_data_changed(binder_idx, self.__class__._BIND_FILTER_COLUMN_IDX)
  
  def make_context_menu(self, index, parent=None):
    """Creates a context menu for the item at the specified model index.
    Returns None if no context menu should be shown for the specified index.
    index -- QModelIndex pointing to the item for which the context menu should be created.
    parent -- Parent widget for the context menu.
    """
    
    node = self._selected_node
    
    menu = QMenu(parent)
    
    # Add menu item for creating a new Property Binder.
    new_binder_row = index.row() + 1 if index.isValid() else len(node.prop_binders)
    def new_binder_func():
      binder = PropBinder(NEW_BINDER_PROP_NAME, STRING_PROP_TYPE)
      self._undo_stack.push(AddPropBinderCommand(self._gui_sync_manager, node, new_binder_row, binder))
    new_binder_action = menu.addAction('&New Property Binder')
    new_binder_action.triggered.connect(new_binder_func)
    
    # Add menu item for deleting the Property Binder.
    if index.isValid():
      def delete_func():
        self._undo_stack.push(RemovePropBinderCommand(self._gui_sync_manager, node, index.row()))
      delete_action = menu.addAction('&Delete')
      delete_action.triggered.connect(delete_func)
    
    return menu
  
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
          undo_command = SetPropBinderNameCommand(self._gui_sync_manager, self._selected_node, index.row(), value)
          self._undo_stack.push(undo_command)
          return True
        
        elif index.column() == self.__class__._PROP_TYPE_COLUMN_IDX:
          new_prop_type = SUPPORTED_PROP_TYPES[value]
          undo_command = SetPropBinderTypeCommand(self._gui_sync_manager, self._selected_node, index.row(),
            new_prop_type)
          self._undo_stack.push(undo_command)
          return True
        
        elif index.column() == self.__class__._BIND_FILTER_COLUMN_IDX:
          new_filter = PropBindCriterion(value.split(BIND_FILTER_SEPARATOR))
          undo_command = SetPropBinderFilterCommand(self._gui_sync_manager, self._selected_node, index.row(),
            new_filter)
          self._undo_stack.push(undo_command)
          return True
     
    # Return false if the change could not be made.
    return False
  
  def mimeTypes(self):
    return [PROP_BINDER_PATH_MEDIA_TYPE]
  
  def mimeData(self, indexes):
    result = QMimeData()
    binder_path = PropBinderPath(self._selected_node.name_path_str, indexes[0].row())
    path_data = pickle.dumps(binder_path)
    result.setData(PROP_BINDER_PATH_MEDIA_TYPE, path_data)
    return result
  
  def supportedDropActions(self):
    return QtCore.Qt.IgnoreAction | QtCore.Qt.MoveAction | QtCore.Qt.CopyAction
  
  def dropMimeData(self, data, action, row, column, parent):
    if not self.canDropMimeData(data, action, row, column, parent):
      return False
    
    if action == QtCore.Qt.IgnoreAction:
      return True
    
    if data.hasFormat(PROP_BINDER_PATH_MEDIA_TYPE):
      # Make sure the Property Binder being moved belongs to the currently selected Sequence Node.
      binder_path = pickle.loads(data.data(PROP_BINDER_PATH_MEDIA_TYPE).data())
      if self._selected_node is not self._root_node.follow_name_path(binder_path.node_path):
        return False
      
      old_idx = binder_path.binder_idx
      new_idx = len(self._selected_node.prop_binders) - 1
      if row >= 0:
        new_idx = row
      elif parent.isValid():
        new_idx = parent.row()
      
      # Verify that the move represents an actual change.
      if old_idx == new_idx:
        return True
      
      # Perform the move.
      binder = self._selected_node.prop_binders[old_idx]
      self._undo_stack.beginMacro("Move Property Binder (Node '{}', Prop '{}')".format(self._selected_node.name,
        binder.prop_name))
      try:
        self._undo_stack.push(RemovePropBinderCommand(self._gui_sync_manager, self._selected_node, old_idx))
        self._undo_stack.push(AddPropBinderCommand(self._gui_sync_manager, self._selected_node, new_idx, binder))
        return True
      finally:
        self._undo_stack.endMacro()
    
    return False
  
  def flags(self, index):
    result = QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsDragEnabled \
      | QtCore.Qt.ItemIsDropEnabled
    
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