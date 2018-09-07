"""Defines the widget class for displaying the project tree."""
from PyQt5.Qt import QWidget

from scriptaseq.internal.generated.qt_ui.project_tree_widget import Ui_ProjectTreeWidget


class ProjectTreeWidget(QWidget, Ui_ProjectTreeWidget):
  """Widget for displaying the project tree."""
  
  def __init__(self, undo_stack, project_tree_qt_model, project_tree_controller, parent=None):
    """Constructor.
    undo_stack -- QUndoStack to receive undoable editing commands generated by this widget.
    project_tree_qt_model -- ProjectTreeQtModel responsible for some of the tree display functionality.
    project_tree_controller -- ProjectTreeController in charge of high-level changes to the project tree.
    parent -- Parent QObject.
    """
    QWidget.__init__(self, parent)
    self.setupUi(self)
    
    self._undo_stack = undo_stack
    self._project_tree_controller = project_tree_controller
    
    self.projectTreeView.setModel(project_tree_qt_model)
  
  def contextMenuEvent(self, event):
    # Get event position relative to the project tree view.
    tree_view_pos = self.projectTreeView.viewport().mapFromGlobal(event.globalPos())
    
    # If the event occurred inside the project tree view, show a context menu for the appropriate project tree node.
    if self.projectTreeView.viewport().rect().contains(tree_view_pos):
      qt_index = self.projectTreeView.indexAt(tree_view_pos)
      node = self.projectTreeView.model().qt_index_to_node(qt_index)
      
      menu = node.make_context_menu(self._undo_stack, self._project_tree_controller, self)
      if menu is not None and not menu.isEmpty():
        event.setAccepted(True)
        menu.exec_(event.globalPos())