"""Defines the main window class"""

from PyQt5.Qt import QUrl
from PyQt5.QtWidgets import QMainWindow, QUndoStack

from scriptaseq.color import RGBAColor
from scriptaseq.geom import Rectangle
from scriptaseq.internal.generated.qt_ui.main_window import Ui_MainWindow
from scriptaseq.seq_node import SeqNode
from scriptaseq.subspace import GridSettings, SpaceMarker, SubspaceSettings
from scriptaseq.internal.gui.qml_types.timeline_editor.editor import TimelineEditor


class MainWindow(QMainWindow, Ui_MainWindow):
  """Main window for a sequencing project"""
  
  def __init__(self):
    super().__init__()
    self.setupUi(self)
    
    # Handle integration with Qt Quick.
    self.quickTimeline.setSource(QUrl('qml/TimelineDock.qml'))
    self._timeline_editor = self.quickTimeline.rootObject().findChild(TimelineEditor, 'timelineEditor')
    
    # Set up menu actions.
    self._undo_stack = QUndoStack(self)
    self.actionUndo.triggered.connect(self._undo_stack.createUndoAction(self).trigger)
    self.actionRedo.triggered.connect(self._undo_stack.createRedoAction(self).trigger)
    
    # Create default project.
    # TODO: Support opening a project file on startup.
    # TODO: The default project should be more generic/empty. It is currently nonempty for testing purposes.
    boundary = Rectangle(0, 0, 10, 10)
    grid_settings = GridSettings(Rectangle(0, 0, 1, 1))
    markers = [SpaceMarker(True, 0, 1, RGBAColor(1, 0.25, 0, 0.5), 'unit'),
               SpaceMarker(False, 0, 2, RGBAColor(0, 1, 0, 0.4), 'double unit')]
    subspace = SubspaceSettings(boundary, grid_settings, markers=markers)
    self._project_root = SeqNode('test', subspace)
    
    # Provide project information to the GUI.
    self._timeline_editor.seq_node = self._project_root