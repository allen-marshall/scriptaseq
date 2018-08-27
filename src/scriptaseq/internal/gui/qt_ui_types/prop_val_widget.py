"""Defines the main property value editor widget."""
from PyQt5.Qt import QWidget

from scriptaseq.internal.generated.qt_ui.prop_val_widget import Ui_PropValWidget


class PropValWidget(QWidget, Ui_PropValWidget):
  def __init__(self, parent=None):
    QWidget.__init__(self, parent)
    self.setupUi(self)
    
    self.gui_sync_manager = None
    self._selected_node = None
    self._selected_binder_idx = None
    
    # TODO: Build the editors for the different property types.
  
  def selected_binder_changed(self, node, binder_idx):
    """Notifies the widget that the selected Property Binder has changed.
    node -- Currently selected Sequence Node. A value of None means that no Sequence Node is selected.
    binder_idx -- Index of the newly selected binder in the selected Sequence Node's Property Binder list. A value of
      None means that no binder is selected.
    """
    self._selected_node = node
    self._selected_binder_idx = binder_idx
    self.update_gui_node_path()
    self.update_gui_binder_info()
  
  def update_gui_node_path(self):
    """Updates the GUI to show the path string for the currently selected node."""
    if self._selected_node is None:
      self.selectedNodeLabel.setText('No node selected')
    else:
      self.selectedNodeLabel.setText(self._selected_node.name_path_str)
  
  def update_gui_binder_info(self):
    """Updates the GUI to show information identifying the currently selected binder."""
    if self._selected_node is None or self._selected_binder_idx is None:
      self.selectedBinderLabel.setText('No binder selected')
    else:
      binder = self._selected_node.prop_binders[self._selected_binder_idx]
      self.selectedBinderLabel.setText("{} ('{}', {})".format(str(self._selected_binder_idx), binder.prop_name,
        binder.prop_type.name))