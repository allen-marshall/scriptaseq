"""Defines a Qt model for visualizing the project tree."""
from PyQt5 import QtCore
from PyQt5.Qt import QAbstractItemModel, QModelIndex, QVariant, QCoreApplication, QMimeData

from scriptaseq.internal.gui.undo_commands.project_tree import RenameProjectTreeNodeCommand,\
  ReparentProjectTreeNodeCommand
from scriptaseq.internal.mime_data import PROJECT_TREE_NODE_PATH_MEDIA_TYPE, encode_project_tree_node_path,\
  decode_project_tree_node_path


class ProjectTreeQtModel(QAbstractItemModel):
  """Qt model class for visualizing the project tree.
  Despite the name, this class is designed to fit most closely into the View role of the MVC pattern.
  """
  
  class _AddNodeNotifier:
    """Class that calls appropriate methods to notify this Qt model's views that a node is being added.
    The notifier class is suitable for use in a with statement to perform operations before and after the change. The
    notifier itself does not perform the change.
    """
    
    def __init__(self, qt_model, parent, dst_row):
      """Constructor.
      qt_model -- ProjectTreeQtModel that owns this notifier.
      parent -- QModelIndex of the parent node to which the new child will be added.
      dst_row -- Numerical index that the node is expected to have within its parent's child ordering after the
        addition.
      """
      self._qt_model = qt_model
      self._parent = parent
      self._dst_row = dst_row
    
    def __enter__(self):
      self._qt_model.beginInsertRows(self._parent, self._dst_row, self._dst_row)
      
      return self
    
    def __exit__(self, exc_type, exc_value, exc_traceback):
      self._qt_model.endInsertRows()
      
      return False
  
  class _DeleteNodeNotifier:
    """Class that calls appropriate methods to notify this Qt model's views that a node is being deleted.
    The notifier class is suitable for use in a with statement to perform operations before and after the change. The
    notifier itself does not perform the change.
    """
    
    def __init__(self, qt_model, index):
      """Constructor.
      qt_model -- ProjectTreeQtModel that owns this notifier.
      index -- QModelIndex of the node to be deleted.
      """
      self._qt_model = qt_model
      self._index = index
      self._should_notify = index.isValid()
    
    def __enter__(self):
      if not self._should_notify:
        return self
      
      self._qt_model.beginRemoveRows(self._index.parent(), self._index.row(), self._index.row())
      
      return self
    
    def __exit__(self, exc_type, exc_value, exc_traceback):
      if not self._should_notify:
        return False
      
      self._qt_model.endRemoveRows()
      
      return False
  
  class _MoveNodeNotifier:
    """Class that calls appropriate methods to notify this Qt model's views that a node is being moved.
    The notifier class is suitable for use in a with statement to perform operations before and after the change. The
    notifier itself does not perform the change.
    """
    
    def __init__(self, qt_model, src_index, dst_parent, dst_row):
      """Constructor.
      qt_model -- ProjectTreeQtModel that owns this notifier.
      src_index -- QModelIndex of the node to be moved.
      dst_parent -- QModelIndex of the parent node to which the node will be moved.
      dst_row -- Numerical index that the node is expected to have within its parent's child ordering after the move.
      """
      self._qt_model = qt_model
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
      assert self._qt_model.beginMoveRows(self._src_index.parent(), self._src_index.row(),
        self._src_index.row(), self._dst_parent, dst_row)
      
      return self
    
    def __exit__(self, exc_type, exc_value, exc_traceback):
      if not self._should_notify:
        return False
      
      self._qt_model.endMoveRows()
      
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
  
  def begin_add_node(self, node, parent):
    """Notifies the ProjectTreeQtModel that a node addition operation is about to take place.
    Returns a notifier object that implements operations required before and after the addition in its __enter__ and
    __exit__ methods, and therefore can be used in a with statement. The actual addition operation should be performed
    inside the with statement; this function does not perform it.
    Raises ValueError if node already has a parent or is the root node.
    node -- Node to be added.
    parent -- Parent to which the node will be added.
    """
    if node.parent is not None or node is self._root_node:
      raise ValueError(
        QCoreApplication.translate('ProjectTreeQtModel', 'Cannot add a node that already exists in the project tree.'))
    
    return ProjectTreeQtModel._AddNodeNotifier(self, self.node_to_qt_index(parent),
      parent.child_idx_from_name(node.name))
  
  def begin_delete_node(self, node):
    """Notifies the ProjectTreeQtModel that a node deletion operation is about to take place.
    Returns a notifier object that implements operations required before and after the deletion in its __enter__ and
    __exit__ methods, and therefore can be used in a with statement. The actual deletion operation should be performed
    inside the with statement; this function does not perform it.
    Raises ValueError if node is the root node.
    node -- Node to be deleted.
    """
    if node.parent is None:
      raise ValueError(
        QCoreApplication.translate('ProjectTreeQtModel', 'Cannot delete root node from the project tree.'))
    
    return ProjectTreeQtModel._DeleteNodeNotifier(self, self.node_to_qt_index(node))
  
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
    return ProjectTreeQtModel._MoveNodeNotifier(self, qt_index, qt_index.parent(), child_idx_after_rename)
  
  def begin_reparent_node(self, node, new_parent):
    """Notifies the ProjectTreeQtModel that a node reparent operation is about to take place.
    Returns a notifier object that implements operations required before and after the reparenting in its __enter__ and
    __exit__ methods, and therefore can be used in a with statement. The actual reparent operation should be performed
    inside the with statement; this function does not perform it.
    Raises value error if it is determined that the operation cannot be performed.
    node -- Node to be reparented.
    new_parent -- New parent to which the node will be attached.
    """
    # Check that the operation is valid.
    new_parent.verify_can_add_as_child(node)
    
    # Determine what the node's child index will be after the operation.
    child_idx_after_reparent = new_parent.child_idx_from_name(node.name)
    
    node_qt_index = self.node_to_qt_index(node)
    new_parent_qt_index = self.node_to_qt_index(new_parent)
    return ProjectTreeQtModel._MoveNodeNotifier(self, node_qt_index, new_parent_qt_index, child_idx_after_reparent)
  
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
    # We use an invalid index for the root node, since we don't want to show it in the GUI.
    if not index.isValid():
      return QtCore.Qt.ItemIsDropEnabled
    
    else:
      return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEditable \
        | QtCore.Qt.ItemIsDragEnabled | QtCore.Qt.ItemIsDropEnabled
  
  def mimeTypes(self):
    return [PROJECT_TREE_NODE_PATH_MEDIA_TYPE]
  
  def mimeData(self, indexes):
    result = QMimeData()
    node = self.qt_index_to_node(indexes[0])
    path_data = encode_project_tree_node_path(node.abs_name_path)
    result.setData(PROJECT_TREE_NODE_PATH_MEDIA_TYPE, path_data)
    return result
  
  def supportedDragActions(self):
    return QtCore.Qt.IgnoreAction | QtCore.Qt.MoveAction
  
  def supportedDropActions(self):
    return QtCore.Qt.IgnoreAction | QtCore.Qt.MoveAction
  
  def canDropMimeData(self, data, action, row, column, parent):
    # Check that the media type is supported.
    if not any(map(lambda media_type: data.hasFormat(media_type), self.mimeTypes())):
      return False
    
    # Check that the drop action is supported.
    if action & self.supportedDropActions() == 0:
      return False
    
    # Check that the move operation can succeed.
    if action == QtCore.Qt.MoveAction:
      try:
        node = self._root_node.resolve_path(decode_project_tree_node_path(data.data(PROJECT_TREE_NODE_PATH_MEDIA_TYPE)))
        parent_node = self.qt_index_to_node(parent)
        if node.parent is parent_node:
          return False
        parent_node.verify_can_add_as_child(node)
      except ValueError:
        return False
    
    # Return true if all checks passed.
    return True
  
  def dropMimeData(self, data, action, row, column, parent):
    # Handle ignore actions.
    if action == QtCore.Qt.IgnoreAction:
      return True
    
    # Handle node move actions.
    if action == QtCore.Qt.MoveAction and data.hasFormat(PROJECT_TREE_NODE_PATH_MEDIA_TYPE):
      try:
        node = self._root_node.resolve_path(decode_project_tree_node_path(data.data(PROJECT_TREE_NODE_PATH_MEDIA_TYPE)))
        new_parent_node = self.qt_index_to_node(parent)
        self._undo_stack.push(ReparentProjectTreeNodeCommand(self._project_tree_controller, node, new_parent_node))
      except ValueError:
        return False
    
    return False