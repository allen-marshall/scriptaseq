"""ScriptASeq launcher script"""

import sys

from PyQt5.Qt import QUrl, QGuiApplication, QQmlApplicationEngine, QTimer
from scriptaseq.internal.gui.qml_types.registration import register_qml_types
from scriptaseq.subspace import SubspaceSettings, GridSettings
from scriptaseq.geom import Rectangle
from scriptaseq.seq_node import SeqNode
from scriptaseq.internal.gui.qml_types.timeline_editor import TimelineGrid

if __name__ == '__main__':

  qt_app = QGuiApplication(sys.argv)
  
  register_qml_types()
  
  # Extract main window from QML file.
  qml_app_engine = QQmlApplicationEngine()
  qml_app_engine.load(QUrl('qml/MainWindow.qml'))
  main_window = qml_app_engine.rootObjects()[0]
  
  # Create an example Sequence Node for testing the GUI functionality.
  boundary = Rectangle(0, 0, 10, 10)
  grid_settings = GridSettings(Rectangle(0, 0, 1, 1))
  subspace = SubspaceSettings(boundary, grid_settings)
  test_node = SeqNode('test', subspace)
  
  # Pass the Sequence Node information to the GUI.
  timeline_grid = main_window.findChild(TimelineGrid, 'grid')
  timeline_grid.seq_node = test_node
  
  # Show the main window.
  main_window.showMaximized()
  
  # Test ability to detect changes.
  def test_change_0():
    test_node.subspace.zoom_settings = (64, 32)
    timeline_grid.update()
  QTimer.singleShot(2000, test_change_0)
  def test_change_1():
    test_node.subspace.grid_settings = GridSettings(Rectangle(0.5, 0.5, 2, 2), (False, False), (True, False))
    timeline_grid.update()
  QTimer.singleShot(4000, test_change_1)
  
  sys.exit(qt_app.exec_())
