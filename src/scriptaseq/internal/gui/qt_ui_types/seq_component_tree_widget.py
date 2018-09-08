"""Defines the widget class for displaying the sequence component tree."""
from PyQt5.Qt import QWidget, QModelIndex

from scriptaseq.internal.generated.qt_ui.seq_component_tree_widget import Ui_SequenceComponentTreeWidget


class SequenceComponentTreeWidget(QWidget, Ui_SequenceComponentTreeWidget):
  """Widget for displaying the sequence component tree."""
  
  def __init__(self, undo_stack, seq_component_tree_qt_model, project_tree_controller, seq_component_tree_controller,
    seq_component_node_controller, parent=None):
    """Constructor.
    undo_stack -- QUndoStack to receive undoable editing commands generated by this widget.
    seq_component_tree_qt_model -- SequenceComponentTreeQtModel responsible for some of the tree display functionality.
    project_tree_controller -- ProjectTreeController in charge of high-level changes to the project tree.
    seq_component_tree_controller -- SequenceComponentTreeController in charge of high-level changes to the sequence
      component tree.
    seq_component_node_controller -- SequenceComponentNodeController in charge of making changes to individual nodes in
      the sequence component tree.
    parent -- Parent QObject.
    """
    QWidget.__init__(self, parent)
    self.setupUi(self)
    
    self._undo_stack = undo_stack
    self._project_tree_controller = project_tree_controller
    self._seq_component_tree_qt_model = seq_component_tree_qt_model
    self._seq_component_tree_controller = seq_component_tree_controller
    self._seq_component_node_controller = seq_component_node_controller
    
    self.seqComponentTreeView.setModel(seq_component_tree_qt_model)
    
    seq_component_tree_qt_model.modelReset.connect(lambda: self._current_selected_node_changed(QModelIndex()))
    self.seqComponentTreeView.selectionModel().currentChanged.connect(
      lambda new_qt_index, _: self._current_selected_node_changed(new_qt_index))
  
  def _current_selected_node_changed(self, new_qt_index):
    """Should be called after the current selected node in the sequence component tree view has changed.
    new_qt_index -- Qt index of the new current selected node. An invalid Qt index means there is no current selected
      node.
    """
    new_active_node = None if not new_qt_index.isValid() \
      else self._seq_component_tree_qt_model.qt_index_to_node(new_qt_index)
    self._seq_component_tree_controller.active_node = new_active_node
  
  def contextMenuEvent(self, event):
    # Get event position relative to the sequence component tree view.
    tree_view_pos = self.seqComponentTreeView.viewport().mapFromGlobal(event.globalPos())
    
    # If the event occurred inside the sequence component tree view, show a context menu for the appropriate sequence
    # component tree node.
    if self.seqComponentTreeView.viewport().rect().contains(tree_view_pos):
      qt_index = self.seqComponentTreeView.indexAt(tree_view_pos)
      node = self.seqComponentTreeView.model().qt_index_to_node(qt_index)
      
      if node is not None:
        menu = node.make_context_menu(self._undo_stack, self._seq_component_tree_controller,
          self._seq_component_node_controller, self)
        if menu is not None and not menu.isEmpty():
          event.setAccepted(True)
          menu.exec_(event.globalPos())