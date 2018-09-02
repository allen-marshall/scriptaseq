"""Defines a Qt model for visualizing the project tree."""
from PyQt5 import QtCore
from PyQt5.Qt import QAbstractItemModel, QModelIndex, QVariant


class ProjectTreeQtModel(QAbstractItemModel):
  """Qt model class for visualizing the project tree.
  Despite the name, this class is designed to fit most closely into the View role of the MVC pattern.
  """
  
  def __init__(self, root_node, undo_stack, parent=None):
    """Constructor.
    root_node -- Root node of the project tree.
    undo_stack -- QUndoStack to receive commands generated through user interaction with this Qt model.
    parent -- Parent QObject.
    """
    super().__init__(parent)
    
    self._root_node = root_node
    self._undo_stack = undo_stack
  
  def node_to_qt_index(self, node):
    """Creates a QModelIndex pointing to the specified node.
    node -- Project tree node for which a QModelIndex is to be made.
    """
    # We use an invalid index for the root node, since we don't want to show it in the GUI.
    if node.parent is None:
      return QModelIndex()
    
    else:
      return self.createIndex(node.idx_in_parent(), 0, node)
  
  def qt_index_to_node(self, index):
    """Extracts the node referenced by the specified QModelIndex.
    index -- QModelIndex identifying the node to return.
    """
    # We use an invalid index for the root node, since we don't want to show it in the GUI.
    if not index.isValid():
      return self._root_node
    
    else:
      return index.internalPointer()
  
  def index(self, row, column, parent=QModelIndex()):
    if not self.hasIndex(row, column, parent):
      return QModelIndex()
    
    parent_node = self.qt_index_to_node(parent)
    
    # Create an index with a reference to the child node as its internal pointer.
    child_node = parent_node.child_at_idx(row)
    return self.createIndex(row, column, child_node)
  
  def parent(self, index):
    if not index.isValid():
      return QModelIndex()
    
    node = self.qt_index_to_node(index)
    
    # Return an invalid index if the node has no parent.
    if node.parent is None:
      return QModelIndex()
    
    # Otherwise, create an index pointing to the parent node.
    else:
      return self.node_to_qt_index(node.parent)
  
  def rowCount(self, parent):
    parent_node = self.qt_index_to_node(parent)
    return len(parent_node.children)
  
  def columnCount(self, parent):
    return 1
  
  def data(self, index, role):
    if index.isValid():
      
      node = self.qt_index_to_node(index)
    
      if index.column() == 0:
        if role == QtCore.Qt.DisplayRole:
          return node.name
    
    # Return an invalid QVariant if the data could not be found.
    return QVariant()