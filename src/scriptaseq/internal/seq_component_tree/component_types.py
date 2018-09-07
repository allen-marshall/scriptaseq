"""Defines objects representing the supported types of nodes in a sequence component tree."""

from PyQt5.Qt import QIcon, QCoreApplication

from scriptaseq.internal.gui.qt_util import make_multires_icon


class BaseSequenceComponentType:
  """Base class for sequence component node types."""
  
  # The user-visible name for this component type. Subclasses should override this.
  display_name = QCoreApplication.translate('BaseComponentType', 'Base Component')
  
  # The user-visible text to display on QMenu items representing this component type. Can contain an ampersand to
  # specify the keyboard shortcut for the menu item.
  menu_text = QCoreApplication.translate('BaseComponentType', '&Base Component')
  
  # A unique name for this component type, for use in save files, etc. Subclasses should override this.
  internal_name = 'BaseComponent'
  
  # TODO: Add a memoization decorator to this method.
  @classmethod
  def get_icon(cls):
    """Gets a QIcon representing this component type, creating it if it has not been previously created.
    This method should not be called before the Qt application's resource loading configuration has been set up.
    Subclasses should generally override make_icon instead of this method.
    """
    return cls.make_icon()
  
  @classmethod
  def make_icon(cls):
    """Makes a QIcon representing this component type.
    This method should not be called before the Qt application's resource loading configuration has been set up.
    Subclasses should override this. Default implementation returns an empty QIcon.
    """
    return QIcon()

class ContainerSequenceComponentType(BaseSequenceComponentType):
  """Sequence component node type for container nodes."""
  
  display_name = QCoreApplication.translate('ContainerSequenceComponentType', 'Container')
  
  menu_text = QCoreApplication.translate('ContainerSequenceComponentType', '&Container')
  
  internal_name = 'Container'
  
  @classmethod
  def make_icon(cls):
    return make_multires_icon(':/icons/sequence_component_tree/container')

class NoteSequenceComponentType(BaseSequenceComponentType):
  """Sequence component type for note nodes."""
  
  display_name = QCoreApplication.translate('NoteSequenceComponentType', 'Note')
  
  menu_text = QCoreApplication.translate('NoteSequenceComponentType', '&Note')
  
  internal_name = 'Note'
  
  @classmethod
  def make_icon(cls):
    return make_multires_icon(':/icons/sequence_component_tree/note')

class AutomationSequenceComponentType(BaseSequenceComponentType):
  """Sequence component type for automation nodes."""
  
  display_name = QCoreApplication.translate('AutomationSequenceComponentType', 'Automation')
  
  menu_text = QCoreApplication.translate('AutomationSequenceComponentType', '&Automation')
  
  internal_name = 'Automation'
  
  @classmethod
  def make_icon(cls):
    return make_multires_icon(':/icons/sequence_component_tree/automation')

class WaveTableSequenceComponentType(BaseSequenceComponentType):
  """Sequence component type for wave table nodes."""
  
  display_name = QCoreApplication.translate('WaveTableSequenceComponentType', 'Wave Table')
  
  menu_text = QCoreApplication.translate('WaveTableSequenceComponentType', '&Wave Table')
  
  internal_name = 'WaveTable'
  
  @classmethod
  def make_icon(cls):
    return make_multires_icon(':/icons/sequence_component_tree/wave_table')

# Sequence that lists the supported sequence component types that should be available through the GUI.
SUPPORTED_COMPONENT_TYPES = (ContainerSequenceComponentType, NoteSequenceComponentType, AutomationSequenceComponentType,
  WaveTableSequenceComponentType)