"""Defines the main node properties widget."""

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
    
    self.gui_sync_manager = None
    self.undo_stack = None
    self._selected_node = None
    
    self.nodePropsTableView.setItemDelegate(PropBindersTableDelegate(self))
    
    self.tagsLineEdit.editingFinished.connect(self._update_node_tags)
  
  def selected_node_changed(self, node):
    """Notifies the widget that the selected Sequence Node has changed.
    node -- The newly selected Sequence Node.
    """
    self._selected_node = node
    self.update_gui_node_path()
    self.update_gui_tags()
  
  def update_gui_node_path(self):
    """Updates the GUI to show the path string for the currently selected node."""
    if self._selected_node is None:
      self.selectedNodeLabel.setText('No node selected')
    else:
      self.selectedNodeLabel.setText(self._selected_node.name_path_str)
    
  def update_gui_tags(self):
    """Updates the GUI to show the tags for the currently selected node."""
    if self._selected_node is None:
      self.tagsLineEdit.setText('')
      self.tagsLineEdit.setEnabled(False)
    else:
      self.tagsLineEdit.setText(NODE_TAGS_SEPARATOR.join(self._selected_node.tags))
      self.tagsLineEdit.setEnabled(True)
  
  def _update_node_tags(self):
    """Updates the tags of the currently selected Sequence Node, based on GUI information."""
    if self.gui_sync_manager is not None and self.undo_stack is not None and self._selected_node is not None:
      tags_text = self.tagsLineEdit.text()
      new_tags = SortedSet(tags_text.split(NODE_TAGS_SEPARATOR))
      if self._selected_node.tags != new_tags:
        self.undo_stack.push(SetNodeTagsCommand(self.gui_sync_manager, self._selected_node, new_tags))
  
  def contextMenuEvent(self, event):
    # Get event position relative to the node properties table.
    props_view_pos = event.globalPos() - self.nodePropsTableView.viewport().mapToGlobal(QPoint())
    
    # If the event occurred inside the node properties table, show a context menu for the table.
    if self.nodePropsTableView.viewport().rect().contains(props_view_pos):
      model_index = self.nodePropsTableView.indexAt(props_view_pos)
      menu = self.nodePropsTableView.model().make_context_menu(model_index, self)
      if menu is not None:
        event.setAccepted(True)
        menu.exec_(event.globalPos())