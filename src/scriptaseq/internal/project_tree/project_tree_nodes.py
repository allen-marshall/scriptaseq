"""Defines tree node types for the project tree."""

from scriptaseq.named_tree_node import NamedTreeNode
from PyQt5.Qt import QIcon
from scriptaseq.internal.gui.qt_util import make_multires_icon

class BaseProjectTreeNode(NamedTreeNode):
  """Base class for nodes in the project tree."""
  
  @classmethod
  def make_icon(cls):
    """Makes a QIcon representing nodes of this class.
    Subclasses should override this. Default implementation returns an empty QIcon.
    """
    return QIcon()

class DirProjectTreeNode(BaseProjectTreeNode):
  """Class for project tree nodes that represent directories inside the project."""
  
  def __init__(self, name, parent=None):
    """Constructor.
    Raises ValueError if the name is invalid or the node cannot be added to the specified parent.
    name -- Name for the new node.
    parent -- BaseProjectTreeNode reference indicating the parent to which the node will be attached as a child. The
      default value is None, meaning the node will initially have no parent.
    """
    super().__init__(name, True, parent)
  
  @classmethod
  def make_icon(cls):
    return make_multires_icon(':/icons/project_tree/dir')

class SequenceProjectTreeNode(BaseProjectTreeNode):
  """Class for project tree nodes that represent Sequences."""
  
  def __init__(self, name, parent=None):
    """Constructor.
    Raises ValueError if the name is invalid or the node cannot be added to the specified parent.
    name -- Name for the new node.
    parent -- BaseProjectTreeNode reference indicating the parent to which the node will be attached as a child. The
      default value is None, meaning the node will initially have no parent.
    """
    super().__init__(name, False, parent)
  
  @classmethod
  def make_icon(cls):
    return make_multires_icon(':/icons/project_tree/sequence')