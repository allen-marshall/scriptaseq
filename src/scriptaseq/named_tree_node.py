"""Base functionality for creating trees of named nodes."""

from sortedcontainers.sorteddict import SortedDict


# Separator string used when encoding a node name path as a string.
NAME_PATH_SEPARATOR = '/'

# Sequence containing the substrings that are disallowed in node names.
NAME_DISALLOWED_SUBSTRINGS = (NAME_PATH_SEPARATOR,)

class TreeNamePath:
  """Represents a path identifying a NamedTreeNode in a tree."""
  
  def __init__(self, path_names, is_absolute=True):
    """Constructor.
    path_names -- Iterable containing the names along the path, starting with the highest in the tree.
    is_absolute -- Indicates whether the path is absolute (relative to the root node) or relative.
    """
    self._path_names = tuple(path_names)
    self._is_absolute = is_absolute
  
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
    self._children = SortedDict()
    self.name = name
    self.parent = parent
    self.can_have_children = can_have_children
  
  @property
  def name(self):
    """Property containing the node's name.
    Setting this property will raise ValueError if the new name is empty or contains a disallowed substring, or if the
    node's parent already has another child with the desired name.
    """
    return self._name
  
  @name.setter
  def name(self, name):
    # Check if the name is empty.
    if name == '':
      raise ValueError('Node name must not be empty.')
    
    # Check if the name contains a disallowed substring.
    for substring in NAME_DISALLOWED_SUBSTRINGS:
      if substring in name:
        raise ValueError("Node name must not contain '{}'.".format(substring))
    
    # Check if the name is available in the parent node.
    if self.parent is not None and name in self.parent.children and self.parent.children[name] is not self:
      raise ValueError("Node '{}' already has a child named '{}'.".format(self.parent.name, name))
    
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
      parent._verify_can_add_as_child(self)
    
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
        raise ValueError("Failed to resolve path '{}'.".format(path))
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
  
  def _abs_name_path_list(self):
    """Gets the absolute path to this node, as a mutable list of node names."""
    # For a root node, use an empty path.
    if self.parent is None:
      return []
    
    # For a non-root node, use the parent node's absolute path with this node's name appended.
    result = self.parent._abs_name_path_list()
    result += [self.name]
    return result
  
  def _verify_can_add_as_child(self, node):
    """Checks if the specified node can be added as a child of this node, and raises ValueError if not.
    node -- The prospective new child node.
    """
    # Check if this node can have children.
    if not self.can_have_children:
      raise ValueError("Node '{}' is not allowed to have children.".format(self.name))
    
    # Check if this node already has another child with the same name as the prospective child.
    if node.name in self._children and self._children[node.name] is not node:
      raise ValueError("Node '{}' already has a child named '{}'.".format(self.name, node.name))
    
    # Check if adding the child would create an inheritance cycle.
    if self is node:
      raise ValueError('Cannot make a node a child of itself.')
    if node in self.ancestors:
      raise ValueError('Operation would create a cycle in the tree.')