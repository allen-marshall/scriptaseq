"""Functionality for modeling a Sequence Node tree in Qt"""

from PyQt5 import QtCore
from PyQt5.Qt import QAbstractItemModel, QModelIndex, QVariant, QMimeData, QMenu

from scriptaseq.internal.gui.mime_data import SEQ_NODE_PATH_MEDIA_TYPE, MEDIA_STR_ENCODING
from scriptaseq.internal.gui.undo_commands.seq_node import RenameNodeCommand, RemoveNodeCommand, AddNodeCommand
from scriptaseq.seq_node import SeqNode


class SeqNodeTreeModel(QAbstractItemModel):
  """PyQt model for the Sequence Node tree"""
  
  def __init__(self, root_node, undo_stack, parent=None):
    """Constructor
    root_node -- Root SeqNode for the Sequence Node tree.
    undo_stack -- QUndoStack to receive undo commands generated through the model.
    parent -- Parent QObject for the model.
    """
    super().__init__(parent)
    self.root_node = root_node
    self.undo_stack = undo_stack
  
  def rename_node(self, node, name):
    """Renames a Sequence Node.
    Raises ValueError if the specified name is not available for the specified node, or if the node is the root node.
    Note: This method generally should only be called from within a QUndoCommand, as the user will not be able to undo
    it otherwise.
    node -- Sequence Node to rename.
    name -- New name for the node.
    """
    # Don't allow renaming the root node.
    if node.parent is None:
      raise ValueError('Cannot rename root node')
    
    # Do nothing if the node already has the desired name.
    if name == node.name:
      return
    
    # Make sure the specified name is available.
    if not node.can_be_renamed_to(name):
      raise ValueError("Name '{}' unavailable.".format(name))
    
    # Remove the node from its parent, then add it back with the new name. (This approach makes it easier to emit the Qt
    # model signals correctly.)
    parent = node.parent
    self.remove_node(node)
    node.name = name
    self.add_node(parent, node)
  
  def add_node(self, parent, node):
    """Adds a Sequence Node to the node tree.
    Raises ValueError if the node cannot be added because the desired parent already has a different child with the same
    name.
    Note: This method generally should only be called from within a QUndoCommand, as the user will not be able to undo
    it otherwise.
    parent -- Parent node to which the child will be added.
    node -- Child node to add.
    """
    # Do nothing if the node is already a child of the specified parent.
    if node.parent is parent:
      return
    
    # Make sure the child node's name is available in the parent node.
    if node.name in parent.children:
      raise ValueError("Parent node already has a child named '{}'".format(node.name))
    
    parent_index = self.make_qt_index(parent)
    
    # Determine the row into which the child will be inserted.
    row = parent.predict_child_idx(node)
    
    # Perform the insertion.
    self.beginInsertRows(parent_index, row, row)
    parent.add_child(node)
    self.endInsertRows()
  
  def remove_node(self, node):
    """Removes a Sequence Node from the node tree.
    Raises ValueError if the node is the root.
    Note: This method generally should only be called from within a QUndoCommand, as the user will not be able to undo
    it otherwise.
    """
    if node.parent is None:
      raise ValueError('Cannot remove root node')
    
    parent = node.parent
    parent_index = self.make_qt_index(parent)
    row = node.idx_in_parent()
    self.beginRemoveRows(parent_index, row, row)
    parent.remove_child(node.name)
    self.endRemoveRows()
  
  def add_empty_node_undoable(self, parent):
    """Adds an empty child node to the specified parent.
    parent -- Parent node to which a new child will be added.
    Note: This method does not need to be called from within a QUndoCommand, as it creates one internally.
    """
    node_name = parent.suggest_child_name()
    child = SeqNode(node_name)
    self.undo_stack.push(AddNodeCommand(self, parent.name_path, child))
  
  def make_qt_index(self, node):
    """Creates a QModelIndex pointing to the specified Sequence Node.
    node -- Sequence Node for which a model index is to be made.
    """
    # Handle the root node differently.
    if node.parent is None:
      return self.createIndex(0, 0, node)
    
    else:
      return self.createIndex(node.idx_in_parent(), 0, node)
  
  def seq_node_from_qt_index(self, index):
    """Extracts the Sequence Node at the specified Qt model index.
    Returns None if the index does not point to a Sequence Node.
    index -- Qt model index of the Sequence Node to get.
    """
    return index.internalPointer() if index.isValid() else None
  
  def make_context_menu(self, index, parent=None):
    """Creates a context menu for the item at the specified model index.
    Returns None if no context menu should be shown for the specified index.
    index -- QModelIndex pointing to the item for which the context menu should be created.
    parent -- Parent widget for the context menu.
    """
    if not index.isValid():
      return None
    
    node = index.internalPointer()
    
    menu = QMenu(parent)
    
    # Add menu item for creating a new child.
    def new_child_func():
      self.add_empty_node_undoable(node)
    new_child_action = menu.addAction('&New child')
    new_child_action.triggered.connect(new_child_func)
    
    # Add menu item for deleting the node if it is not the root node.
    if node.parent is not None:
      def delete_func():
        self.undo_stack.push(RemoveNodeCommand(self, node.name_path))
      delete_action = menu.addAction('&Delete')
      delete_action.triggered.connect(delete_func)
    
    return menu
  
  def index(self, row, column, parent=QModelIndex()):
    if not self.hasIndex(row, column, parent):
      return QModelIndex()
    
    # Construct an index for the root Sequence Node if the parent index is invalid.
    if not parent.isValid():
      return self.createIndex(row, column, self.root_node)
    
    # Find the Sequence Node referenced by the parent index.
    parent_seq_node = parent.internalPointer()
    
    # Create an index with a reference to the child Sequence Node as its internal pointer.
    child_seq_node = parent_seq_node.child_at_idx(row)
    return self.createIndex(row, column, child_seq_node)
  
  def parent(self, index):
    if not index.isValid():
      return QModelIndex()
    
    # Get the parent of the Sequence Node referenced by the index, if it is not the root node.
    parent_seq_node = index.internalPointer().parent
    if parent_seq_node is None:
      return QModelIndex()
    
    # Determine the row for the parent index.
    row = 0
    if parent_seq_node.parent is not None:
      row = parent_seq_node.idx_in_parent()
    
    return self.createIndex(row, 0, parent_seq_node)
  
  def rowCount(self, parent):
    if parent.column() > 0:
      return 0
    
    # The root "table" should have one row corresponding to the root node.
    if not parent.isValid():
      return 1
    
    parent_seq_node = parent.internalPointer()
    return len(parent_seq_node.children)
  
  def columnCount(self, parent):
    return 1
  
  def data(self, index, role):
    if not index.isValid():
      return QVariant()
    
    seq_node = index.internalPointer()
    
    if index.column() == 0:
      if role == QtCore.Qt.DisplayRole:
        return seq_node.name
      elif role == QtCore.Qt.EditRole:
        return seq_node.name
    
    return QVariant()
  
  def setData(self, index, value, role):
    if index.isValid():
      if role == QtCore.Qt.EditRole:
        
        # Rename the node.
        try:
          self.undo_stack.push(RenameNodeCommand(self, index.internalPointer().name_path, value))
          return True
        
        # Renaming may fail due to the parent already having a child with the desired name.
        except ValueError:
          # TODO: Maybe put a message in the status bar explaining the reason for the failure.
          return False
    
    return False
  
  def mimeTypes(self):
    return [SEQ_NODE_PATH_MEDIA_TYPE]
  
  def mimeData(self, indexes):
    result = QMimeData()
    path_data = indexes[0].internalPointer().name_path_str.encode(MEDIA_STR_ENCODING)
    result.setData(SEQ_NODE_PATH_MEDIA_TYPE, path_data)
    return result
  
  def supportedDropActions(self):
    return QtCore.Qt.IgnoreAction | QtCore.Qt.MoveAction | QtCore.Qt.CopyAction
  
  def dropMimeData(self, data, action, row, column, parent):
    if not self.canDropMimeData(data, action, row, column, parent):
      return False
    
    if action == QtCore.Qt.IgnoreAction:
      return True
    
    if data.hasFormat(SEQ_NODE_PATH_MEDIA_TYPE):
      # Find the node to be moved.
      path_str = data.data(SEQ_NODE_PATH_MEDIA_TYPE).data().decode(MEDIA_STR_ENCODING)
      node_to_move = self.root_node.follow_name_path(path_str)
      
      # Find the new parent node.
      if not parent.isValid():
        return False
      new_parent_node = parent.internalPointer()
      
      # Verify that the move will not create an inheritance loop.
      if new_parent_node is node_to_move or any(map(lambda ancestor: ancestor is node_to_move,
      new_parent_node.ancestors)):
        return False
      
      # Verify that the move represents an actual change.
      if node_to_move.parent is new_parent_node:
        return False
      
      # Verify that the new parent doesn't already have another child with the same name as the child being moved.
      if node_to_move.name in new_parent_node.children:
        return False
      
      # Perform the move.
      self.undo_stack.beginMacro("Move node '{}'".format(node_to_move.name))
      try:
        self.undo_stack.push(RemoveNodeCommand(self, node_to_move.name_path))
        self.undo_stack.push(AddNodeCommand(self, new_parent_node.name_path, node_to_move))
        return True
      finally:
        self.undo_stack.endMacro()
    
    return False
  
  def flags(self, index):
    if not index.isValid():
      return QtCore.Qt.NoItemFlags
    
    flags = QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsDropEnabled
    
    # Flags are different for root and non-root nodes.
    if index.parent().isValid():
      flags |= QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsDragEnabled
    
    return flags