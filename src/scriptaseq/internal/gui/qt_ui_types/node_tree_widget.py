"""Defines the main node tree widget."""

from PyQt5.Qt import QWidget, QPoint

from scriptaseq.internal.generated.qt_ui.node_tree_widget import Ui_NodeTreeWidget


class NodeTreeWidget(QWidget, Ui_NodeTreeWidget):
  def __init__(self, parent=None):
    QWidget.__init__(self, parent)
    self.setupUi(self)
  
  @property
  def node_tree_model(self):
    """Property containing the Qt item model to show in the node tree view."""
    return self.seqNodeTreeView.model()
  
  @node_tree_model.setter
  def node_tree_model(self, node_tree_model):
    self.seqNodeTreeView.setModel(node_tree_model)
  
  def contextMenuEvent(self, event):
    # Get event position relative to the node tree view.
    tree_view_pos = event.globalPos() - self.seqNodeTreeView.mapToGlobal(QPoint())
    
    model_index = self.seqNodeTreeView.indexAt(tree_view_pos)
    if model_index.isValid():
      menu = self.node_tree_model.make_context_menu(model_index, self)
      if menu is not None:
        event.setAccepted(True)
        menu.exec_(event.globalPos())