"""Functionality related to the Sequence Node abstraction"""
from scriptaseq.geom import LineSeg

# Default inheritance script for inheritable attachments. This script causes the attachment to apply only to the node
# that has it directly attached.
DEFAULT_INHERITANCE_SCRIPT = 'inherit = ancestor is descendant'

class InheritableAttachment:
  """Base class for information that can be attached to a Sequence Node, and potentially inherited by other nodes."""
  
  def __init__(self, inheritance_script=DEFAULT_INHERITANCE_SCRIPT):
    """Constructor
    WARNING: Any string passed as the inheritance_script parameter will likely be executed as a Python script at some
    point. Avoid passing untrusted code in inheritance_script.
    inheritance_script -- Script to be used for determining to which nodes the attachment applies.
    """
    self.inheritance_script = inheritance_script
  
  def check_inheritance(self, ancestor, descendant):
    """Checks if this attachment should be inherited by the specified descendant.
    Note: This method can run user-supplied scripts, so the caller should generally be prepared to handle all exceptions
    gracefully.
    Returns true if the descendant should inherit the attachment, false otherwise.
    ancestor -- The Sequence Node that directly contains the attachment.
    descendant -- The Sequence Node for which inheritance of the attachment is to be queried. Must be either the same
      node as ancestor, or a descendant of ancestor.
    """
    env = {'ancestor' : ancestor, 'descendant' : descendant, 'inherit' : False}
    exec(self.inheritance_script, env)
    return env['inherit']

class DataAttachment(InheritableAttachment):
  """Represents nearly-arbitrary string data attached to a Sequence Node.
  The meaning of a data attachment usually depends on user-defined scripts.
  """
  
  def __init__(self, name, value, inheritance_script=DEFAULT_INHERITANCE_SCRIPT):
    """Constructor
    WARNING: See superclass warning about passing untrusted code in inheritance_script.
    name -- Name of the attachment, as a string. Note that multiple attachments on the same Sequence Node can have the
      same name.
    value -- Data stored in the attachment, as a string.
    inheritance_script -- See superclass.
    """
    super().__init__(inheritance_script)
    self.name = name
    self.value = value

class ScriptAttachment(InheritableAttachment):
  """Represents a user-defined script attached to a Sequence Node."""
  
  def __init__(self, role='', script='', inheritance_script=DEFAULT_INHERITANCE_SCRIPT):
    """Constructor
    WARNING: Any string passed as the script or inheritance_script parameter will likely be executed as a Python script
    at some point. Avoid passing untrusted code in script and inheritance_script.
    role -- String identifying the 'role' of the script, which determines when it gets called.
    script -- Script to be called when the attachment's role is triggered.
    inheritance_script -- See superclass.
    """
    super().__init__(inheritance_script)
    self.role = role
    self.script = script
  
  def call_script(self, node, root=None, env={}):
    """Calls the script for the specified Sequence Node.
    node -- Current Sequence Node to pass to the script.
    root -- Reference to the root Sequence Node. Can be passed as an argument for efficiency. If this is None, the root
      will be found by traversing the tree upward from the current Sequence Node.
    env -- Extra environment information to pass to the script. Keys are variable names; values are variable values. If
      the script modifies any variables named here, the passed dictionary will be modified to reflect those changes.
      This can be used to extract return values from scripts when necessary.
    """
    if root is None:
      root = node.root_ancestor()
    
    # Add standard parameters, overwriting them if they were included in env.
    env['node'] = node
    env['root'] = root
    
    # Call the script.
    exec(self.script, env)

class SeqNode:
  """Represents a node in the Sequence Node tree."""
  
  def __init__(self, name, subspace, line_seg=LineSeg(), data_attach=[], script_attach=[], parent=None):
    """Constructor
    name -- Name for this SeqNode. Must be unique among this SeqNode's siblings.
    subspace -- SubspaceSettings object indicating the behavior of the node's subspace.
    line_seg -- LineSeg object indicating the node's positioning inside its parent's subspace.
    data_attach -- List of DataAttachment objects containing the node's data attachments, if any.
    script_attach -- List of ScriptAttachment objects containing the node's script attachments, if any.
    parent -- Reference to parent node.
    """
    self._name = name
    self.subspace = subspace
    self.line_seg = line_seg
    self.data_attach = data_attach
    self.script_attach = script_attach
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
  
  def clipped_child_names(self, boundary):
    """Gets the names of child nodes that would be clipped if the Sequence Node's boundary were changed as specified.
    boundary -- The new boundary rectangle.
    """
    for name, child in self.children.items():
      if not child.line_seg.is_in_rect(boundary):
        yield name
  
  def sorted_children(self, key=lambda child : child.line_seg.start_x):
    """Returns a list of this node's direct children in sorted order.
    By default, sorting is based on the child's starting horizontal position, which normally corresponds to start time.
    key -- The sorting key to use.
    """
    children = list(self.children.values())
    children.sort(key=key)
    return children
  
  def root_ancestor(self):
    """Gets a reference to the node's root ancestor.
    Returns self if this node has no parent."""
    root = self
    while root.parent is not None:
      root = root.parent
    
    return root
  
  def find_data_attachments(self, attach_name):
    """Finds the values stored in data attachments with the specified name.
    Returns an iterable of the values found. If matching attachments are inherited from multiple nodes, the values that
    the node inherits from itself are returned first, followed by the values inherited from the parent, and so on. If
    multiple matching attachments are inherited from the same node, those attachments are ordered according to their
    order in the ancestor's data attachment list.
    Note: This method can run user-supplied scripts, so the caller should generally be prepared to handle all exceptions
    gracefully.
    attach_name -- Data attachment name/key to be queried.
    """
    # Traverse the tree upwards looking for matches.
    ancestor = self
    while ancestor is not None:
      for attachment in self.data_attach:
        if attachment.name == attach_name and attachment.check_inheritance(ancestor, self):
          yield attachment.value
      
      ancestor = ancestor.parent
  
  def find_first_data_attachment(self, attach_name):
    """Similar to find_data_attachments, but only returns the first attachment value found.
    Note: This method can run user-supplied scripts, so the caller should generally be prepared to handle all exceptions
    gracefully.
    attach_name -- Data attachment name/key to be queried.
    """
    attachments = self.find_data_attachments(attach_name)
    try:
      return attachments.next()
    except StopIteration:
      return None
  
  def call_script(self, role, root=None, env={}):
    """Invokes the node's script attachment with the specified role, if one is found.
    Only the first matching script attachment found is invoked. The order of searching is similar to that in
    find_data_attachments.
    Note: This method can run user-supplied scripts, so the caller should generally be prepared to handle all exceptions
    gracefully.
    role -- String identifying the script role to invoke.
    root -- Reference to the root Sequence Node. Can be passed as an argument for efficiency. If this is None, the root
      will be found by traversing the tree upward from the current Sequence Node.
    env -- Extra environment information to pass to the script. Keys are variable names; values are variable values. If
      the script modifies any variables named here, the passed dictionary will be modified to reflect those changes.
      This can be used to extract return values from scripts when necessary.
    """
    # TODO: Maybe try to reduce code duplication between find_data_attachments and call_script.
    # Traverse the tree upwards looking for matches.
    ancestor = self
    while ancestor is not None:
      for attachment in self.script_attach:
        if attachment.role == role and attachment.check_inheritance(ancestor, self):
          attachment.call_script(self, root, env)
          # Stop after we have invoked the first matching script.
          return
      
      ancestor = ancestor.parent