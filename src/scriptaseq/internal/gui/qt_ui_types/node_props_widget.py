"""Defines the main node tree widget."""

from PyQt5.Qt import QWidget, QPoint
from sortedcontainers.sortedset import SortedSet

from scriptaseq.internal.generated.qt_ui.node_props_widget import Ui_NodePropsWidget
from scriptaseq.internal.gui.qt_models.prop_binders_table_model import PropBindersTableDelegate
from scriptaseq.internal.gui.undo_commands.seq_node import SetNodeTagsCommand


# Separator string for displaying node tags as strings.
NODE_TAGS_SEPARATOR = ','

class NodePropsWidget(QWidget, Ui_NodePropsWidget):
  def __init__(self, parent=None):
    QWidget.__init__(self, parent)
    self.setupUi(self)
    
    self.nodePropsTableView.setItemDelegate(PropBindersTableDelegate(self))
    
    self.node_props_wdm = None
    
    self.tagsLineEdit.editingFinished.connect(self._update_node_tags)
  
  @property
  def node_props_model(self):
    """Property containing the Qt item model to show in the node properties table."""
    return self.nodePropsTableView.model()
  
  @node_props_model.setter
  def node_props_model(self, node_props_model):
    self.nodePropsTableView.setModel(node_props_model)
  
  def _update_node_tags(self):
    """Updates the tags of the currently selected Sequence Node, based on GUI information."""
    if self.node_props_wdm is not None and self.undo_stack is not None:
      tags_text = self.tagsLineEdit.text()
      new_tags = SortedSet(tags_text.split(NODE_TAGS_SEPARATOR))
      self.node_props_wdm.set_selected_node_tags_undoable(new_tags)
  
  def contextMenuEvent(self, event):
    # Get event position relative to the node properties view.
    props_view_pos = event.globalPos() - self.nodePropsTableView.viewport().mapToGlobal(QPoint())
    
    model_index = self.nodePropsTableView.indexAt(props_view_pos)
    if model_index.isValid():
      menu = self.node_props_model.make_context_menu(model_index, self)
      if menu is not None:
        event.setAccepted(True)
        menu.exec_(event.globalPos())

class NodePropsWidgetDisplayManager:
  """Responsible for keeping a NodePropsWidget's GUI up to date.
  QUndoCommands that modify node properties displayed in the NodePropsWidget should generally do so through an instance
  of this class, except when the change is related to the Property Binders table, in which case a PropBindersTableModel
  should be used instead.
  """
  
  def __init__(self, node_props_widget, node_tree_sel_model, undo_stack):
    """Constructor
    node_props_widget -- NodePropsWidget that displays node properties. This widget will be kept up to date by this
      manager.
    node_tree_sel_model -- QItemSelectionModel from which the selected node will be determined.
    undo_stack -- QUndoStack to receive undo commands generated through the manager.
    """
    self._node_props_widget = node_props_widget
    self._node_tree_sel_model = node_tree_sel_model
    self._undo_stack = undo_stack
    
    self._node_tree_sel_model.currentChanged.connect(lambda current, previous: self._update_selected_node())
    
    self._update_selected_node()
  
  def set_node_tags(self, node, new_tags):
    """Sets a Sequence Node's tags, and updates the GUI accordingly.
    Note: This method generally should only be called from within a QUndoCommand, as the user will not be able to undo
    it otherwise.
    node -- Sequence Node whose tags are to be changed.
    new_tags -- Iterable containing the new set of tags for the node.
    """
    node.tags.clear()
    node.tags.update(new_tags)
    if node is self._selected_node:
      self._update_gui_tags()
  
  def set_selected_node_tags_undoable(self, new_tags):
    """Sets the currently selected Sequence Node's tags, and updates the GUI accordingly.
    Note: This method uses a QUndoCommand internally, so it is undoable.
    new_tags -- Iterable containing the new set of tags for the selected Sequence Node.
    """
    if self._selected_node is not None and self._selected_node.tags != SortedSet(new_tags):
      self._undo_stack.push(SetNodeTagsCommand(self, self._selected_node, new_tags)) 
  
  def _update_selected_node(self):
    """Updates the manager's internal reference to the currently selected sequence node."""
    self._selected_node = self._node_tree_sel_model.model().seq_node_from_qt_index(
      self._node_tree_sel_model.currentIndex())
    self._update_gui_node_path()
    self._update_gui_tags()
  
  def _update_gui_node_path(self):
    """Updates the GUI display of the selected node path.
    Should be called when the selected node is reassigned, renamed, or moved to a new position in the tree structure.
    """
    if self._selected_node is None:
      self._node_props_widget.selectedNodeLabel.setText('No node selected')
    else:
      self._node_props_widget.selectedNodeLabel.setText(self._selected_node.name_path_str)
  
  def _update_gui_tags(self):
    """Updates the GUI display of the node tags.
    Should be called when the selected node is reassigned or its tags change.
    """
    if self._selected_node is None:
      self._node_props_widget.tagsLineEdit.setText('')
      self._node_props_widget.tagsLineEdit.setEnabled(False)
    else:
      self._node_props_widget.tagsLineEdit.setText(NODE_TAGS_SEPARATOR.join(self._selected_node.tags))
      self._node_props_widget.tagsLineEdit.setEnabled(True)