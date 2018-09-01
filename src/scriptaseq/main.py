"""ScriptASeq launcher script"""

from PyQt5.Qt import QTranslator, QLocale, QLibraryInfo, QDir, QResource
from PyQt5.QtWidgets import QApplication
import sys

from scriptaseq.internal.gui.qml_types.registration import register_qml_types
from scriptaseq.internal.gui.qt_ui_types.main_window import MainWindow


if __name__ == '__main__':
  qt_app = QApplication(sys.argv)
  
  # Register resource packages.
  QResource.registerResource('resources.rcc')
  
  # Set up translation.
  
  qt_translator = QTranslator(qt_app)
  if not qt_translator.load('qt_' + QLocale.system().name(), QLibraryInfo.location(QLibraryInfo.TranslationsPath)):
    # TODO: Log the failure to load translation information.
    pass
  elif not qt_app.installTranslator(qt_translator):
    # TODO: Log the failure to install translation information.
    pass
  
  app_translator = QTranslator(qt_app)
  app_translations_path = QDir.toNativeSeparators('./qt_qm/translations')
  if not app_translator.load('scriptaseq_' + QLocale.system().name(), app_translations_path):
    # TODO: Log the failure to load translation information.
    pass
  elif not qt_app.installTranslator(app_translator):
    # TODO: Log the failure to load translation information.
    pass
  
  register_qml_types()
  
  # Construct the main window.
  main_window = MainWindow()
  main_window.showMaximized()
  
  sys.exit(qt_app.exec_())
