"""Script to update app translation source files based on translatable strings found in the source code.
Should be executed from the project's main directory."""
import os
from gen_scripts.util import SUPPORTED_TRANSLATION_LOCALES
import subprocess


# Path to the ScriptASeq app's main Python source directory.
APP_MAIN_SRC_PATH = 'src'

# Format string that takes a locale name and generates the path to the Qt .ts file that should be generated for that
# locale.
TRANSLATION_SRC_FILE_FORMAT_STRING = 'qt_ts/scriptaseq_{}.ts'

if __name__ == '__main__':
  
  # Construct a list of all of the main app's Python source files.
  python_src_files = []
  for (dirpath, dirnames, filenames) in os.walk(APP_MAIN_SRC_PATH):
    for file_name in filenames:
      if file_name.endswith('.py'):
        python_src_files.append(os.path.join(dirpath, file_name))
  
  # Construct a list of translation source files to update.
  translation_src_files = []
  for translation_locale in SUPPORTED_TRANSLATION_LOCALES:
    translation_src_files.append(TRANSLATION_SRC_FILE_FORMAT_STRING.format(translation_locale))
  
  # Run the pylupdate5 command to update the translation source files.
  subprocess.call(['pylupdate5'] + python_src_files + ['-ts'] + translation_src_files)