"""Utilities related to dictionaries."""

from collections import UserDict
from scipy._lib._ccallback_c import idx

class ReorderableDict(UserDict):
  """A dictionary-like type that maintains its keys in a well-defined order.
  This class is similar to OrderedDict from the standard library, but does not force the key ordering to match the order
  in which the keys were inserted.
  By default, setting a mapping in the dictionary moves the mapping to the end of the ordering, whether the key was
  already present or not. To set a mapping without moving it to the end, use set_at_index or set_keeping_index."""
  
  def __init__(self):
    super().__init__()
    self._ordered_keys = []
  
  def __setitem__(self, key, item):
    self.set_at_index(key, item)
  
  def __iter__(self):
    for idx in range(len(self.data)):
      yield self.key_at_index(idx)
  
  def key_at_index(self, idx):
    """Gets the key of the mapping at the specified index in this dictionary's ordering.
    idx -- Ordering index to query.
    """
    return self._ordered_keys[idx]
  
  def val_at_index(self, idx):
    """Gets the value of the mapping at the specified index in this dictionary's ordering.
    idx -- Ordering index to query.
    """
    return self.data[self.key_at_index(idx)]
  
  def mapping_at_index(self, idx):
    """Gets the mapping at the specified index in this dictionary's ordering, as a key/value pair.
    idx -- Ordering index to query.
    """
    key = self.key_at_index(idx)
    return (key, self.data[key])
  
  def set_at_index(self, key, item, idx=None):
    """Inserts a mapping into the ordered dictionary.
    key -- Key of the mapping.
    item -- Value of the mapping.
    idx -- Index at which to place the key in the dictionary's ordering. If the key is already present before the
      insertion, it will be moved to this index. Default is None, which places the key at the end of the ordering.
    """
    key_already_present = key in self.data
    
    # Check for invalid index.
    max_idx = len(self.data) - (1 if key_already_present else 0)
    min_idx = -(max_idx + 1)
    if idx is not None and not (min_idx <= idx <= max_idx):
      raise IndexError('Index {} out of bounds'.format(str(idx)))
    
    # Store the mapping in the dictionary.
    self.data[key] = item
    
    # Update the ordering.
    if key_already_present:
      self._ordered_keys.remove(key)
      if idx is None:
        idx = len(self._order_list)
      self._ordered_keys.insert(idx, key)
  
  def set_keeping_index(self, key, item):
    """Inserts a mapping into the ordered dictionary, without moving the key to the end of the dictionary's ordering.
    If the specified key is already present, it will keep its current position in the ordering. If the key is not
    already present, it will be added at the end of the ordering.
    """
    key_already_present = key in self.data
    self.data[key] = item
    if not key_already_present:
      self._ordered_keys.append(key)
  
  def move_to_index(self, key, idx=None):
    """Moves an existing mapping to the specified position in the dictionary's ordering.
    Does nothing if the specified key is not present.
    key -- Key of the mapping to move.
    idx -- New index at which to place the key in the dictionary's ordering. Default is None, which places the key at
      the end of the ordering.
    """
    if key in self.data:
      # Check for invalid index.
      max_idx = len(self.data) - 1
      min_idx = -(max_idx + 1)
      if idx is not None and not (min_idx <= idx <= max_idx):
        raise IndexError('Index {} out of bounds'.format(str(idx)))
      
      self._ordered_keys.remove(key)
      if idx is None:
        idx = len(self._order_list)
      self._ordered_keys.insert(idx, key)