"""Defines a Qt model for visualizing a sequence component tree."""

from PyQt5 import QtCore
from PyQt5.Qt import QAbstractItemModel, QModelIndex, QVariant, QCoreApplication, QMimeData

from scriptaseq.internal.gui.qt_models.qt_model_notifiers import DoNothingNotifier, AddNodeNotifier, DeleteNodeNotifier, \
  MoveNodeNotifier, ResetModelNotifier
from scriptaseq.internal.gui.undo_commands.seq_component_tree import RenameSequenceComponentTreeNodeCommand, \
  ReparentSequenceComponentTreeNodeCommand
from scriptaseq.internal.mime_data import SEQUENCE_COMPONENT_TREE_NODE_PATH_MEDIA_TYPE, encode_seq_component_tree_node_path, \
  decode_seq_component_tree_node_path
from scriptaseq.internal.project_tree.project_tree_nodes import SequenceProjectTreeNode


# TODO: Figure out if it is possible to reduce code duplication between ProjectTreeQtModel and
# SequenceComponentTreeQtModel.
class SequenceComponentTreeQtModel(QAbstractItemModel):
  """Qt model class for visualizing a sequence component tree.
  Despite the name, this class is designed to fit most closely into the View role of the MVC pattern.
  """
  
  def __init__(self, undo_stack, project_tree_controller, seq_component_tree_controller, seq_component_node_controller,
    parent=None):
    """Constructor.
    undo_stack -- QUndoStack to receive commands generated through user interaction with this Qt model.
    project_tree_controller -- Reference to the ProjectTreeController in charge of high-level changes to the project
      tree.
    seq_component_tree_controller -- Reference to the SequenceComponentTreeController in charge of high-level changes to
      sequence component trees.
    seq_component_node_controller -- Reference to the SequenceComponentNodeController in charge of making changes to
      individual nodes in sequence component trees.
    parent -- Parent QObject.
    """
    super().__init__(parent)
    
    self._undo_stack = undo_stack
    self._project_tree_controller = project_tree_controller
    self._seq_component_tree_controller = seq_component_tree_controller
    # No need to store a reference to seq_component_node_controller; we just need to connect to its signals.
    
    self._seq_component_tree_controller.node_renamed.connect(self._node_name_changed)
    seq_component_node_controller.node_component_type_changed.connect(self._node_component_type_changed)
  
  def node_to_qt_index(self, seq_component_tree_node):
    """Creates a QModelIndex pointing to the specified sequence component tree node.
    Returns an invalid index if the sequence component tree is not the one currently being displayed by this
    SequenceComponentTreeQtModel.
    project_tree_node -- Project tree node that owns the sequence component tree.
    seq_component_tree_node -- Sequence component tree node to which the QModelIndex should refer.
    """
    # Return an invalid index for nodes that do not belong to the active project tree node.
    if self._project_tree_controller.active_node is not seq_component_tree_node.owning_project_tree_node:
      return QModelIndex()
    
    row = 0 if seq_component_tree_node.parent is None else seq_component_tree_node.idx_in_parent()
    
    return self.createIndex(row, 0, seq_component_tree_node)
  
  def qt_index_to_node(self, index):
    """Extracts the sequence component tree node referenced by the specified QModelIndex.
    Returns None if the QModelIndex does not refer to a sequence component tree node.
    index -- QModelIndex identifying the node to return.
    """
    if not index.isValid():
      return None
    
    return index.internalPointer()
  
  def begin_change_active_project_tree_node(self):
    """Notifies the SequenceComponentTreeQtModel that the active node in the project tree is about to change.
    Returns a notifier object that implements operations required before and after the change in its __enter__ and
    __exit__ methods, and therefore can be used in a with statement. The actual change should be performed inside the
    with statement; this function does not perform it.
    """
    return ResetModelNotifier(self)
  
  def begin_add_node(self, node_to_add, parent):
    """Notifies the SequenceComponentTreeQtModel that a node addition operation is about to take place.
    Returns a notifier object that implements operations required before and after the addition in its __enter__ and
    __exit__ methods, and therefore can be used in a with statement. The actual addition operation should be performed
    inside the with statement; this function does not perform it.
    Raises ValueError if it is determined that the operation cannot be performed.
    node_to_add -- Sequence component tree node to be added.
    parent -- Parent to which the node will be added.
    """
    if node_to_add.parent is not None or node_to_add is node_to_add.owning_project_tree_node.root_seq_component_node:
      raise ValueError(
        QCoreApplication.translate('SequenceComponentTreeQtModel', 'Cannot add a node that already exists in the sequence component tree.'))
    
    # No special operations are required if the sequence component tree being modified is not the one this Qt model is
    # showing.
    if self._project_tree_controller.active_node is not node_to_add.owning_project_tree_node:
      return DoNothingNotifier()
    
    return AddNodeNotifier(self, self.node_to_qt_index(parent), parent.child_idx_from_name(node_to_add.name))
  
  def begin_delete_node(self, node_to_delete):
    """Notifies the SequenceComponentTreeQtModel that a node deletion operation is about to take place.
    Returns a notifier object that implements operations required before and after the deletion in its __enter__ and
    __exit__ methods, and therefore can be used in a with statement. The actual deletion operation should be performed
    inside the with statement; this function does not perform it.
    Raises ValueError if it is determined that the operation cannot be performed.
    node_to_delete -- Sequence component tree node to be deleted.
    """
    if node_to_delete.parent is None:
      raise ValueError(
        QCoreApplication.translate('SequenceComponentTreeQtModel', 'Cannot delete root node from the sequence component tree.'))
    
    # No special operations are required if the sequence component tree being modified is not the one this Qt model is
    # showing.
    if self._project_tree_controller.active_node is not node_to_delete.owning_project_tree_node:
      return DoNothingNotifier()
    
    return DeleteNodeNotifier(self, self.node_to_qt_index(node_to_delete))
  
  def begin_rename_node(self, node_to_rename, new_name):
    """Notifies the SequenceComponentTreeQtModel that a node rename operation is about to take place.
    Returns a notifier object that implements operations required before and after the rename in its __enter__ and
    __exit__ methods, and therefore can be used in a with statement. The actual rename operation should be performed
    inside the with statement; this function does not perform it.
    node_to_rename -- Sequence component tree node to be renamed.
    new_name -- New name to which the node will be renamed.
    """
    # No special operations are required if the sequence component tree being modified is not the one this Qt model is
    # showing.
    if self._project_tree_controller.active_node is not node_to_rename.owning_project_tree_node:
      return DoNothingNotifier()
    
    # Determine what the node's child index will be after the rename.
    child_idx_after_rename = 0
    if node_to_rename.parent is not None:
      child_idx_after_rename = node_to_rename.parent.child_idx_from_name(new_name)
      if child_idx_after_rename > node_to_rename.idx_in_parent():
        child_idx_after_rename -= 1
    
    qt_index = self.node_to_qt_index(node_to_rename)
    return MoveNodeNotifier(self, qt_index, qt_index.parent(), child_idx_after_rename)
  
  def begin_reparent_node(self, node_to_reparent, new_parent):
    """Notifies the SequenceComponentTreeQtModel that a node reparent operation is about to take place.
    Returns a notifier object that implements operations required before and after the reparenting in its __enter__ and
    __exit__ methods, and therefore can be used in a with statement. The actual reparent operation should be performed
    inside the with statement; this function does not perform it.
    Raises ValueError if it is determined that the operation cannot be performed.
    node_to_reparent -- Sequence component tree node to be reparented.
    new_parent -- New parent to which the node will be attached.
    """
    # Check that the operation is valid.
    new_parent.verify_can_add_as_child(node_to_reparent)
    
    # No special operations are required if the sequence component tree being modified is not the one this Qt model is
    # showing.
    if self._project_tree_controller.active_node is not node_to_reparent.owning_project_tree_node:
      return DoNothingNotifier()
    
    # Determine what the node's child index will be after the operation.
    child_idx_after_reparent = new_parent.child_idx_from_name(node_to_reparent.name)
    
    node_qt_index = self.node_to_qt_index(node_to_reparent)
    new_parent_qt_index = self.node_to_qt_index(new_parent)
    return MoveNodeNotifier(self, node_qt_index, new_parent_qt_index, child_idx_after_reparent)
  
  def _has_active_sequence(self):
    """Checks whether there is currently an active project tree node and it represents a sequence."""
    return isinstance(self._project_tree_controller.active_node, SequenceProjectTreeNode)
  
  def _node_name_changed(self, node, new_name, old_name):
    """Should be called after a sequence component tree node has been renamed.
    This method is meant to be invoked by a signal from the SequenceComponentTreeController.
    node -- Sequence component tree node that has been renamed.
    new_name -- New name to which the node was renamed.
    old_name -- Old name from which the node was renamed.
    """
    qt_index = self.node_to_qt_index(node)
    if qt_index.isValid():
      self.dataChanged.emit(qt_index, qt_index, [QtCore.Qt.DisplayRole, QtCore.Qt.EditRole])
  
  def _node_component_type_changed(self, node, new_component_type, old_component_type):
    """Should be called after a sequence component tree node has had its component type changed.
    This method is meant to be invoked by a signal from the SequenceComponentNodeController.
    node -- Sequence component tree node whose component type has changed.
    new_component_type -- New component type that was assigned to the node.
    old_component_type -- Component type that the node had before the change.
    """
    qt_index = self.node_to_qt_index(node)
    if qt_index.isValid():
      self.dataChanged.emit(qt_index, qt_index, [QtCore.Qt.DecorationRole])
  
  def index(self, row, column, parent=QModelIndex()):
    if not self.hasIndex(row, column, parent):
      return QModelIndex()
    
    # The call to self.hasIndex should return false if there is no active sequence.
    assert self._has_active_sequence()
    
    parent_node = self.qt_index_to_node(parent)
    if parent_node is None:
      child_node = self._project_tree_controller.active_node.root_seq_component_node
    else:
      child_node = parent_node.child_at_idx(row)
    
    return self.node_to_qt_index(child_node)
  
  def parent(self, index):
    if not index.isValid():
      return QModelIndex()
    
    node = self.qt_index_to_node(index)
    
    # Return an invalid index if the node has no parent.
    if node is None or node.parent is None:
      return QModelIndex()
    
    # Otherwise, create an index pointing to the parent node.
    else:
      return self.node_to_qt_index(node.parent)
  
  def rowCount(self, parent):
    if not self._has_active_sequence():
      return 0
    elif not parent.isValid():
      return 1
    else:
      parent_node = self.qt_index_to_node(parent)
      return len(parent_node.children)
  
  def columnCount(self, parent):
    return 1
  
  def data(self, index, role):
    if index.isValid():
      
      node = self.qt_index_to_node(index)
    
      if node is not None and index.column() == 0:
        
        if role == QtCore.Qt.DisplayRole:
          return node.name
        
        if role == QtCore.Qt.EditRole:
          return node.name
        
        if role == QtCore.Qt.DecorationRole:
          return node.component_type.get_icon()
    
    # Return an invalid QVariant if the data could not be found.
    return QVariant()
  
  def setData(self, index, value, role):
    node = self.qt_index_to_node(index)
    if node is not None:
      if role == QtCore.Qt.EditRole:
        
        # Rename the node.
        try:
          self._undo_stack.push(RenameSequenceComponentTreeNodeCommand(self._seq_component_tree_controller, node,
            value))
          return True
        
        # Renaming may fail due to the name being invalid or unavailable.
        except ValueError:
          # TODO: Maybe log the error message to explain the reason for the cancellation of the operation.
          return False
    
    return False
  
  def flags(self, index):
    node = self.qt_index_to_node(index)
    
    if node is None:
      return QtCore.Qt.NoItemFlags
    
    # Flags are different for the root node.
    if node.parent is None:
      return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsDragEnabled \
        | QtCore.Qt.ItemIsDropEnabled
    
    else:
      return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEditable \
        | QtCore.Qt.ItemIsDragEnabled | QtCore.Qt.ItemIsDropEnabled
  
  def mimeTypes(self):
    return [SEQUENCE_COMPONENT_TREE_NODE_PATH_MEDIA_TYPE]
  
  def mimeData(self, indexes):
    result = QMimeData()
    node = self.qt_index_to_node(indexes[0])
    if node is not None:
      path_data = encode_seq_component_tree_node_path(
        self._project_tree_controller.active_node.abs_name_path, node.abs_name_path)
      result.setData(SEQUENCE_COMPONENT_TREE_NODE_PATH_MEDIA_TYPE, path_data)
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
        
        if not self._has_active_sequence():
          return False
        
        # Check that the operation applies to the active project tree node.
        project_tree_path, seq_component_tree_path = decode_seq_component_tree_node_path(data.data(
          SEQUENCE_COMPONENT_TREE_NODE_PATH_MEDIA_TYPE))
        project_tree_node = self._project_tree_controller.active_node.tree_root.resolve_path(project_tree_path)
        if self._project_tree_controller.active_node is not project_tree_node:
          return False
        
        node = self._project_tree_controller.active_node.root_seq_component_node.resolve_path(seq_component_tree_path)
        parent_node = self.qt_index_to_node(parent)
        if parent_node is None:
          return False
        if node.parent is parent_node:
          return False
        parent_node.verify_can_add_as_child(node)
      
      except ValueError:
        return False
    
    # Return true if all checks passed.
    return True
  
  def dropMimeData(self, data, action, row, column, parent):
    if not self.canDropMimeData(data, action, row, column, parent):
      return False
    
    # Handle ignore actions.
    if action == QtCore.Qt.IgnoreAction:
      return True
    
    # Handle node move actions.
    if action == QtCore.Qt.MoveAction and data.hasFormat(SEQUENCE_COMPONENT_TREE_NODE_PATH_MEDIA_TYPE):
      try:
        
        _, seq_component_tree_path = decode_seq_component_tree_node_path(data.data(
          SEQUENCE_COMPONENT_TREE_NODE_PATH_MEDIA_TYPE))
        
        node = self._project_tree_controller.active_node.root_seq_component_node.resolve_path(seq_component_tree_path)
        new_parent_node = self.qt_index_to_node(parent)
        self._undo_stack.push(ReparentSequenceComponentTreeNodeCommand(self._seq_component_tree_controller, node,
          new_parent_node))
        return True
      
      except ValueError:
        return False
    
    return False