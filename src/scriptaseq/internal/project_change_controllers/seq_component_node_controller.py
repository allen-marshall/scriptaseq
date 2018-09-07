"""Defines a controller class for making changes to individual nodes in sequence component trees."""

from PyQt5.Qt import QObject, pyqtSignal

from scriptaseq.internal.seq_component_tree.component_tree_nodes import SequenceComponentNode


class SequenceComponentNodeController(QObject):
  """Controller class for making changes to individual nodes in sequence component trees.
  Note that this class does not internally support undo/redo functionality, so its methods that change project state
  should generally be called only from within subclasses of QUndoCommand.
  """
  
  # Signal emitted when a sequence component node's component type has been changed.
  # Arguments:
  # - Reference to the SequenceComponentNode whose component type has been changed.
  # - BaseSequenceComponentType subclass representing the new component type.
  # - BaseSequenceComponentType subclass representing the old component type.
  node_component_type_changed = pyqtSignal(SequenceComponentNode, type, type)
  
  def set_component_type(self, node, new_component_type):
    """Sets the component type for a sequence component tree node.
    node -- Sequence component tree node whose component type is to be changed.
    new_component_type -- New component type for the node.
    """
    # Do nothing if the node already has the specified component type.
    if node.component_type == new_component_type:
      return
    
    old_component_type = node.component_type
    
    # Perform the change.
    node.component_type = new_component_type
    
    # Send out appropriate signals to notify GUI components.
    self.node_component_type_changed.emit(node, new_component_type, old_component_type)