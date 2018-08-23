"""Functionality related to the Sequence Node abstraction"""

from scriptaseq.prop_binder import SCRIPT_PROP_TYPE

class SeqNode:
  """Represents a node in the Sequence Node tree."""
  
  def __init__(self, name, prop_binders=[], parent=None):
    """Constructor
    name -- Name for this SeqNode. Must be unique among this SeqNode's siblings.
    prop_binders -- List of PropBinder objects containing the node's Property Binders, if any.
    parent -- Reference to parent node.
    """
    self._name = name
    self.prop_binders = prop_binders
    self.children = {}
    
    self.parent = parent
    if parent is not None:
      parent.add_child(self)
  
  @property
  def name(self):
    return self._name
  
  @name.setter
  def name(self, name):
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
    This SeqNode must not already contain a different child with the same name.
    child -- The child SeqNode to add.
    """
    if child.name in self.children:
      if self.children[child.name] is not child:
        raise ValueError("Node '{}' already has a child named '{}'.".format(self.name, child.name))
      
      # If we already have the specified node as a child, don't do anything else.
      else:
        return
    
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
  
  def find_prop_binders(self, prop_name, skip_scripts=False):
    """Finds all applicable Property Binders for the specified property for this node.
    Returns an iterable of the applicable PropBinders found. If applicable binders are found in multiple ancestor nodes,
    the ones found in the ancestors lowest in the tree are returned first. If multiple applicable binders are found in
    the same ancestor, those values are ordered according to their order in the ancestor node's Property Binder list.
    Note: This method can run user-supplied scripts, so the caller should generally be prepared to handle all exceptions
    gracefully.
    prop_name -- Property name to query.
    skip_scripts -- If true, Property Binders of script type will be skipped.
    """
    # Traverse the tree upwards looking for applicable binders.
    ancestor = self
    while ancestor is not None:
      for prop_binder in ancestor.prop_binders:
        if prop_binder.prop_name == prop_name and not (skip_scripts and prop_binder.prop_type == SCRIPT_PROP_TYPE) \
        and prop_binder.applies_to_descendant(ancestor, self):
          yield prop_binder
      
      ancestor = ancestor.parent
  
  def find_prop_vals(self, prop_name, skip_scripts=False):
    """Finds all applicable values for the specified property for this node.
    Similar to find_prop_binders, except the property values are returned rather than the PropBinders containing the
    values.
    Note: This method can run user-supplied scripts, so the caller should generally be prepared to handle all exceptions
    gracefully.
    prop_name -- Property name to query.
    skip_scripts -- If true, Property Binders of script type will be skipped.
    """
    return map(lambda binder: binder.prop_value, self._find_prop_binders(prop_name, skip_scripts))
  
  def find_first_prop_val(self, prop_name, skip_scripts=False):
    """Similar to find_prop_vals, but only returns the first applicable value found.
    Returns None if no applicable values were found.
    Note: This method can run user-supplied scripts, so the caller should generally be prepared to handle all exceptions
    gracefully.
    prop_name -- Property name to query.
    skip_scripts -- If true, Property Binders of script type will be ignored.
    """
    prop_vals = self.find_prop_vals(prop_name, skip_scripts)
    try:
      return prop_vals.next()
    except StopIteration:
      return None
  
  def call_prop_script(self, prop_name, env={}):
    """Finds a bound script under the specified property name and invokes it.
    This method searches for applicable Property Binders with property type Script, and invokes the first one it finds.
    The order of searching is similar to that in find_prop_binders. This method does not raise an error if no
    appropriate script is found.
    Note: This method can run user-supplied scripts, so the caller should generally be prepared to handle all exceptions
    gracefully.
    prop_name -- Name of the property under which the script is defined.
    env -- Extra environment information to pass to the script. Keys are variable names; values are variable values. If
      the script modifies any variables named here, the passed dictionary will be modified to reflect those changes.
      This can be used to extract return values from scripts when necessary.
    """
    script_binders = filter(lambda binder: binder.prop_type == SCRIPT_PROP_TYPE, self.find_prop_binders(prop_name))
    try:
      exec(script_binders.next().prop_val, env)
    except StopIteration:
      pass