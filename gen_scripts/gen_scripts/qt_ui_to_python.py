"""Script to convert this project's Qt UI files into PyQt Python files using pyuic5.
Should be executed from the project's main directory."""

import os
import subprocess


# File extension suffix for Qt UI files.
UI_FILE_EXTENSION_SUFFIX = '.ui'

# Path to the directory where the project's Qt UI files are stored, relative to the main project directory.
QT_UI_PATH = 'qt_ui'

QT_UI_PY_PATH = 'src/scriptaseq/internal/generated/qt_ui'

def process_subdir(dir_path):
  """Processes a subdirectory of the main Qt UI file directory.
  Should be called before process_file is called for files in the subdirectory.
  dir_path -- Path to the subdirectory, relative to the main Qt UI file directory. Should not be empty.
  """
  # Create a Python module corresponding to the directory, if one does not exist. The created module will have an empty
  # __init__.py file.
  os.mkdir(os.path.join(QT_UI_PY_PATH, dir_path))
  with open(os.path.join(QT_UI_PY_PATH, dir_path, '__init__.py'), 'w'):
    pass

def process_file(dir_path, base_file_name):
  """Processes an individual UI file.
  dir_path -- Path to the directory containing the UI file, relative to the main Qt UI file directory.
  base_file_name -- Name of the UI file, with the file extension suffix removed.
  """
  in_path = os.path.join(QT_UI_PATH, dir_path, base_file_name + UI_FILE_EXTENSION_SUFFIX)
  out_path = os.path.join(QT_UI_PY_PATH, dir_path, base_file_name + '.py')
  subprocess.call(['pyuic5', in_path, '-o', out_path])
  

if __name__ == '__main__':
  
  for (dirpath, dirnames, filenames) in os.walk(QT_UI_PATH):
    dir_rel_path = os.path.relpath(dirpath, QT_UI_PATH)
    for dir_name in dirnames:
      process_subdir(os.path.join(dir_rel_path, dir_name))
    for file_name in filenames:
      if file_name.endswith(UI_FILE_EXTENSION_SUFFIX):
        process_file(dir_rel_path, file_name[:-len(UI_FILE_EXTENSION_SUFFIX)])