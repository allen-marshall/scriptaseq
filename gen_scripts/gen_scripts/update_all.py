"""Script that calls the other generation scripts to update all auto-generated files in the project.
Should be executed from the project's main directory."""

import runpy


if __name__ == '__main__':
  
  runpy.run_module('gen_scripts.qt_ui_to_python', run_name='__main__')
  runpy.run_module('gen_scripts.update_translation_source_files', run_name='__main__')
  runpy.run_module('gen_scripts.update_translation_release_files', run_name='__main__')