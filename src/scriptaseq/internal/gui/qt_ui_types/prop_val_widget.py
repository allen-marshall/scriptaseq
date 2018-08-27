"""Defines the main property value editor widget."""
from PyQt5.Qt import QWidget

from scriptaseq.internal.generated.qt_ui.prop_val_widget import Ui_PropValWidget


class PropValWidget(QWidget, Ui_PropValWidget):
  def __init__(self, parent=None):
    QWidget.__init__(self, parent)
    self.setupUi(self)
    
    self.gui_sync_manager = None
    
    # TODO: Build the editors for the different property types.