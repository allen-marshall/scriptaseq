"""Script to package this project's Qt resources into .qrc and .rcc files.
Should be executed from the project's main directory."""

import os
import subprocess

# Path to the directory where the raw resource files are stored.
RESOURCES_PATH = 'qt_resources'

# Names of files in the resources directory that should not be included in the resource packages.
RESOURCE_FILE_NAMES_TO_IGNORE = ['.gitignore']

# Path to the .qrc file that should be generated.
QRC_FILE_PATH = 'resources.qrc'

# Path to the .rcc file that should be generated.
RCC_FILE_PATH = 'resources.rcc'

if __name__ == '__main__':
  
  # Build the .qrc file.
  with open(QRC_FILE_PATH, 'w') as qrc_file:
    qrc_file.write('<!DOCTYPE RCC><RCC version="1.0">\n')
    qrc_file.write('<qresource>\n')
    
    # Iterate over the resource files and add their paths to the .qrc file.
    for dirpath, dirnames, filenames in os.walk('qt_resources'):
      for file_name in filenames:
        if file_name not in RESOURCE_FILE_NAMES_TO_IGNORE:
          file_path = os.path.join(dirpath, file_name)
          alias_path = os.path.relpath(file_path, RESOURCES_PATH)
          qrc_file.write('  <file alias="{}">{}</file>\n'.format(alias_path, file_path))
    
    qrc_file.write('</qresource>\n')
    qrc_file.write('</RCC>')
  
  # Package the resources into an .rcc file.
  subprocess.call(['rcc', '-binary', QRC_FILE_PATH, '-o', RCC_FILE_PATH])