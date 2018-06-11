from PyQt5.Qt import qmlRegisterType

from scriptaseq.internal.gui.qml_types.timeline_editor.grid import TimelineGrid
from scriptaseq.internal.gui.qml_types.timeline_editor.editor import TimelineEditor
from scriptaseq.internal.gui.qml_types.timeline_editor.markers import TimelineMarkers

# Settings for the ScriptASeq QML library.
QML_LIB_NAME = 'ScriptASeq'
QML_LIB_MAJOR_VERSION = 0
QML_LIB_MINOR_VERSION = 1

def _register_type(py_type, qml_type):
  """Registers the specified QML type.
  py_type -- Python class indicating the type to register.
  qml_type -- Name to use for the type in QML.
  """
  qmlRegisterType(py_type, QML_LIB_NAME, QML_LIB_MAJOR_VERSION, QML_LIB_MINOR_VERSION, qml_type)

def register_qml_types():
  """Registers the ScriptASeq QML library with Qt."""
  _register_type(TimelineGrid, 'TimelineGrid')
  _register_type(TimelineMarkers, 'TimelineMarkers')
  _register_type(TimelineEditor, 'TimelineEditor')