"""Script that calls the other generation scripts to update all auto-generated files in the project.
Should be executed from the project's main directory."""

import runpy
import argparse


if __name__ == '__main__':
  
  arg_parser = argparse.ArgumentParser()
  arg_parser.add_argument('--no-update-translation-source-files', dest='no_update_translation_source_files',
    action='store_const', const=True, default=False)
  args = arg_parser.parse_args()
  
  runpy.run_module('gen_scripts.qt_ui_to_python', run_name='__main__')
  if not args.no_update_translation_source_files:
    runpy.run_module('gen_scripts.update_translation_source_files', run_name='__main__')
  runpy.run_module('gen_scripts.update_translation_release_files', run_name='__main__')
  runpy.run_module('gen_scripts.package_qt_resources', run_name='__main__')