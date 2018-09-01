"""ScriptASeq launcher script"""

from PyQt5.Qt import QTranslator, QLocale, QLibraryInfo, QDir, QResource, QFile
from PyQt5.QtWidgets import QApplication
import sys

from scriptaseq.internal.gui.qml_types.registration import register_qml_types
from scriptaseq.internal.gui.qt_ui_types.main_window import MainWindow
from scriptaseq.internal.gui.qt_util import read_qt_resource


# Text encoding to assume when loading the default style sheet.
DEFAULT_STYLE_SHEET_ENCODING = 'utf-8'

def _init_translation(qt_app):
  """Sets up translation data for the application.
  qt_app -- The QApplication that is being set up.
  """
  # Set up translation for Qt's built-in strings.
  qt_translator = QTranslator(qt_app)
  if not qt_translator.load('qt_' + QLocale.system().name(), QLibraryInfo.location(QLibraryInfo.TranslationsPath)):
    # TODO: Log the failure to load translation information.
    pass
  elif not qt_app.installTranslator(qt_translator):
    # TODO: Log the failure to install translation information.
    pass
  
  # Set up translation for app-specific strings.
  app_translator = QTranslator(qt_app)
  app_translations_path = QDir.toNativeSeparators('./qt_qm/translations')
  if not app_translator.load('scriptaseq_' + QLocale.system().name(), app_translations_path):
    # TODO: Log the failure to load translation information.
    pass
  elif not qt_app.installTranslator(app_translator):
    # TODO: Log the failure to load translation information.
    pass

def _init_style(qt_app):
  """Sets up style information for the application.
  qt_app -- The QApplication that is being set up.
  """
  # TODO: Allow loading of custom styles.
  style_text = read_qt_resource(':/qss/default.qss', DEFAULT_STYLE_SHEET_ENCODING)
  qt_app.setStyleSheet(style_text)

if __name__ == '__main__':
  qt_app = QApplication(sys.argv)
  
  # Register resource packages.
  QResource.registerResource('resources.rcc')
  
  # Set up translation.
  _init_translation(qt_app)
  
  # Set up style information.
  _init_style(qt_app)
  
  register_qml_types()
  
  # Construct the main window.
  main_window = MainWindow()
  main_window.showMaximized()
  
  sys.exit(qt_app.exec_())
