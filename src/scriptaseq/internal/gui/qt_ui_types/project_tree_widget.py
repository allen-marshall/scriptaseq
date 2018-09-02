"""Defines the widget class for displaying the project tree."""
from PyQt5.Qt import QWidget

from scriptaseq.internal.generated.qt_ui.project_tree_widget import Ui_ProjectTreeWidget


class ProjectTreeWidget(QWidget, Ui_ProjectTreeWidget):
  """Widget for displaying the project tree."""
  
  def __init__(self, project_tree_qt_model, parent=None):
    """Constructor.
    project_tree_qt_model -- ProjectTreeQtModel responsible for some of the tree display functionality.
    parent -- Parent QObject.
    """
    QWidget.__init__(self, parent)
    self.setupUi(self)
    
    self.projectTreeView.setModel(project_tree_qt_model)