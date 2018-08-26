"""Defines the main node tree widget."""

from PyQt5.Qt import QWidget, QPoint

from scriptaseq.internal.generated.qt_ui.node_props_widget import Ui_NodePropsWidget
from scriptaseq.internal.gui.qt_models.prop_binders_table_model import PropBindersTableDelegate


class NodePropsWidget(QWidget, Ui_NodePropsWidget):
  def __init__(self, parent=None):
    QWidget.__init__(self, parent)
    self.setupUi(self)
    
    self.nodePropsTableView.setItemDelegate(PropBindersTableDelegate(self))
  
  @property
  def node_props_model(self):
    """Property containing the Qt item model to show in the node properties table."""
    return self.nodePropsTableView.model()
  
  @node_props_model.setter
  def node_props_model(self, node_props_model):
    self.nodePropsTableView.setModel(node_props_model)
  
  def contextMenuEvent(self, event):
    # Get event position relative to the node tree view.
    props_view_pos = event.globalPos() - self.seqNodePropsView.mapToGlobal(QPoint())
    
    model_index = self.seqNodePropsView.indexAt(props_view_pos)
    if model_index.isValid():
      menu = self.node_props_model.make_context_menu(model_index, self)
      if menu is not None:
        event.setAccepted(True)
        menu.exec_(event.globalPos())