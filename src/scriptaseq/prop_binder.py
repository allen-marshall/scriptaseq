"""Functionality related to Property Binders"""

import copy
from sortedcontainers.sortedset import SortedSet

from scriptaseq.util.scripts import invoke_user_script

class PropType:
  """Represents a type that a property binder's value is expected to have.
  PropTypes are used to determine what type of GUI to show when editing a property value.
  """
  def __init__(self, name, def_val, conversion_func, uses_scripted_val=False):
    """Constructor
    WARNING: If uses_scripted_val is true, any string passed as the def_val parameter will likely be executed as a
    Python script at some point. Avoid passing untrusted code in def_val when uses_scripted_val is true.
    name -- User-displayable name for this property value type.
    def_val -- Default stored value for properties of this type. If uses_scripted_val is true, this should be a script
      that constructs the value rather than the value itself.
    conversion_func -- A function that attempts to convert a property value of another PropType to this type. Takes two
      arguments containing the property value and the old PropType, respectively, and returns the converted value.
      Should raise ValueError if the value cannot be converted.
    uses_scripted_val -- Indicates whether properties of this type should store the value indirectly as a value
      construction script, or directly as a value object (the default).
    """
    self.name = name
    self.def_val = def_val
    self.uses_scripted_val = uses_scripted_val
    self._conversion_func = conversion_func
  
  def convert(self, prop_val, old_prop_type):
    """Attempts to convert a property value to a different property type.
    Returns the converted value. If the value cannot be converted, returns a copy of this PropType's default value.
    Note: If old_prop_type.uses_scripted_val is true and self.uses_scripted_val is false, this function may run
    user-supplied scripts, so the caller should generally be prepared to handle UserScriptErrors gracefully.
    prop_val -- Property value to convert.
    old_prop_type -- The previous PropType that prop_val belonged to.
    """
    # When converting from a scripted value type to a non-scripted value type, execute the generator script to get the
    # non-scripted value before performing the conversion.
    if old_prop_type.uses_scripted_val and not self.uses_scripted_val:
      prop_val = invoke_user_script(prop_val)
    
    # Try to convert the value.
    try:
      return self._conversion_func(prop_val, old_prop_type)
    
    # If conversion failed, return a copy of the new PropType's default value instead.
    except ValueError:
      return copy.deepcopy(self.def_val)

def _string_conversion_func(prop_val, old_prop_type):
  """PropType conversion function that simply converts the old property value to a string.
  prop_val -- Property value to convert.
  old_prop_type -- The previous PropType that prop_val belonged to. (Not used in this implementation.)"""
  return str(prop_val)

# PropType for string properties.
STRING_PROP_TYPE = PropType('String', '', _string_conversion_func)

# PropType for values that are to be generated by a script.
SCRIPTED_VAL_PROP_TYPE = PropType('Scripted Value', 'script = lambda: None', True, _string_conversion_func)

# PropType for scripts (not to be confused with scripted values).
SCRIPT_PROP_TYPE = PropType('Script', '', _string_conversion_func)

# List of PropTypes supported by ScriptASeq.
SUPPORTED_PROP_TYPES = [STRING_PROP_TYPE, SCRIPTED_VAL_PROP_TYPE, SCRIPT_PROP_TYPE]

class PropBindCriterion:
  """Represents a criterion which must be satisfied for a Property Binder to bind to a Sequence Node.
  The criterion is based on a set of tags stored in Sequence Nodes. In order for a Property Binder to be bindable to a
  node, the node must have all of the tags specified in the Property Binder's PropBindCriterion.
  """
  def __init__(self, bind_tags=[]):
    """Constructor
    bind_tags -- Iterable containing the tags that a Sequence Node must have in order to be bound by this binding
      criterion.
    """
    self.bind_tags = SortedSet(bind_tags)
  
  def criterion_satisfied(self, node):
    """Checks if a Sequence Node meets this binding criterion.
    The criterion is met if and only if every tag in self.bind_tags has a matching tag in the Sequence Node's tag set.
    node -- The Sequence Node to check.
    """
    def tag_check(tag):
      return tag in node.tags
    return all(map(tag_check, self.bind_tags))

class PropBinder:
  """Represents a Property Binder that can be attached to a Sequence Node.
  A Property Binder contains a property name and value, along with a tag-based binding criterion that determines to
  which nodes the property name/value pair will be applied."""
  
  def __init__(self, prop_name, prop_type, use_def_val=True, prop_val=None, bind_criterion=PropBindCriterion()):
    """Constructor
    WARNING: If prop_type.uses_scripted_val is true, any string passed as the prop_val parameter will likely be executed
    as a Python script at some point. Avoid passing untrusted code in prop_val when prop_type.uses_scripted_val is true.
    prop_name -- Name of the property.
    prop_type -- PropType object indicating what type the property value is expected to have. This is meant to inform
      the GUI of what type of widget(s) to use for editing the property value.
    use_def_val -- Indicates whether to use the default value for the PropType as the initial value, or to use the
      prop_val parameter as the initial value.
    prop_val -- Initial value for the property, or value construction script if prop_type.uses_scripted_val is true.
      Ignored if use_def_val is true.
    bind_criterion -- Binding criterion to determine to which nodes the property name/value pair will be applied.
    """
    self.prop_name = prop_name
    self._prop_type = prop_type
    self.bind_criterion = bind_criterion
    self.prop_val = prop_val if not use_def_val else copy.deepcopy(prop_type.def_val)
  
  @property
  def prop_type(self):
    """PropType object indicating what type the property value is expected to have.
    This is meant to inform the GUI of what type of widget(s) to use for editing the property value. Note that setting
    this property may cause the property value to be changed or reset to the default value for the new PropType,
    depending on whether the previous value can be successfully converted to the new type.
    """
    return self._prop_type
  
  @prop_type.setter
  def prop_type(self, prop_type):
    self.prop_val = prop_type.convert(self.prop_val, self._prop_type)
    self._prop_type = prop_type
  
  def extract_val(self, apply_gen_scripts=True):
    """Extracts the value stored in the Property Binder.
    Note: If apply_gen_scripts is true, this method can run user-supplied scripts, so the caller should generally be
    prepared to handle UserScriptErrors gracefully.
    apply_gen_scripts -- If apply_gen_scripts is true and this PropBinder is of a scripted value type, the generator
      script will be applied to generate the returned property value. Otherwise, the generator script will itself be
      returned as the property value.
    """
    if apply_gen_scripts and self.prop_type.uses_scripted_val:
      return invoke_user_script(self.prop_val)
    else:
      return self.prop_val
  
  def binds_to_node(self, node):
    """Checks if this Property Binder can bind to the specified node.
    node -- The node to check. This is assumed to be either the same node as the node that owns this PropBinder, or a
      descendant of that node. For efficiency, this assumption is not checked, and the returned result may be incorrect
      if it does not hold.
    """
    return self.bind_criterion.criterion_satisfied(node)