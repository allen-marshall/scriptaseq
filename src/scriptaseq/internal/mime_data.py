"""Functionality related to use of media/MIME types to transfer data around within the application.
This functionality may be used e.g. by a drag and drop mechanism.
"""
from PyQt5.Qt import QCoreApplication

from scriptaseq.named_tree_node import TreeNamePath
import pickle


# String encoding to use when serializing strings.
MEDIA_STR_ENCODING = 'utf-8'

# Media type for path-based references to project tree nodes.
PROJECT_TREE_NODE_PATH_MEDIA_TYPE = 'application/x-scriptaseq-project-tree-node-path'

# Media type for path-based references to sequence component tree nodes.
SEQUENCE_COMPONENT_TREE_NODE_PATH_MEDIA_TYPE = 'application/x-scriptaseq-seq-component-tree-node-path'

def encode_project_tree_node_path(path):
  """Encodes a path-based reference to a project tree node.
  Suitable for use with the PROJECT_TREE_NODE_PATH_MEDIA_TYPE media type. Returns the data as a bytes-like object.
  Raises ValueError if the specified path is relative.
  path -- TreeNamePath to encode.
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

def encode_seq_component_tree_node_path(project_tree_path, seq_component_tree_path):
  """Encodes a path-based reference to a sequence component tree node.
  Suitable for use with the SEQUENCE_COMPONENT_TREE_NODE_PATH_MEDIA_TYPE media type.
  Returns the data as a bytes-like object.
  Raises ValueError if either specified path is relative.
  project_tree_path -- Absolute TreeNamePath giving the path of the project tree node that owns the relevant sequence
    component tree.
  seq_component_tree_path -- Absolute TreeNamePath giving the path of the relevant node in the sequence component tree.
  """
  if not project_tree_path.is_absolute:
    raise ValueError(
      QCoreApplication.translate('MIMEData', 'Cannot encode relative path as project tree node path data.'))
  if not seq_component_tree_path.is_absolute:
    raise ValueError(
      QCoreApplication.translate('MIMEData', 'Cannot encode relative path as sequence component tree node path data.'))
  
  project_tree_path_bytes = str(project_tree_path).encode(MEDIA_STR_ENCODING)
  seq_component_tree_path_bytes = str(seq_component_tree_path).encode(MEDIA_STR_ENCODING)
  return pickle.dumps((project_tree_path_bytes, seq_component_tree_path_bytes))

def decode_seq_component_tree_node_path(data):
  """Decodes a path-based reference to a sequence component tree node.
  Suitable for use with the SEQUENCE_COMPONENT_TREE_NODE_PATH_MEDIA_TYPE media type.
  Returns the decoded paths as a 2-tuple containing the project tree node's absolute path and the sequence component
  node's absolute path.
  """
  project_tree_path_bytes, seq_component_tree_path_bytes = pickle.loads(bytes(data))
  project_tree_path = TreeNamePath.from_str(project_tree_path_bytes.decode(MEDIA_STR_ENCODING))
  seq_component_tree_path = TreeNamePath.from_str(seq_component_tree_path_bytes.decode(MEDIA_STR_ENCODING))
  
  if not project_tree_path.is_absolute:
    raise ValueError(QCoreApplication.translate('MIMEData', 'Expected an absolute path, got a relative path.'))
  if not seq_component_tree_path.is_absolute:
    raise ValueError(QCoreApplication.translate('MIMEData', 'Expected an absolute path, got a relative path.'))
  
  return (project_tree_path, seq_component_tree_path)