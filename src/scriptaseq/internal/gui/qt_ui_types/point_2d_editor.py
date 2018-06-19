"""Widget class for point_2d_editor"""

from PyQt5.Qt import QWidget

from scriptaseq.internal.generated.qt_ui.point_2d_editor import Ui_Point2DEditor


class Point2DEditor(QWidget, Ui_Point2DEditor):
  
  def __init__(self, parent=None):
    QWidget.__init__(self, parent)
    self.setupUi(self)