"""Defines tree node types for a sequence component tree."""

from PyQt5.Qt import QMenu, QCoreApplication
from sortedcontainers.sorteddict import SortedDict
from sortedcontainers.sortedset import SortedSet

from scriptaseq.internal.gui.undo_commands.seq_component_node import SetComponentTypeCommand
from scriptaseq.internal.gui.undo_commands.seq_component_tree import DeleteSequenceComponentTreeNodeCommand, \
  AddSequenceComponentTreeNodeCommand
from scriptaseq.internal.seq_component_tree.component_types import ContainerSequenceComponentType, \
  SUPPORTED_COMPONENT_TYPES
from scriptaseq.named_tree_node import NamedTreeNode


class CustomSequenceComponentPropValue:
  """Represents the value of a custom property attached to a sequence component tree node."""
  
  def __init__(self, value_str, is_expr=False):
    """Constructor.
    value_str -- Property value, as a string.
    is_expr -- Indicates whether value_str should be interpreted as a Python expression (True) or as a raw string
      (False).
    """
    self.value_str = value_str
    self.is_expr = is_expr

class BaseSequenceComponentNode(NamedTreeNode):
  """Base class for nodes in a sequence component tree."""
  
  def __init__(self, name, tree_owner):
    """Constructor.
    The constructed node initially has no parent.
    Raises ValueError if the name is invalid.
    name -- Name for the new node.
    tree_owner -- Reference to the project tree node that owns the sequence component tree to which this node will
      belong.
    """
    super().__init__(name, True)
    
    self.tree_owner = tree_owner
  
  @property
  def component_type(self):
    """Property containing the component type of this node, as a BaseSequenceComponentType subclass.
    By default, this property is read-only. Subclasses can make the property writable by overriding the setter (and
    should also override the getter in that case). Default implementation returns ContainerSequenceComponentType.
    """
    return ContainerSequenceComponentType
  
  @property
  def is_in_instance(self):
    """Read-only boolean property indicating whether this node is part of an instancing subtree.
    Default implementation always returns false. Subclasses that support instancing should override this.
    """
    return False
  
  @property
  def is_instance_root(self):
    """Read-only boolean property indicating whether this node is the root of an instancing subtree."""
    return self.is_in_instance() and (self.parent is None or not self.parent.is_in_instance())
  
  @property
  def instance_src(self):
    """Read-only property referencing the BaseSequenceComponentNode that this node is instancing.
    The value should be None if and only if is_in_instance is false. Default implementation always returns None.
    Subclasses that support instancing should override this.
    """
    return None
  
  @property
  def custom_prop_names(self):
    """Read-only property containing a SortedSet-like sequence of custom property names attached to this node.
    Default implementation returns an empty SortedSet. Subclasses should override this.
    The returned object may or may not automatically update when new custom properties are added. The caller should
    generally avoid modifying the returned object directly.
    """
    return SortedSet()
  
  def get_custom_prop(self, name):
    """Gets the value of a custom property, as a CustomSequenceComponentPropValue object.
    Raises KeyError if no custom property with the specified name is present.
    Default implementation always raises KeyError. Subclasses should override this.
    name -- Name of the custom property to get.
    """
    raise KeyError(
      QCoreApplication.translate('BaseSequenceComponentNode', "Custom property '{}' not found.").format(name))
  
  def set_custom_prop(self, name, value):
    """Sets the value of a custom property, creating the property if it does not exist.
    Default implementation raises NotImplementedError. Subclasses should override this.
    name -- Name of the custom property to set.
    value -- CustomSequenceComponentPropValue object containing the value.
    """
    raise NotImplementedError()
  
  def del_custom_prop(self, name):
    """Deletes a custom property mapping.
    Raises KeyError if no custom property with the specified name is present.
    Default implementation always raises KeyError. Subclasses should override this.
    name -- Name of the custom property to delete.
    """
    raise KeyError(
      QCoreApplication.translate('BaseSequenceComponentNode', "Custom property '{}' not found.").format(name))
  
  def make_context_menu(self, undo_stack, seq_component_tree_controller, seq_component_node_controller, parent=None):
    """Creates a context menu for this node.
    Default implementation returns an empty menu. Subclasses that support context menu operations should override this.
    undo_stack -- QUndoStack that should receive undoable editing commands generated by the menu.
    seq_component_tree_controller -- SequenceComponentTreeController in charge of high-level changes to the sequence
      component tree.
    seq_component_node_controller -- SequenceComponentNodeController in charge of changes to individual nodes in the
      sequence component tree.
    parent -- Parent QObject for the context menu.
    """
    return QMenu(parent)
  
  def verify_can_add_as_child(self, node):
    super().verify_can_add_as_child(node)
    
    if node.tree_owner is not self.tree_owner:
      raise ValueError(
        QCoreApplication.translate('BaseSequenceComponentNode', 'Cannot mix nodes belonging to different sequence component trees.'))

class NonInstancedSequenceComponentNode(BaseSequenceComponentNode):
  """Class for sequence component tree nodes that do not instance other nodes."""
  
  def __init__(self, name, tree_owner, component_type=ContainerSequenceComponentType):
    """Constructor.
    The constructed node initially has no parent.
    Raises ValueError if the name is invalid.
    name -- Name for the new node.
    tree_owner -- Reference to the project tree node that owns the sequence component tree to which this node will
      belong.
    component_type -- BaseSequenceComponentType subclass indicating the type of component.
    """
    super().__init__(name, tree_owner)
    self._component_type = component_type
    self._custom_props = SortedDict()
  
  @property
  def component_type(self):
    return self._component_type
  
  @component_type.setter
  def component_type(self, component_type):
    self._component_type = component_type
  
  @property
  def custom_prop_names(self):
    return self._custom_props.keys()
  
  def get_custom_prop(self, name):
    return self._custom_props[name]
  
  def set_custom_prop(self, name, value):
    self._custom_props[name] = value
  
  def del_custom_prop(self, name):
    del self._custom_props[name]
  
  def make_context_menu(self, undo_stack, seq_component_tree_controller, seq_component_node_controller, parent=None):
    menu = super().make_context_menu(undo_stack, seq_component_tree_controller, seq_component_node_controller, parent)

    # Add menu items for changing the component type, if that is allowed.
    change_type_menu = menu.addMenu(QCoreApplication.translate('NonInstancedSequenceComponentNode', 'Change &Type'))
    def change_type_func_maker(new_component_type):
      def change_type_func():
        undo_stack.push(SetComponentTypeCommand(seq_component_node_controller, self, new_component_type))
      return change_type_func
    for component_type in SUPPORTED_COMPONENT_TYPES:
      change_type_action = change_type_menu.addAction(component_type.get_icon(), component_type.menu_text)
      change_type_action.setEnabled(component_type != self.component_type)
      change_type_action.triggered.connect(change_type_func_maker(component_type))
    
    # Add menu items for creating child nodes, if creating children is allowed.
    if self.can_have_children:
      add_menu = menu.addMenu(QCoreApplication.translate('NonInstancedSequenceComponentNode', '&Create Child'))
      def add_func_maker(component_type):
        def add_func():
          new_node = NonInstancedSequenceComponentNode(self.suggest_child_name(component_type.node_default_name),
            component_type=component_type, tree_owner=self.tree_owner)
          undo_stack.push(AddSequenceComponentTreeNodeCommand(seq_component_tree_controller, new_node, self))
        return add_func
      for component_type in SUPPORTED_COMPONENT_TYPES:
        add_action = add_menu.addAction(component_type.get_icon(), component_type.menu_text)
        add_action.triggered.connect(add_func_maker(component_type))
    
    # Add a menu item for deleting the node, if it can be deleted.
    if self.parent is not None:
      def delete_func():
        undo_stack.push(DeleteSequenceComponentTreeNodeCommand(seq_component_tree_controller, self))
      delete_action = menu.addAction(QCoreApplication.translate('NonInstancedSequenceComponentNode', '&Delete'))
      delete_action.triggered.connect(delete_func)
    
    return menu