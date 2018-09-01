"""Utilities related to PyQt functionality."""
from PyQt5.Qt import QFile, QCoreApplication


def read_qt_resource(path, encoding=None):
  """Reads a resource from the file system or a packaged Qt resource file.
  Returns either binary or text data, depending on whether encoding is None.
  path -- Path to the resource. Should start with ":" if referencing a resource inside a packaged Qt resource file.
  encoding -- Text encoding to use for decoding the data, or None to return binary data.
  """
  qfile = QFile(path)
  try:
    # Open the QFile.
    if not qfile.open(QFile.ReadOnly):
      raise IOError(QCoreApplication.translate('QtUtil', "Failed to open '{}'").format(path))
    
    # Read the data.
    # TODO: Handle reading in a way that can report errors.
    data = bytes(qfile.readAll())
    
    if encoding is None:
      return data
    else:
      return data.decode(encoding)
  
  # Close the QFile.
  finally:
    if qfile.isOpen():
      qfile.close()