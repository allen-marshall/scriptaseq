"""Defines the value editor widget to use for property types where the editor is not yet implemented."""

from PyQt5.Qt import QWidget

from scriptaseq.internal.generated.qt_ui.val_editor_not_implemented_widget import Ui_ValEditorNotImplementedWidget
from scriptaseq.internal.gui.val_editor_widget import ValEditorWidget


class ValEditorNotImplementedWidget(ValEditorWidget, Ui_ValEditorNotImplementedWidget):
  
  def __init__(self, parent=None):
    QWidget.__init__(self, parent)
    self.setupUi(self)
  
  def update_editor(self, node, binder_idx):
    if node is None or binder_idx is None:
      self.notImplementedMessageLabel.setText('No Property Binder selected')
    else:
      binder = node.prop_binders[binder_idx]
      self.notImplementedMessageLabel.setText('Editor not implemented for type {}'.format(binder.prop_type.name))