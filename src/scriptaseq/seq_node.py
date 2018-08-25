"""Functionality related to the Sequence Node abstraction"""

from sortedcontainers.sortedset import SortedSet

from scriptaseq.prop_binder import SCRIPT_PROP_TYPE
from scriptaseq.util.scripts import invoke_user_script
from sortedcontainers.sorteddict import SortedDict

class SeqNode:
  """Represents a node in the Sequence Node tree."""
  
  def __init__(self, name, prop_binders=[], tags=[], parent=None):
    """Constructor
    name -- Name for this SeqNode. Must be unique among this SeqNode's siblings, or a ValueError will be raised.
    prop_binders -- List of PropBinder objects containing the Property Binders owned by the node, if any.
    tags -- Iterable containing the initial tags for the node.
    parent -- Reference to parent node.
    """
    self._name = name
    self.prop_binders = prop_binders
    self.tags = SortedSet(tags)
    self.children = SortedDict()
    
    self.parent = parent
    if parent is not None:
      parent.add_child(self)
  
  @property
  def name(self):
    return self._name
  
  @name.setter
  def name(self, name):
    """Name setter.
    name -- Name for this SeqNode. Must be unique among this SeqNode's siblings, or a ValueError will be raised.
    """
    parent = self.parent
    if parent is None:
      self._name = name
    else:
      parent.remove_child(self._name)
      self._name = name
      parent.add_child(self)
  
  def remove_child(self, child_name):
    """Removes the specified child node from this SeqNode.
    If no child with the specified name is found, does nothing.
    child_name -- Name of the child to remove.
    """
    if child_name in self.children:
      child = self.children[child_name]
      child.parent = None
      del self.children[child_name]
  
  def add_child(self, child):
    """Adds the specified child node to this SeqNode.
    This SeqNode must not already contain a different child with the same name, or a ValueError will be raised.
    child -- The child SeqNode to add.
    """
    if child.name in self.children and self.children[child.name] is not child:
        raise ValueError("Node '{}' already has a child named '{}'.".format(self.name, child.name))
    
    # Remove the child from its previous parent.
    if child.parent is not None:
      child.parent.remove_child(child.name)
    
    # Attach the child.
    child.parent = self
    self.children[child.name] = child
  
  def root_ancestor(self):
    """Gets a reference to the node's root ancestor.
    Returns self if this node has no parent."""
    ancestor = self
    while ancestor.parent is not None:
      ancestor = ancestor.parent
    return ancestor
  
  def idx_in_parent(self):
    """Determines the numerical index at which this child node can be found in its parent.
    Returns None if this Sequence Node has no parent.
    """
    if self.parent is None:
      return None
    else:
      return self.parent.children.index(self.name)
  
  def child_at_idx(self, idx):
    """Finds the child at the specified numerical index in this Sequence Node's child ordering.
    idx -- Index to query.
    """
    return self.children.peekitem(idx)[1]
  
  def predict_child_idx(self, node):
    """Determines what the specified node's numerical child index would be if it were added as a child to this node.
    Raises ValueError if this node already has a different child with the same name as the specified node.
    node -- The prospective child node to be added.
    """
    # If the node is already a child of this node, just return what its index actually is.
    if node.parent is self:
      return node.idx_in_parent()
    
    if node.name in self.children:
      raise ValueError("Node '{}' already has a child named '{}'.".format(self.name, node.name))
    
    # TODO: This could probably be made more efficient.
    children_copy = self.children.copy()
    children_copy[node.name] = node
    return children_copy.index(node.name)
  
  def _find_prop_binders(self, prop_name, skip_scripts=False):
    """Finds all applicable Property Binders for the specified property for this node.
    Returns an iterable of the applicable PropBinders found. If applicable binders are found in multiple ancestor nodes,
    the ones found in the ancestors lowest in the tree are returned first. If multiple applicable binders are found in
    the same ancestor, those binders are ordered according to their order in the ancestor node's Property Binder list.
    prop_name -- Property name to query.
    skip_scripts -- If true, Property Binders of Script type will be skipped.
    """
    # Traverse the tree upwards looking for applicable binders.
    ancestor = self
    while ancestor is not None:
      for prop_binder in ancestor.prop_binders:
        if prop_binder.prop_name == prop_name and not (skip_scripts and prop_binder.prop_type == SCRIPT_PROP_TYPE) \
        and prop_binder.binds_to_node(self):
          yield prop_binder
      
      ancestor = ancestor.parent
  
  def find_prop_binder(self, prop_name, skip_scripts=False):
    """Finds the most applicable Property Binder for the specified property for this node.
    Returns None if no applicable Property Binders were found.
    prop_name -- Property name to query.
    skip_scripts -- If true, Property Binders of Script type will be ignored.
    """
    prop_binders = self.find_prop_binders(prop_name, skip_scripts)
    try:
      return prop_binders.next()
    except StopIteration:
      return None
  
  def _find_prop_vals(self, prop_name, skip_scripts=False, apply_gen_scripts=True):
    """Finds all applicable values for the specified property for this node.
    Similar to find_prop_binders, except the property values are returned rather than the PropBinders containing the
    values.
    Note: If apply_gen_scripts is true, this method can run user-supplied scripts, so the caller should generally be
    prepared to handle UserScriptErrors gracefully.
    prop_name -- Property name to query.
    skip_scripts -- If true, Property Binders of Script type will be skipped.
    apply_gen_scripts -- If true, Property Binders of Scripted Value type will have their generator scripts applied to
      generate the returned property value(s). Otherwise, the generator scripts will themselves be returned as the
      property value(s).
    """
    return map(lambda binder: binder.extract_val(apply_gen_scripts), self._find_prop_binders(prop_name, skip_scripts))
  
  def find_prop_val(self, prop_name, default=None, skip_scripts=False, apply_gen_scripts=True):
    """Finds the most applicable property value for the specified property for this node.
    Returns default if no applicable values were found.
    Note: If apply_gen_scripts is true, this method can run user-supplied scripts, so the caller should generally be
    prepared to handle UserScriptErrors gracefully.
    prop_name -- Property name to query.
    default -- Default value to return if no applicable values are found.
    skip_scripts -- If true, Property Binders of Script type will be ignored.
    apply_gen_scripts -- If apply_gen_scripts is true and the matching PropBinder is of Scripted Value type, the
      generator script will be applied to generate the returned property value. Otherwise, the generator script will
      itself be returned as the property value.
    """
    prop_vals = self.find_prop_vals(prop_name, skip_scripts, apply_gen_scripts)
    try:
      return prop_vals.next()
    except StopIteration:
      return default
  
  def call_prop_script(self, prop_name, *args, **kwargs):
    """Finds a bound script under the specified property name and invokes it.
    This method searches for the most applicable Property Binder with property type Script, and invokes it.
    Returns the return value of the script.
    Raises KeyError if no applicable script could be found under the specified property name.
    Note: This method can run user-supplied scripts, so the caller should generally be prepared to handle
    UserScriptErrors gracefully.
    prop_name -- Name of the property under which the script is defined.
    args -- Positional arguments to pass to the user-supplied script.
    kwargs -- Keyword arguments to pass to the user-supplied script.
    """
    script_binders = filter(lambda binder: binder.prop_type == SCRIPT_PROP_TYPE, self.find_prop_binders(prop_name))
    try:
      binder = script_binders.next()
      return invoke_user_script(binder.prop_val, *args, **kwargs)
        
    except StopIteration:
      raise KeyError('No bindable script found under property name \'{}\''.format(prop_name))