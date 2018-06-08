"""Utilities related to interacting with Qt"""

from PyQt5.Qt import QSGGeometry, QSGGeometryNode, QSGFlatColorMaterial, QColor

def make_qcolor(red=0, green=0, blue=0, alpha=1):
  """Makes a QColor with specified component values.
  red -- Red component. Should be in the range [0, 1].
  green -- Green component. Should be in the range [0, 1].
  blue -- Blue component. Should be in the range [0, 1].
  alpha -- Alpha component. Should be in the range [0, 1].
  """
  scaled_comps = [round(comp * 255) for comp in (red, green, blue, alpha)]
  return QColor(*scaled_comps)

def make_or_reuse_geom_node(old_node):
  """Returns old_node if old_node is not None, otherwise creates a new geometry node.
  old_node -- Node to return, or None to create a new geometry node.
  """
  if old_node is None:
    return QSGGeometryNode()
  else:
    return old_node

def make_or_reuse_geom(old_node, attrs, num_vertices):
  """Extracts the geometry from old_node if old_node is not None, otherwise creates a new geometry object.
  old_node -- Node from which to try to reuse a QSGGeometry object.
  attrs -- Attributes for the QSGGeometry object in case a new one has to be made.
  num_vertices -- Number of vertices desired in the new geometry object.
  """
  if old_node is None:
    geom = QSGGeometry(attrs, num_vertices)
  else:
    geom = old_node.geometry()
    if geom.vertexCount() != num_vertices:
      geom.allocate(num_vertices)
  
  return geom

def make_or_reuse_flat_mat(old_node):
  """Extracts the material from old_node if old_node is not None, otherwise creates a new flat color material.
  old_node -- Node from which to try to reuse a QSGFlatColorMaterial.
  """
  if old_node is None:
    mat = QSGFlatColorMaterial()
  else:
    mat = old_node.material()
  
  return mat