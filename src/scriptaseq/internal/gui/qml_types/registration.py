from PyQt5.Qt import qmlRegisterType

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
  # Currently ScriptASeq doesn't register any QML types.
  pass