"""Defines classes that call appropriate methods on Qt models to notify viewers of changes."""

class DoNothingNotifier:
  """Class that behaves like the other change notifier classes, but does nothing before or after the change."""
  
  def __enter__(self):
    pass
  
  def __exit__(self):
    pass

class ResetModelNotifier:
  """Class that calls appropriate methods to notify a QAbstractItemModel's views that the model is being reset.
  The notifier class is suitable for use in a with statement to perform operations before and after the change. The
  notifier itself does not perform the change.
  """
  
  def __init__(self, qt_model):
    """Constructor.
    qt_model -- QAbstractItemModel that owns this notifier.
    """
    self._qt_model = qt_model
  
  def __enter__(self):
    self._qt_model.beginResetModel()
    
    return self
  
  def __exit__(self, exc_type, exc_value, exc_traceback):
    self._qt_model.endResetModel()
    
    return False

class AddNodeNotifier:
  """Class that calls appropriate methods to notify a QAbstractItemModel's views that a tree node is being added.
  The notifier class is suitable for use in a with statement to perform operations before and after the change. The
  notifier itself does not perform the change.
  """
  
  def __init__(self, qt_model, parent, dst_row):
    """Constructor.
    qt_model -- QAbstractItemModel that owns this notifier.
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

class DeleteNodeNotifier:
  """Class that calls appropriate methods to notify a Qt model's views that a tree node is being deleted.
  The notifier class is suitable for use in a with statement to perform operations before and after the change. The
  notifier itself does not perform the change.
  """
  
  def __init__(self, qt_model, index):
    """Constructor.
    qt_model -- QAbstractItemModel that owns this notifier.
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

class MoveNodeNotifier:
  """Class that calls appropriate methods to notify a QAbstractItemModel's views that a node is being moved.
  The notifier class is suitable for use in a with statement to perform operations before and after the change. The
  notifier itself does not perform the change.
  """
  
  def __init__(self, qt_model, src_index, dst_parent, dst_row):
    """Constructor.
    qt_model -- QAbstractItemModel that owns this notifier.
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
    
    # If we are moving the root, the notifier shouldn't do anything, as the root is not displayed.
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