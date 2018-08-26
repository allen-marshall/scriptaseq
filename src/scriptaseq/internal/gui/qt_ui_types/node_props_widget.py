"""Defines the main node tree widget."""

from PyQt5.Qt import QWidget, QPoint
from sortedcontainers.sortedset import SortedSet

from scriptaseq.internal.generated.qt_ui.node_props_widget import Ui_NodePropsWidget
from scriptaseq.internal.gui.qt_models.prop_binders_table_model import PropBindersTableDelegate
from scriptaseq.internal.gui.undo_commands.seq_node import SetNodeTagsCommand


# Separator string for displaying node tags as strings.
TAGS_SEPARATOR = ','

class NodePropsWidget(QWidget, Ui_NodePropsWidget):
  def __init__(self, parent=None):
    QWidget.__init__(self, parent)
    self.setupUi(self)
    
    self.nodePropsTableView.setItemDelegate(PropBindersTableDelegate(self))
    
    self.selected_node = None
    self.undo_stack = None
    
    self.tagsLineEdit.editingFinished.connect(self._update_node_tags)
  
  @property
  def node_props_model(self):
    """Property containing the Qt item model to show in the node properties table."""
    return self.nodePropsTableView.model()
  
  @node_props_model.setter
  def node_props_model(self, node_props_model):
    self.nodePropsTableView.setModel(node_props_model)
    # TODO: Need to disconnect this connection if the setter gets called multiple times.
    node_props_model.node_tree_sel_model.currentChanged.connect(
      lambda current, previous: self._update_selected_node(current))
  
  def update_tag_display(self):
    """Updates the GUI to reflect any changes in the currently selected Sequence Node's tags."""
    if self.selected_node is None:
      self.tagsLineEdit.setText('')
      self.tagsLineEdit.setEnabled(False)
    else:
      self.tagsLineEdit.setText(TAGS_SEPARATOR.join(self.selected_node.tags))
      self.tagsLineEdit.setEnabled(True)
  
  def _update_selected_node(self, index):
    """Updates the GUI to reflect changes in the currently selected Sequence Node.
    index -- Model index into the Sequence Node tree model indicating the currently selected sequence node.
    """
    self.selected_node = self.node_props_model.node_tree_sel_model.model().seq_node_from_qt_index(index)
    if self.selected_node is None:
      self.selectedNodeLabel.setText('No node selected')
    else:
      self.selectedNodeLabel.setText(self.selected_node.name_path_str)
    self.update_tag_display()
  
  def _update_node_tags(self):
    """Updates the tags of the currently selected Sequence Node, based on GUI information."""
    if self.selected_node is not None and self.undo_stack is not None:
      tags_text = self.tagsLineEdit.text()
      new_tags = SortedSet(tags_text.split(TAGS_SEPARATOR))
      self.undo_stack.push(SetNodeTagsCommand(self, self.selected_node, new_tags))
  
  def contextMenuEvent(self, event):
    # Get event position relative to the node properties view.
    props_view_pos = event.globalPos() - self.nodePropsTableView.viewport().mapToGlobal(QPoint())
    
    model_index = self.nodePropsTableView.indexAt(props_view_pos)
    if model_index.isValid():
      menu = self.node_props_model.make_context_menu(model_index, self)
      if menu is not None:
        event.setAccepted(True)
        menu.exec_(event.globalPos())