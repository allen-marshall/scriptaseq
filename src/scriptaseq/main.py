"""ScriptASeq launcher script"""

from PyQt5.Qt import QUrl, QGuiApplication, QQmlApplicationEngine, QTimer
import sys

from scriptaseq.geom import Rectangle
from scriptaseq.internal.gui.qml_types.registration import register_qml_types
from scriptaseq.internal.gui.qml_types.timeline_editor.editor import TimelineEditor
from scriptaseq.seq_node import SeqNode
from scriptaseq.subspace import SubspaceSettings, GridSettings, SpaceMarker
from scriptaseq.color import RGBAColor


if __name__ == '__main__':
  
  register_qml_types()

  qt_app = QGuiApplication(sys.argv)
  
  # Extract main window from QML file.
  qml_app_engine = QQmlApplicationEngine()
  qml_app_engine.load(QUrl('qml/MainWindow.qml'))
  main_window = qml_app_engine.rootObjects()[0]
  
  # Create an example Sequence Node for testing the GUI functionality.
  boundary = Rectangle(0, 0, 10, 10)
  grid_settings = GridSettings(Rectangle(0, 0, 1, 1))
  markers = [SpaceMarker(True, 0, 1, RGBAColor(1, 0.25, 0, 0.5), 'unit'),
             SpaceMarker(False, 0, 2, RGBAColor(0, 1, 0, 0.4), 'double unit')]
  subspace = SubspaceSettings(boundary, grid_settings, markers=markers)
  test_node = SeqNode('test', subspace)
  
  # Pass the Sequence Node information to the GUI.
  timeline_editor = main_window.findChild(TimelineEditor, 'timelineEditor')
  timeline_editor.seq_node = test_node
   
  # Show the main window.
  main_window.showMaximized()
   
  # Test ability to detect changes.
  def test_change_0():
    test_node.subspace.zoom_settings = (64, 32)
    timeline_editor.update()
  QTimer.singleShot(2000, test_change_0)
  def test_change_1():
    test_node.subspace.grid_settings = GridSettings(Rectangle(0.5, 0.5, 2, 2), (False, False), (True, False))
    timeline_editor.update()
  QTimer.singleShot(4000, test_change_1)
  
  sys.exit(qt_app.exec_())
