"""Functionality for keeping the GUI state synchronized with the project contents"""

from PyQt5.Qt import QObject

from scriptaseq.internal.gui.qt_models.prop_binders_table_model import PropBindersTableModel
from scriptaseq.internal.gui.qt_models.seq_node_tree_model import SeqNodeTreeModel


class GUISyncManager(QObject):
  """Main class responsible for keeping the GUI state synchronized with the project contents.
  This class contains several methods that modify the project state and notify the GUI accordingly. To ensure that the
  GUI stays up to date, the project contents should typically be modified only through these methods. Unless otherwise
  noted, these methods should generally be called only from within QUndoCommands, as the user will not be able to undo
  the changes otherwise.
  The GUISyncManager is also responsible for creating the Qt item models used for things like the Sequence Node tree and
  Property Binder table.
  """
  
  def __init__(self, root_node, undo_stack, node_tree_widget, node_props_widget, prop_val_widget, parent=None):
    """Constructor
    root_node -- Root SeqNode for the Sequence Node tree.
    undo_stack -- QUndoStack to receive undo commands generated inside this manager.
    node_tree_widget -- NodeTreeWidget responsible for displaying the node tree.
    node_props_widget -- NodePropsWidget responsible for displaying the node properties.
    prop_val_widget -- PropValWidget responsible for displaying the property value editor.
    parent -- Parent QObject.
    """
    super().__init__(parent)
    
    self._root_node = root_node
    self._undo_stack = undo_stack
    self._node_tree_widget = node_tree_widget
    self._node_props_widget = node_props_widget
    self._prop_val_widget = prop_val_widget
    
    node_tree_widget.gui_sync_manager = self
    node_props_widget.gui_sync_manager = self
    prop_val_widget.gui_sync_manager = self
    
    self._seq_node_tree_model = SeqNodeTreeModel(root_node, undo_stack, self)
    node_tree_widget.seqNodeTreeView.setModel(self._seq_node_tree_model)
    self._seq_node_sel_model = node_tree_widget.seqNodeTreeView.selectionModel()
    
    self._prop_binders_table_model = PropBindersTableModel(undo_stack, self)
    node_props_widget.nodePropsTableView.setModel(self._prop_binders_table_model)
    self._prop_binder_sel_model = node_props_widget.nodePropsTableView.selectionModel()
    
    self._seq_node_sel_model.currentChanged.connect(lambda current, previous: self._selected_node_changed())
    self._prop_binder_sel_model.currentChanged.connect(lambda current, previous: self._selected_binder_changed())
    
    # Initialize selection information.
    self._selected_node_changed()
    self._selected_binder_changed()
  
  def rename_node(self, node, name):
    """Renames a Sequence Node.
    Raises ValueError if the specified name is not available for the specified node, or if the node is the root node.
    node -- Sequence Node to rename.
    name -- New name for the node.
    """
    self._seq_node_tree_model.rename_node(node, name)
  
  def add_node(self, parent, node):
    """Adds a Sequence Node to the node tree.
    Raises ValueError if the node cannot be added because the desired parent already has a different child with the same
    name.
    parent -- Parent node to which the child will be added.
    node -- Child node to add.
    """
    self._seq_node_tree_model.add_node(parent, node)
  
  def remove_node(self, node):
    """Removes a Sequence Node from the node tree.
    Raises ValueError if the node is the root.
    node -- Sequence Node to remove.
    """
    self._seq_node_tree_model.remove_node(node)
  
  def set_node_tags(self, node, tags):
    """Sets a Sequence Node's tags.
    node -- Sequence Node whose tags will be changed.
    tags -- Iterable containing the new set of tags.
    """
    node.tags.clear()
    node.tags.update(tags)
    self._node_props_widget.update_gui_tags()
  
  def add_prop_binder(self, node, binder_idx, binder):
    """Adds a new Property Binder to a Sequence Node.
    node -- Sequence Node that will own the Property Binder.
    binder_idx -- Desired index of the binder in the node's Property Binder list.
    binder -- New binder to add to the Sequence Node.
    """
    self._prop_binders_table_model.add_prop_binder(node, binder_idx, binder)
  
  def remove_prop_binder(self, node, binder_idx):
    """Removes a Property Binder from a Sequence Node.
    node -- Sequence Node that owns the Property Binder.
    binder_idx -- Index of the binder to delete in the node's Property Binder list.
    """
    self._prop_binders_table_model.remove_prop_binder(node, binder_idx)
  
  def set_prop_name(self, node, binder_idx, new_prop_name):
    """Sets the property name for a Property Binder.
    node -- Sequence Node that owns the Property Binder.
    binder_idx -- Index of the binder in the node's Property Binder list.
    new_prop_name -- New property name for the binder.
    """
    self._prop_binders_table_model.set_prop_name(node, binder_idx, new_prop_name)
  
  def set_prop_type(self, node, binder_idx, new_prop_type):
    """Sets the property type for a Property Binder.
    Note: Changing a Property Binder's property type may also affect its property value, so QUndoCommands that call this
    method should generally store the old property value as well as the old property type.
    node -- Sequence Node that owns the Property Binder.
    binder_idx -- Index of the binder in the node's Property Binder list.
    new_prop_type -- New PropType for the binder.
    """
    self._prop_binders_table_model.set_prop_type(node, binder_idx, new_prop_type)
  
  def set_prop_val(self, node, binder_idx, new_prop_val):
    """Sets the property value for a Property Binder.
    node -- Sequence Node that owns the Property Binder.
    binder_idx -- Index of the binder in the node's Property Binder list.
    new_prop_val -- New property value for the binder.
    """
    self._prop_binders_table_model.set_prop_val(node, binder_idx, new_prop_val)
  
  def set_bind_filter(self, node, binder_idx, new_filter):
    """Sets the binding filter for a Property Binder.
    node -- Sequence Node that owns the Property Binder.
    binder_idx -- Index of the binder in the node's Property Binder list.
    new_filter -- New PropBindCriterion for the binder.
    """
    self._prop_binders_table_model.set_bind_filter(node, binder_idx, new_filter)
  
  def _selected_node(self):
    """Gets the currently selected Sequence Node.
    Returns None if no node is selected."""
    return self._seq_node_tree_model.seq_node_from_qt_index(self._seq_node_sel_model.currentIndex())
  
  def _selected_binder_idx(self):
    """Gets the index of the currently selected Property Binder, within the binder list of the node that owns it.
    Returns None if no Property Binder is selected.
    """
    if self._selected_node() is None:
      return None
    
    return self._prop_binders_table_model.binder_idx_from_qt_index(self._prop_binder_sel_model.currentIndex())
  
  def _selected_node_changed(self):
    """Called when the selected Sequence Node has changed."""
    selected_node = self._selected_node()
    self._prop_binders_table_model.selected_node_changed(selected_node)
    self._node_props_widget.selected_node_changed(selected_node)
    self._prop_val_widget.selected_binder_changed(selected_node, None)
  
  def _selected_binder_changed(self):
    """Called when the selected Property Binder has changed."""
    selected_node = self._selected_node()
    selected_binder_idx = self._selected_binder_idx()
    self._prop_val_widget.selected_binder_changed(selected_node, selected_binder_idx)