"""Functionality related to project modeling from a GUI perspective"""
from PyQt5.Qt import pyqtProperty, pyqtSignal, QObject

from scriptaseq.seq_node import SeqNode

# TODO: Need to figure out how to robustly handle the signals in the presence of multiple changes occurring in the same
# iteration of the Qt main loop.

class ProjectModel(QObject):
  """Project wrapper model that adds functionality such as signals to keep the GUI up to date, etc."""
  
  # Emitted when the project is swapped out or reloaded as a whole.
  # Args:
  # - The new root SeqNode.
  project_reloaded = pyqtSignal(SeqNode)
  
  # Emitted when a Sequence Node's name is changed.
  # Args:
  # - The modified SeqNode.
  # - The previous name.
  node_name_changed = pyqtSignal(SeqNode, str)
  
  # Emitted when a new Sequence Node has been added.
  # Args:
  # - The newly added SeqNode.
  node_added = pyqtSignal(SeqNode)
  
  # Emitted when an existing Sequence Node has been removed.
  # Args:
  # - The removed SeqNode.
  # - The former parent of the removed SeqNode.
  node_removed = pyqtSignal(SeqNode, SeqNode)
  
  # Emitted when a Property Binder in a Sequence Node has been added, removed, or modified.
  # Args:
  # - The SeqNode to which the Property Binder is or was directly attached.
  # - The name of the property associated with the Property Binder.
  node_prop_binder_changed = pyqtSignal(SeqNode, str)
  
  def __init__(self, root_node):
    """Constructor
    root_node -- Root Sequence Node for the project.
    """
    super().__init__()
    
    self._root_node = root_node
  
  @pyqtProperty(SeqNode)
  def root_node(self):
    """Property containing the root Sequence Node for the project.
    Assigning to this property is regarded as a project reload.
    """
    return self._root_node
  
  @root_node.setter
  def root_node(self, root_node):
    self._root_node = root_node
    self.project_reloaded.emit(root_node)
  
  def set_node_name(self, node, name):
    """Sets the name for the specified node, and emits any appropriate signals.
    node -- The Sequence Node to change.
    name -- The new name. node's parent must not already have another child with the specified name, or a ValueError
      will be raised.
    """
    old_name = node.name
    node.name = name
    self.node_name_changed.emit(node, old_name)
  
  def add_node(self, parent, child):
    """Adds the specified child node to the specified parent node.
    The parent node must not already contain a different child with the same name, or a ValueError will be raised.
    parent -- The parent node.
    child -- The child node to add.
    """
    if child.parent is not parent:
      # If the child already has another parent, treat the operation as a removal followed by an insertion.
      if child.parent is not None:
        self.child_removed.emit(child, child.parent)
      
      parent.add_child(child)
      self.child_added.emit(child)
  
  def remove_node(self, node):
    """Removes the specified child node from its parent.
    This effectively deletes the child node from the project.
    child -- The child node to remove.
    """
    if node.parent is not None:
      old_parent = node.parent
      old_parent.remove_child(node.name)
      self.child_removed.emit(node, old_parent)
  
  def add_prop_binder(self, node, prop_binder, index=None):
    """Adds a new Property Binder to a Sequence Node.
    node -- The Sequence Node to which the new Property Binder will be directly attached.
    prop_binder -- The Property Binder to add.
    index -- The desired index in the Sequence Node's Property Binder list. Default is None, which places the Property
      Binder at the end of the list.
    """
    if index is None:
      index = len(node.prop_binders)
    node.prop_binders.insert(index, prop_binder)
    self.node_prop_binder_changed.emit(node, prop_binder.prop_name)
  
  def remove_prop_binder(self, node, index):
    """Removes an existing Property Binder from a Sequence Node.
    node -- The Sequence Node to which the Property Binder is directly attached.
    index -- Index of the Property Binder to remove, within the Sequence Node's Property Binder list.
    """
    prop_binder = node.prop_binders[index]
    del node.prop_binders[index]
    self.node_prop_binder_changed.emit(node, prop_binder.prop_name)
  
  def set_prop_binder_prop_name(self, node, prop_name, index):
    """Sets the property name for a Property Binder.
    node -- The Sequence Node to which the Property Binder is directly attached.
    prop_name -- The new property name for the Property Binder.
    index -- Index of the Property Binder to change, within the Sequence Node's Property Binder list.
    """
    prop_binder = node.prop_binders[index]
    old_prop_name = prop_binder.prop_name
    if old_prop_name != prop_name:
      prop_binder.prop_name = prop_name
      # The change may affect bound property values for both the old and new property names, so emit signals for both.
      self.node_prop_binder_changed.emit(node, old_prop_name)
      self.node_prop_binder_changed.emit(node, prop_name)
  
  def set_prop_binder_prop_type(self, node, prop_type, index):
    """Sets the property type for a Property Binder.
    node -- The Sequence Node to which the Property Binder is directly attached.
    prop_type -- The new PropType for the Property Binder.
    index -- Index of the Property Binder to change, within the Sequence Node's Property Binder list.
    """
    prop_binder = node.prop_binders[index]
    old_prop_type = prop_binder.prop_type
    if old_prop_type != prop_type:
      prop_binder.prop_type = prop_type
      self.node_prop_binder_changed.emit(node, prop_binder.prop_name)
  
  def set_prop_binder_prop_val(self, node, prop_val, index):
    """Sets the property value for a Property Binder.
    node -- The Sequence Node to which the Property Binder is directly attached.
    prop_val -- The new property value for the Property Binder.
    index -- Index of the Property Binder to change, within the Sequence Node's Property Binder list.
    """
    prop_binder = node.prop_binders[index]
    prop_binder.prop_val = prop_val
    self.node_prop_binder_changed.emit(node, prop_binder.prop_name)
  
  def set_prop_binder_bind_script(self, node, bind_script, index):
    """Sets the binding script for a Property Binder.
    node -- The Sequence Node to which the Property Binder is directly attached.
    bind_script -- The new binding script for the Property Binder.
    index -- Index of the Property Binder to change, within the Sequence Node's Property Binder list.
    """
    prop_binder = node.prop_binders[index]
    prop_binder.bind_script = bind_script
    self.node_prop_binder_changed.emit(node, prop_binder.prop_name)