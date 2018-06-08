from PyQt5.Qt import qmlRegisterType
from scriptaseq.internal.gui.qml_types.timeline_editor import TimelineGrid
def register_qml_types():
  qmlRegisterType(TimelineGrid, 'ScriptASeq', 0, 1, 'TimelineGrid')