"""Utilities related to PyQt functionality."""
from PyQt5.Qt import QFile, QCoreApplication, QDir, QIcon, QPixmap


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

def make_multires_icon(path):
  """Makes a multi-resolution QIcon using images from the specified path.
  This function assumes that all files in the specified directory contain images that should be loaded into the QIcon.
  path -- Path to the directory containing the images from which the icon should be constructed. Should start with ":"
    if referencing a resource inside a packaged Qt resource file.
  """
  icon = QIcon()
  
  # For each file found in the specified directory, add a pixmap of the file's contents to the icon.
  for file_info in QDir(path).entryInfoList(sort=QDir.Name):
    if file_info.isFile():
      icon.addPixmap(QPixmap(file_info.absoluteFilePath()))
  
  return icon