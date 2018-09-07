"""Defines the widget class for displaying the sequence component tree."""
from PyQt5.Qt import QWidget

from scriptaseq.internal.generated.qt_ui.seq_component_tree_widget import Ui_SequenceComponentTreeWidget


class SequenceComponentTreeWidget(QWidget, Ui_SequenceComponentTreeWidget):
  """Widget for displaying the sequence component tree."""
  
  def __init__(self, seq_component_tree_qt_model, parent=None):
    """Constructor.
    seq_component_tree_qt_model -- SequenceComponentTreeQtModel responsible for some of the tree display functionality.
    parent -- Parent QObject.
    """
    QWidget.__init__(self, parent)
    self.setupUi(self)
    
    self.seqComponentTreeView.setModel(seq_component_tree_qt_model)