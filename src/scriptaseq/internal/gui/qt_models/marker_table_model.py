"""Functionality for modeling a marker table in Qt"""
from PyQt5 import QtCore
from PyQt5.Qt import QAbstractListModel, pyqtProperty, QStyledItemDelegate, QModelIndex, QAbstractTableModel

from scriptaseq.internal.gui.project_model import ProjectModel
from scriptaseq.internal.gui.qt_util import make_qcolor


class MarkerTableDelegate(QStyledItemDelegate):
  """Qt table delegate for a table of timeline markers"""
  # TODO

class MarkerTableModel(QAbstractTableModel):
  """Qt table model for a table of timeline markers"""
  
  def __init__(self, parent=None):
    """Constructor
    parent -- The parent QObject
    """
    super().__init__(parent)
    self._project = None
  
  @pyqtProperty(ProjectModel)
  def project(self):
    """Property representing the project to be edited"""
    return self._project
  
  @project.setter
  def project(self, project):
    self.beginResetModel()
    self._project = project
    self.endResetModel()
  
  def rowCount(self, parent=None):
    if self.project is None or (parent is not None and parent.isValid()):
      return 0
    else:
      return len(self.project.active_seq_node.subspace.markers)
  
  def columnCount(self, parent=None):
    return 0 if (parent is not None and parent.isValid()) else 5
  
  def data(self, index, role):
    if index.isValid() and 0 <= index.row() < self.rowCount(None) and 0 <= index.column() < self.columnCount(None) \
      and role == QtCore.Qt.DisplayRole:
      marker = self.project.active_seq_node.subspace.markers[index.row()]
      if index.column() == 0:
        return marker.label
      elif index.column() == 1:
        return str(marker.is_horizontal)
      elif index.column() == 2:
        return str(marker.marked_value)
      elif index.column() == 3:
        return str(marker.repeat_dist) if marker.repeat_dist is not None else str(0)
      elif index.column() == 4:
        return str(make_qcolor(marker.color.red, marker.color.green, marker.color.blue, marker.color.alpha))
    
    # If no data was found, return an invalid value.
    return None
  
  def headerData(self, section, orientation, role):
    if role == QtCore.Qt.DisplayRole and orientation == QtCore.Qt.Horizontal:
      if section == 0:
        return 'Label'
      elif section == 1:
        return 'Horizontal'
      elif section == 2:
        return 'Value'
      elif section == 3:
        return 'Repeat Distance'
      elif section == 4:
        return 'Color'
    
    # If there is no header at the specified location, return an invalid value.
    return None
