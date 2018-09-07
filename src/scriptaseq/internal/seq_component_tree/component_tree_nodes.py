"""Defines a tree node type for a sequence component tree."""

from scriptaseq.named_tree_node import NamedTreeNode


class SequenceComponentNode(NamedTreeNode):
  """Class for nodes in a sequence component tree."""
  
  def __init__(self, name, parent=None, instanced_project_tree_node=None):
    """Constructor.
    Raises ValueError if the name is invalid or the node cannot be added to the specified parent.
    name -- Name for the new node.
    parent -- SequenceComponentNode reference indicating the parent to which the node will be attached as a child. The
      default value is None, meaning the node will initially have no parent.
    instanced_project_tree_node -- Reference to the project tree node that this node is instancing, or None if this node
      is not instancing a project tree node.
    """
    super().__init__(name, instanced_project_tree_node is None, parent)
    
    self._instanced_project_tree_node = instanced_project_tree_node
  
  @property
  def instanced_project_tree_node(self):
    """Property containing a reference to the project tree node that this node is instancing.
    A value of None means this node is not instancing a project tree node.
    """
    return self._instanced_project_tree_node
  
  @instanced_project_tree_node.setter
  def instanced_project_tree_node(self, instanced_project_tree_node):
    self._instanced_project_tree_node = instanced_project_tree_node
    self.can_have_children = instanced_project_tree_node is None