"""ScriptASeq launcher script"""

from PyQt5.Qt import QApplication
import sys

from scriptaseq.internal.gui.qml_types.registration import register_qml_types
from scriptaseq.internal.gui.main_window import MainWindow

if __name__ == '__main__':
  qt_app = QApplication(sys.argv)
  register_qml_types()
  main_window = MainWindow()
  main_window.showMaximized()
  sys.exit(qt_app.exec_())
