"""Widget class for rectangle_editor"""

from PyQt5.Qt import QWidget, pyqtProperty, pyqtSignal
import copy

from scriptaseq.geom import Rectangle
from scriptaseq.internal.generated.qt_ui.rectangle_editor import Ui_RectEditor


class RectEditor(QWidget, Ui_RectEditor):
  
  # Emitted when the rectangle is changed through the GUI.
  rect_edited = pyqtSignal()
  
  def __init__(self, parent=None):
    QWidget.__init__(self, parent)
    self.setupUi(self)
    
    self.xEdit.editingFinished.connect(self._changed_from_gui)
    self.yEdit.editingFinished.connect(self._changed_from_gui)
    self.widthEdit.editingFinished.connect(self._changed_from_gui)
    self.heightEdit.editingFinished.connect(self._changed_from_gui)
    
    self._rect = Rectangle(0, 0, 1, 1)
    
    self.update_form()
  
  @pyqtProperty(Rectangle)
  def rect(self):
    return self._rect
  
  @rect.setter
  def rect(self, rect):
    self._rect = copy.deepcopy(rect)
    self.update_form()
  
  def update_form(self):
    """Updates the GUI to match the rectangle's current state."""
    self.xEdit.setProperty('text', str(float(self._rect.x)))
    self.yEdit.setProperty('text', str(float(self._rect.y)))
    self.widthEdit.setProperty('text', str(float(self._rect.width)))
    self.heightEdit.setProperty('text', str(float(self._rect.height)))
  
  def _changed_from_gui(self):
    """Called when the rectangle has been changed through the GUI.
    Updates internal state to match the GUI.
    """
    try:
      new_x = float(self.xEdit.property('text'))
      new_y = float(self.yEdit.property('text'))
      new_width = float(self.widthEdit.property('text'))
      new_height = float(self.heightEdit.property('text'))
      if new_width < 0 or new_height < 0:
        raise ValueError('Negative rectangle dimension(s)')
      self._rect = Rectangle(new_x, new_y, new_width, new_height)
    
    except ValueError:
      pass
    
    # Update the GUI. For consistent presentation, we do this even if the editing succeeded, so that integers get
    # decimal points added.
    self.update_form()
    
    self.rect_edited.emit()
