"""Defines the value editor widget to use when no Property Binder is selected."""

from PyQt5.Qt import QWidget

from scriptaseq.internal.generated.qt_ui.val_editor_not_selected_widget import Ui_ValEditorNotSelectedWidget
from scriptaseq.internal.gui.val_editor_widget import ValEditorWidget


class ValEditorNotSelectedWidget(ValEditorWidget, Ui_ValEditorNotSelectedWidget):
  
  def __init__(self, parent=None):
    QWidget.__init__(self, parent)
    self.setupUi(self)