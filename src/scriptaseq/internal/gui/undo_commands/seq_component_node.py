"""Contains QUndoCommand subclasses related to operations on individual nodes in a sequence component tree."""

from scriptaseq.internal.gui.undo_commands.id_gen import gen_undo_id, UndoCommandWithClassBasedID
from PyQt5.Qt import QCoreApplication


class BaseSequenceComponentNodeUndoCommand(UndoCommandWithClassBasedID):
  """Base class for QUndoCommands related to operations on individual nodes in a sequence component tree."""
  
  undo_id = gen_undo_id()
  
  def __init__(self, seq_component_node_controller, parent=None):
    """Constructor.
    seq_component_node_controller -- Reference to the SequenceComponentNodeController in charge of making changes to
      individual nodes in the sequence component tree.
    parent -- Parent QUndoCommand.
    """
    super().__init__(parent)
    self.seq_component_node_controller = seq_component_node_controller

class SetComponentTypeCommand(BaseSequenceComponentNodeUndoCommand):
  """QUndoCommand class for changing the component type of a sequence component tree node."""
  
  undo_id = gen_undo_id()
  
  def __init__(self, seq_component_node_controller, node, new_component_type, parent=None):
    """Constructor.
    seq_component_node_controller -- Reference to the SequenceComponentNodeController in charge of making changes to
      individual nodes in the sequence component tree.
    node -- Sequence component tree node whose component type is to be changed.
    new_component_type -- New component type for the node.
    parent -- Parent QUndoCommand.
    """
    super().__init__(seq_component_node_controller, parent)
    
    self._node = node
    self._old_component_type = node.component_type
    self._new_component_type = new_component_type
    
    self.setObsolete(self._old_component_type == self._new_component_type)
    self.setText(
      QCoreApplication.translate('SetComponentTypeCommand', "Change Type of '{}' to {}").format(node.name, new_component_type.display_name))
  
  def redo(self):
    self.seq_component_node_controller.set_component_type(self._node, self._new_component_type)
  
  def undo(self):
    self.seq_component_node_controller.set_component_type(self._node, self._old_component_type)