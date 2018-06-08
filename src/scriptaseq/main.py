"""ScriptASeq launcher script"""

import sys

from PyQt5.Qt import QQmlEngine, QQmlComponent, QUrl, QGuiApplication, QQmlApplicationEngine
from scriptaseq.internal.gui.qml_types.registration import register_qml_types

if __name__ == '__main__':
  qt_app = QGuiApplication(sys.argv)
  
  register_qml_types()
  
  qml_app_engine = QQmlApplicationEngine()
  qml_app_engine.load(QUrl('qml/MainWindow.qml'))
  main_window = qml_app_engine.rootObjects()[0]
  
#   qml_engine = QQmlEngine()
#   qml_component = QQmlComponent(qml_engine)
#   qml_component.loadUrl(QUrl('qml/TimelineEditor.qml'))
#   qml_grid = qml_component.create()

  sys.exit(qt_app.exec_())
