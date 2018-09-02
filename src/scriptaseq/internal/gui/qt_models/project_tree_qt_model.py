"""Defines a Qt model for visualizing the project tree."""
from PyQt5 import QtCore
from PyQt5.Qt import QAbstractItemModel, QModelIndex, QVariant

from scriptaseq.internal.gui.undo_commands.project_tree import RenameProjectTreeNodeCommand


class ProjectTreeQtModel(QAbstractItemModel):
  """Qt model class for visualizing the project tree.
  Despite the name, this class is designed to fit most closely into the View role of the MVC pattern.
  """
  
  class _MoveRowNotifier:
    """Class that calls appropriate methods to notify this Qt model's views that a node is being moved.
    The notifier class is suitable for use in a with statement to perform operations before and after the change. The
    notifier itself does not perform the change.
    """
    
    def __init__(self, src_index, dst_parent, dst_row):
      """Constructor.
      qt_model -- ProjectTreeQtModel that owns this notifier.
      src_index -- QModelIndex of the node to be moved.
      dst_parent -- QModelIndex of the parent node to which the node will be moved.
      dst_row -- Numerical index that the node is expected to have within its parent's child ordering after the move.
      """
      self._src_index = src_index
      self._dst_parent = dst_parent
      self._changing_parent = dst_parent != src_index.parent()
      self._dst_row = dst_row
      self._should_notify = True
      
      # If we are moving the root node, the notifier shouldn't do anything, as the ProjectTreeQtModel doesn't display
      # the root node.
      if not self._src_index.isValid():
        self._should_notify = False
      
      # If the source and destination positions are the same, the notifier shouldn't do anything, to avoid getting an
      # error condition from Qt.
      if (not self._changing_parent) and self._dst_row == self._src_index.row():
        self._should_notify = False
    
    def __enter__(self):
      if not self._should_notify:
        return self
      
      # Compute destination row. Note that Qt interprets the arguments to beginMoveRows differently when moving to a
      # higher row index within the same parent, so we treat that as a special case.
      dst_row = self._dst_row
      if (not self._changing_parent) and dst_row >= self._src_index.row():
        dst_row += 1
      
      # Call beginMoveRows, asserting that it doesn't fail.
      assert self._src_index.model().beginMoveRows(self._src_index.parent(), self._src_index.row(),
        self._src_index.row(), self._dst_parent, dst_row)
      
      return self
    
    def __exit__(self, exc_type, exc_value, exc_traceback):
      if not self._should_notify:
        return False
      
      self._src_index.model().endMoveRows()
      
      return False
  
  def __init__(self, root_node, undo_stack, project_tree_controller, parent=None):
    """Constructor.
    root_node -- Root node of the project tree.
    undo_stack -- QUndoStack to receive commands generated through user interaction with this Qt model.
    project_tree_controller -- Reference to the ProjectTreeController in charge of high-level changes to the project
      tree.
    parent -- Parent QObject.
    """
    super().__init__(parent)
    
    self._root_node = root_node
    self._undo_stack = undo_stack
    self._project_tree_controller = project_tree_controller
    
    # Create a cache for icons to avoid reloading icons unnecessarily. Keys are node classes, and values are QIcons.
    self._icon_cache = {}
  
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
  
  def begin_rename_node(self, node, new_name):
    """Notifies the ProjectTreeQtModel that a node rename operation is about to take place.
    Returns a notifier object that implements operations required before and after the rename in its __enter__ and
    __exit__ methods, and therefore can be used in a with statement. The actual rename operation should be performed
    inside the with statement; this function does not perform it.
    node -- Node to be renamed.
    new_name -- New name to which the node will be renamed.
    """
    # Determine what the node's child index will be after the rename.
    child_idx_after_rename = 0
    if node.parent is not None:
      child_idx_after_rename = node.parent.child_idx_from_name(new_name)
      if child_idx_after_rename > node.idx_in_parent():
        child_idx_after_rename -= 1
    
    qt_index = self.node_to_qt_index(node)
    return ProjectTreeQtModel._MoveRowNotifier(qt_index, qt_index.parent(), child_idx_after_rename)
  
  def _icon_for_node(self, node):
    """Gets the QIcon that should be used to decorate the specified node.
    node -- Node whose icon is to be obtained.
    """
    if node.__class__ not in self._icon_cache:
      self._icon_cache[node.__class__] = node.__class__.make_icon()
    return self._icon_cache[node.__class__]
  
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
        
        if role == QtCore.Qt.EditRole:
          return node.name
        
        if role == QtCore.Qt.DecorationRole:
          return self._icon_for_node(node)
    
    # Return an invalid QVariant if the data could not be found.
    return QVariant()
  
  def setData(self, index, value, role):
    if index.isValid():
      if role == QtCore.Qt.EditRole:
        
        # Rename the node.
        try:
          self._undo_stack.push(RenameProjectTreeNodeCommand(self._project_tree_controller, self.qt_index_to_node(index),
            value))
          return True
        
        # Renaming may fail due to the name being invalid or unavailable.
        except ValueError:
          # TODO: Maybe log the error message to explain the reason for the cancellation of the operation.
          return False
    
    return False
  
  def flags(self, index):
    if not index.isValid():
      return QtCore.Qt.NoItemFlags
    
    return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEditable