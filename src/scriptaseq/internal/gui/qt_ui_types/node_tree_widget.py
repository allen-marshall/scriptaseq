"""Defines the main node tree widget."""

from PyQt5.Qt import QWidget

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