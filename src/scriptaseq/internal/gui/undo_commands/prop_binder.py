"""Undo commands that alter Property Binders."""

from PyQt5.Qt import QUndoCommand

from scriptaseq.internal.gui.undo_commands.id_gen import gen_undo_id


class AddPropBinderCommand(QUndoCommand):
  """Undo command for adding a Property Binder to a Sequence Node"""
  
  _undo_id = gen_undo_id()
  
  def __init__(self, node_props_model, node, binder_idx, binder, parent=None):
    """Constructor
    node_props_model -- PropBindersTableModel in charge of changes to Property Binders.
    node -- The Sequence Node to which the Property Binder will be directly attached.
    binder_idx -- Index at which to insert the Property Binder, within the Sequence Node's Property Binder list.
    binder -- Property Binder to add.
    parent -- Parent QUndoCommand.
    """
    super().__init__(parent)
    
    self._node_props_model = node_props_model
    self._node = node
    self._binder_idx = binder_idx
    self._binder = binder
    
    self.setText("Add Property Binder (Node '{}', Idx {})".format(node.name, str(binder_idx)))
  
  def id(self):
    return self.__class__._undo_id
  
  def redo(self):
    self._node_props_model.add_prop_binder(self._node, self._binder_idx, self._binder)
  
  def undo(self):
    self._node_props_model.remove_prop_binder(self._node, self._binder_idx)

class RemovePropBinderCommand(QUndoCommand):
  """Undo command for removing a Property Binder from a Sequence Node"""
  
  _undo_id = gen_undo_id()
  
  def __init__(self, node_props_model, node, binder_idx, parent=None):
    """Constructor
    node_props_model -- PropBindersTableModel in charge of changes to Property Binders.
    node -- The Sequence Node to which the Property Binder is directly attached.
    binder_idx -- Index of the Property Binder to remove, within the Sequence Node's Property Binder list.
    parent -- Parent QUndoCommand.
    """
    super().__init__(parent)
    
    self._node_props_model = node_props_model
    self._node = node
    self._binder_idx = binder_idx
    
    # Store a reference to the binder so we can re-add it if the command is undone.
    self._binder = node.prop_binders[binder_idx]
    
    self.setText("Remove Property Binder (Node '{}', Idx {})".format(node.name, str(binder_idx)))
  
  def id(self):
    return self.__class__._undo_id
  
  def redo(self):
    self._node_props_model.remove_prop_binder(self._node, self._binder_idx)
  
  def undo(self):
    self._node_props_model.add_prop_binder(self._node, self._binder_idx, self._binder)

class SetPropBinderNameCommand(QUndoCommand):
  """Undo command for modifying the property name in a Property Binder"""
  
  _undo_id = gen_undo_id()
  
  def __init__(self, node_props_model, node, binder_idx, prop_name, parent=None):
    """Constructor
    node_props_model -- PropBindersTableModel in charge of changes to Property Binders.
    node -- The Sequence Node to which the Property Binder is directly attached.
    binder_idx -- Index of the Property Binder to change, within the Sequence Node's Property Binder list.
    prop_name -- The new property name for the Property Binder.
    parent -- Parent QUndoCommand.
    """
    super().__init__(parent)
    
    self._node_props_model = node_props_model
    self._node = node
    self._binder_idx = binder_idx
    self._new_prop_name = prop_name
    self._old_prop_name = node.prop_binders[binder_idx].prop_name
    
    self.setText("Change Property Name (Node '{}', Idx {})".format(node.name, str(binder_idx)))
    
    self.setObsolete(self._old_prop_name == self._new_prop_name)
  
  def id(self):
    return self.__class__._undo_id
  
  def redo(self):
    self._node_props_model.set_prop_name(self._node, self._binder_idx, self._new_prop_name)
  
  def undo(self):
    self._node_props_model.set_prop_name(self._node, self._binder_idx, self._old_prop_name)

class SetPropBinderTypeCommand(QUndoCommand):
  """Undo command for modifying the property type in a Property Binder"""
  
  _undo_id = gen_undo_id()
  
  def __init__(self, node_props_model, node, binder_idx, prop_type, parent=None):
    """Constructor
    node_props_model -- PropBindersTableModel in charge of changes to Property Binders.
    node -- The Sequence Node to which the Property Binder is directly attached.
    binder_idx -- Index of the Property Binder to change, within the Sequence Node's Property Binder list.
    prop_type -- The new property type for the Property Binder.
    parent -- Parent QUndoCommand.
    """
    super().__init__(parent)
    
    self._node_props_model = node_props_model
    self._node = node
    self._binder_idx = binder_idx
    self._new_prop_type = prop_type
    self._old_prop_type = node.prop_binders[binder_idx].prop_type
    
    # Changing the property type can also change the property value, so we need to store the old value.
    self._old_prop_val = node.prop_binders[binder_idx].prop_val
    
    self.setText("Change Property Type (Node '{}', Idx {})".format(node.name, str(binder_idx)))
    
    self.setObsolete(self._old_prop_type == self._new_prop_type)
  
  def id(self):
    return self.__class__._undo_id
  
  def redo(self):
    self._node_props_model.set_prop_type(self._node, self._binder_idx, self._new_prop_type)
  
  def undo(self):
    self._node_props_model.set_prop_type(self._node, self._binder_idx, self._old_prop_type)
    self._node_props_model.set_prop_val(self._node, self._binder_idx, self._old_prop_val)

class SetPropBinderFilterCommand(QUndoCommand):
  """Undo command for modifying the binding filter in a Property Binder"""
  
  _undo_id = gen_undo_id()
  
  def __init__(self, node_props_model, node, binder_idx, bind_filter, parent=None):
    """Constructor
    node_props_model -- PropBindersTableModel in charge of changes to Property Binders.
    node -- The Sequence Node to which the Property Binder is directly attached.
    binder_idx -- Index of the Property Binder to change, within the Sequence Node's Property Binder list.
    bind_filter -- The new PropBindCriterion for the Property Binder.
    parent -- Parent QUndoCommand.
    """
    super().__init__(parent)
    
    self._node_props_model = node_props_model
    self._node = node
    self._binder_idx = binder_idx
    self._new_bind_filter = bind_filter
    self._old_bind_filter = node.prop_binders[binder_idx].bind_criterion
    
    self.setText("Change Binding Filter (Node '{}', Idx {})".format(node.name, str(binder_idx)))
    
    self.setObsolete(self._old_bind_filter == self._new_bind_filter)
  
  def id(self):
    return self.__class__._undo_id
  
  def redo(self):
    self._node_props_model.set_bind_filter(self._node, self._binder_idx, self._new_bind_filter)
  
  def undo(self):
    self._node_props_model.set_bind_filter(self._node, self._binder_idx, self._old_bind_filter)