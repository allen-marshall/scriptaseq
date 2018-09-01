"""Script to update app translation release files based on translation source files.
Should be executed from the project's main directory."""

from gen_scripts.util import SUPPORTED_TRANSLATION_LOCALES
import subprocess


# Format string that takes a locale name and generates the path to the Qt .ts file for that locale.
TRANSLATION_SRC_FILE_FORMAT_STRING = 'qt_ts/scriptaseq_{}.ts'

# Format string that takes a locale name and generates the path to the QT .qm file that should be generated for that
# locale.
TRANSLATION_RELEASE_FILE_FORMAT_STRING = 'qt_qm/translations/scriptaseq_{}.qm'

if __name__ == '__main__':
  
  for translation_locale in SUPPORTED_TRANSLATION_LOCALES:
    src_file = TRANSLATION_SRC_FILE_FORMAT_STRING.format(translation_locale)
    release_file = TRANSLATION_RELEASE_FILE_FORMAT_STRING.format(translation_locale)
    subprocess.call(['lrelease', src_file, '-qm', release_file])