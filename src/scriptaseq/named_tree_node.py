"""Base functionality for creating trees of named nodes."""

from sortedcontainers.sorteddict import SortedDict
from PyQt5.Qt import QCoreApplication


# Separator string used when encoding a node name path as a string.
NAME_PATH_SEPARATOR = '/'

# Sequence containing the substrings that are disallowed in node names.
NAME_DISALLOWED_SUBSTRINGS = (NAME_PATH_SEPARATOR,)

# Default name prefix to use when suggesting an available child name.
DEFAULT_NAME_PREFIX = 'Node'

# Format string used to convert a name suffix number to a suffix string when suggesting an available child name.
_SUFFIX_FORMAT_STRING = '_{:08}'

class TreeNamePath:
  """Represents a path identifying a NamedTreeNode in a tree."""
  
  def __init__(self, path_names, is_absolute=True):
    """Constructor.
    path_names -- Iterable containing the names along the path, starting with the highest in the tree.
    is_absolute -- Indicates whether the path is absolute (relative to the root node) or relative.
    """
    # Raise ValueError if path_names contains an invalid path name.
    for path_name in path_names:
      NamedTreeNode.verify_name_valid(path_name)
    
    self._path_names = tuple(path_names)
    self._is_absolute = is_absolute
  
  @staticmethod
  def from_str(path_str):
    """Converts a path string to a TreeNamePath object.
    path_str -- Path string to convert. This may have been obtained by previously converting a TreeNamePath to a string.
    """
    # Detect and remove leading / for absolute paths.
    is_absolute = path_str.startswith(NAME_PATH_SEPARATOR)
    if is_absolute:
      path_str = path_str[len(NAME_PATH_SEPARATOR):]
    
    # Separate the path names.
    if path_str == '':
      return TreeNamePath([], is_absolute)
    else:
      path_names = path_str.split(NAME_PATH_SEPARATOR)
      return TreeNamePath(path_names, is_absolute)
  
  @property
  def is_absolute(self):
    """Read-only property indicating whether this is an absolute or relative path."""
    return self._is_absolute
  
  @property
  def path_names(self):
    """Read-only property containing the names in the path, as an immutable sequence."""
    return self._path_names
  
  def __str__(self):
    result = NAME_PATH_SEPARATOR.join(self.path_names)
    if self.is_absolute:
      result = NAME_PATH_SEPARATOR + result
    return result
  
  def __eq__(self, other):
    return \
      isinstance(other, TreeNamePath) \
      and bool(self.is_absolute) == bool(other.is_absolute) \
      and self.path_names == other.path_names
  
  def __hash__(self):
    return hash((self.is_absolute, self.path_names))

class NamedTreeNode:
  """Base class representing a node in a tree of named nodes.
  This class assumes a tree model in which nodes may have zero or more children indexed by string names, and any two
  sibling nodes must have different names. Each parent node contains a name-indexed, sorted collection of child
  references, and each child node also contains a reference to its parent.
  This class provides functionality for accessing nodes by relative name paths. In order to support a simple string
  representation of paths, certain substrings have special meaning and are not allowed in node names. The disallowed
  substrings are recorded in NAME_DISALLOWED_SUBSTRINGS.
  """
  
  def __init__(self, name, can_have_children=True, parent=None):
    """Constructor.
    Raises ValueError if the name is invalid, the parent node already has another child with the specified name, or the
    parent node is not allowed to have children.
    name -- Name for the new node.
    can_have_children -- Indicates whether the node is allowed to have children.
    parent -- NamedTreeNode reference indicating the parent to which the node will be attached as a child. The default
      value is None, meaning the node will have no parent and will be considered a root node.
    """
    self._parent = None
    self._name = ''
    self._children = SortedDict()
    self.name = name
    self.parent = parent
    self.can_have_children = can_have_children
  
  @staticmethod
  def verify_name_valid(name):
    """Checks if a prospective node name is valid, and raises ValueError if not.
    name -- Name to check.
    """
    # Check if the name is empty.
    if name == '':
      raise ValueError(QCoreApplication.translate('NamedTreeNode', 'Node name must not be empty.'))
    
    # Check if the name contains a disallowed substring.
    for substring in NAME_DISALLOWED_SUBSTRINGS:
      if substring in name:
        raise ValueError(
          QCoreApplication.translate('NamedTreeNode', "Node name must not contain '{}'.").format(substring))
  
  @property
  def name(self):
    """Property containing the node's name.
    Setting this property will raise ValueError if the new name is empty or contains a disallowed substring, or if the
    node's parent already has another child with the desired name.
    """
    return self._name
  
  @name.setter
  def name(self, name):
    # Do nothing if this node already has the specified name.
    if name == self.name:
      return
    
    # Check that the name is valid.
    NamedTreeNode.verify_name_valid(name)
    
    # Check that the name is available.
    if self.parent is not None:
      self.parent.verify_child_name_available(name)
    
    # Set the name. The procedure for doing this depends on whether the node has a parent.
    if self.parent is None:
      self._name = name
    else:
      parent = self.parent
      parent.remove_child(self._name)
      self._name = name
      parent.add_child(self)
  
  @property
  def parent(self):
    """Property containing the node's parent reference.
    The value is None for root nodes.
    Setting this property will raise ValueError if the new parent already contains another child with the same name as
    this node, if setting the parent would create an inheritance cycle, or if the parent is not allowed to have
    children.
    """
    return self._parent
  
  @parent.setter
  def parent(self, parent):
    # Make sure the new parent assignment is valid.
    if parent is not None:
      parent.verify_can_add_as_child(self)
    
    # Update the old and new parent nodes' child collections.
    if self._parent is not None:
      del self._parent._children[self.name]
    if parent is not None:
      parent._children[self.name] = self
    
    # Update the parent reference.
    self._parent = parent
  
  @property
  def can_have_children(self):
    """Property indicating whether the node is allowed to have children.
    Setting this property to false will cause any existing children of the node to be removed.
    """
    return self._can_have_children
  
  @can_have_children.setter
  def can_have_children(self, can_have_children):
    # If setting to false, remove any existing children.
    if not can_have_children:
      for child in list(self._children.values()):
        child.parent = None
    
    self._can_have_children = bool(can_have_children)
  
  @property
  def children(self):
    """Read-only property containing the node's indexed child collection, as a SortedDict.
    Avoid modifying the returned object from outside the NamedTreeNode class."""
    # TODO: Maybe use a custom subclass of SortedDict to make modification of the returned object safe.
    return self._children
  
  @property
  def ancestors(self):
    """Read-only property that creates an iterable of the node's ancestors, ordered from bottom to top.
    This function does not consider a node to be an ancestor of itself.
    """
    ancestor = self.parent
    while ancestor is not None:
      yield ancestor
      ancestor = ancestor.parent
  
  @property
  def tree_root(self):
    """Read-only property that gets a reference to the node's root ancestor, or the node itself if it is the root."""
    if self.parent is None:
      return self
    else:
      # Return the last node in the ancestors iterable.
      for result in self.ancestors:
        pass
      return result
  
  @property
  def abs_name_path(self):
    """Read-only property that creates an absolute TreeNamePath pointing to this node's location in the tree."""
    path_list = self._abs_name_path_list()
    return TreeNamePath(path_list)
  
  def add_child(self, child):
    """Adds the specified node as a child of this node.
    This is equivalent to setting child.parent = self, and will raise an exception under the same circumstances.
    child -- The child node to add.
    """
    child.parent = self
  
  def remove_child(self, child_name):
    """Removes the specified child node from this parent node.
    If no child with the specified name is found, does nothing.
    child_name -- Name of the child to remove.
    """
    if child_name in self._children:
      self._children[child_name].parent = None
  
  def suggest_child_name(self, prefix=DEFAULT_NAME_PREFIX):
    """Suggests an available child name starting with the specified prefix.
    Raises ValueError if this node is not allowed to have children, or if the prefix is not a valid node name.
    prefix -- String that the child name must start with.
    """
    # Check that the prefix is a valid name.
    NamedTreeNode.verify_name_valid(prefix)
    
    # Check that this node is allowed to have children.
    if not self.can_have_children:
      raise ValueError(
        QCoreApplication.translate('NamedTreeNode', "Node '{}' is not allowed to have children.").format(self.name))
    
    # Use the prefix as the full name if it is available.
    if prefix not in self._children:
      return prefix
    
    # Otherwise, append a number to the prefix.
    suffix_num = 0
    while prefix + _SUFFIX_FORMAT_STRING.format(suffix_num) in self._children:
      suffix_num += 1
    
    return prefix + _SUFFIX_FORMAT_STRING.format(suffix_num)
  
  def resolve_path(self, path):
    """Resolves a TreeNamePath and returns the NamedTreeNode it points to.
    If path is an absolute path, the path will be resolved relative to the root of the tree containing this node.
    Otherwise, the path will be resolved relative to this node.
    Raises ValueError if no node matching the path is found.
    path -- TreeNamePath to resolve.
    """
    curr_node = self.tree_root if path.is_absolute else self
    for name in path.path_names:
      if name not in curr_node._children:
        raise ValueError(QCoreApplication.translate('NamedTreeNode', "Failed to resolve path '{}'.").format(path))
      curr_node = curr_node._children[name]
    
    return curr_node
  
  def idx_in_parent(self):
    """Determines the numerical index at which this child node can be found in its parent.
    Returns None if this node has no parent.
    """
    if self.parent is None:
      return None
    else:
      return self.parent.child_idx_from_name(self.name)
  
  def child_at_idx(self, idx):
    """Finds the child at the specified numerical index in this node's child ordering.
    idx -- Index to query.
    """
    return self._children.peekitem(idx)[1]
  
  def child_idx_from_name(self, child_name):
    """Finds the index of the node with the specified name in this node's child ordering.
    If this node has no child with the specified name, this function will instead predict what the index would be if a
    child of the specified name were to be added.
    child_name -- Name of the child to query, or the prospective child to be added.
    """
    # If this node has a child with the specified name, return the index of that child.
    if child_name in self._children:
      return self._children.index(child_name)
    
    # Otherwise, predict what the insertion index would be if a child with the specified name were added.
    # TODO: This could probably be made more efficient.
    children_copy = self._children.copy()
    children_copy[child_name] = None
    return children_copy.index(child_name)
  
  def verify_child_name_available(self, name):
    """Checks that the specified name is valid and available under this parent node, and raises ValueError if not.
    All child names are considered unavailable if this node is not allowed to have children. Otherwise, a valid name is
    considered available if and only if this node currently has no child with that name.
    name -- Name to check.
    """
    # Check that the name is valid.
    NamedTreeNode.verify_name_valid(name)
    
    # Check that this node can have children.
    if not self.can_have_children:
      raise ValueError(
        QCoreApplication.translate('NamedTreeNode', "Node '{}' is not allowed to have children.").format(self.name))
    
    # Check that this node does not have a child with the specified name.
    if name in self._children:
      raise ValueError(
        QCoreApplication.translate('NamedTreeNode', "Node '{}' already has a child named '{}'").format(self.name, name))
  
  def verify_can_add_as_child(self, node):
    """Checks if the specified node can be added as a child of this node, and raises ValueError if not.
    Does not raise an exception if the specified node is already a child of this node.
    node -- The prospective new child node.
    """
    # Do nothing if the node is already a child of this node.
    if node.name in self._children and self._children[node.name] is node:
      return
    
    # Chick if the node's name is available as a child name for this node. This will also check if this node is allowed
    # to have children.
    self.verify_child_name_available(node.name)
    
    # Check if adding the child would create an inheritance cycle.
    if self is node:
      raise ValueError(QCoreApplication.translate('NamedTreeNode', 'Cannot make a node a child of itself.'))
    if node in self.ancestors:
      raise ValueError(QCoreApplication.translate('NamedTreeNode', 'Operation would create a cycle in the tree.'))
  
  def _abs_name_path_list(self):
    """Gets the absolute path to this node, as a mutable list of node names."""
    # For a root node, use an empty path.
    if self.parent is None:
      return []
    
    # For a non-root node, use the parent node's absolute path with this node's name appended.
    result = self.parent._abs_name_path_list()
    result += [self.name]
    return result