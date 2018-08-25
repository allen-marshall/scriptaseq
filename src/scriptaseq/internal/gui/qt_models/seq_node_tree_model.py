"""Functionality for modeling a Sequence Node tree in Qt"""

from PyQt5 import QtCore
from PyQt5.Qt import QAbstractItemModel, QModelIndex, QVariant


class SeqNodeTreeModel(QAbstractItemModel):
  """PyQt model for the Sequence Node tree"""
  
  def __init__(self, root_node, parent=None):
    """Constructor
    root_node -- Root SeqNode for the Sequence Node tree.
    parent -- Parent QObject for the model.
    """
    super().__init__(parent)
    self.root_node = root_node
  
  def rename_node(self, node, name):
    """Renames a Sequence Node.
    Raises ValueError if the node has a sibling that already has the specified name, or if the node is the root node.
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
    if node.parent is not None and name in node.parent.children:
      raise ValueError("Parent node already has a child named '{}'".format(name))
    
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
    """
    if node.parent is None:
      raise ValueError('Cannot remove root node')
    
    parent = node.parent
    parent_index = self.make_qt_index(parent)
    row = node.idx_in_parent()
    self.beginRemoveRows(parent_index, row, row)
    parent.remove_child(node.name)
    self.endRemoveRows()
  
  def make_qt_index(self, node):
    """Creates a QModelIndex pointing to the specified Sequence Node.
    node -- Sequence Node for which a model index is to be made.
    """
    # Handle the root node differently.
    if node.parent is None:
      return self.createIndex(0, 0, node)
    
    else:
      return self.createIndex(node.idx_in_parent(), 0, node)
  
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
          self.rename_node(index.internalPointer(), value)
          return True
        
        # Renaming may fail due to the parent already having a child with the desired name.
        except ValueError:
          # TODO: Maybe put a message in the status bar explaining the reason for the failure.
          return False
    
    return False
  
  def flags(self, index):
    if not index.isValid():
      return QtCore.Qt.NoItemFlags
    
    flags = QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsDropEnabled
    
    # Flags are different for root and non-root nodes.
    if index.parent().isValid():
      flags |= QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsDragEnabled
    
    return flags