"""Functionality related to use of media/MIME types to transfer data around within the application.
This functionality may be used e.g. by a drag and drop mechanism.
"""
from PyQt5.Qt import QCoreApplication

from scriptaseq.named_tree_node import TreeNamePath


# String encoding to use when serializing strings.
MEDIA_STR_ENCODING = 'utf-8'

# Media type for path-based references to project nodes.
PROJECT_TREE_NODE_PATH_MEDIA_TYPE = 'application/x-scriptaseq-project-tree-node-path'

def encode_project_tree_node_path(path):
  """Encodes a path-based reference to a project tree node.
  Suitable for use with the PROJECT_TREE_NODE_PATH_MEDIA_TYPE media type. Returns the data as a bytes-like object.
  Raises ValueError if the specified path is relative.
  path --  TreeNamePath to encode.
  """
  if not path.is_absolute:
    raise ValueError(
      QCoreApplication.translate('MIMEData', 'Cannot encode relative path as project tree node path data.'))
  
  return str(path).encode(MEDIA_STR_ENCODING)

def decode_project_tree_node_path(data):
  """Decodes a path-based reference to a project tree node.
  Suitable for use with the PROJECT_TREE_NODE_PATH_MEDIA_TYPE media type.
  Returns the decoded path as a TreeNamePath object.
  """
  path = TreeNamePath.from_str(bytes(data).decode(MEDIA_STR_ENCODING))
  if not path.is_absolute:
    raise ValueError(QCoreApplication.translate('MIMEData', 'Expected an absolute path, got a relative path.'))
  return path