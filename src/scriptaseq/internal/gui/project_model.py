"""Functionality related to project modeling from a GUI perspective"""
from PyQt5.Qt import pyqtProperty, pyqtSignal, QObject

from scriptaseq.geom import Rectangle
from scriptaseq.seq_node import SeqNode


class ProjectModel(QObject):
  """Project wrapper model that adds functionality such as signals to keep the GUI up to date, etc."""
  
  # Emitted when the project is swapped out or reloaded as a whole.
  project_reloaded = pyqtSignal(SeqNode)
  
  # Emitted when the active node is changed.
  active_seq_node_changed = pyqtSignal(SeqNode)
  
  # Emitted when the active node's name is changed.
  active_seq_node_name_changed = pyqtSignal(str)
  
  # Emitted when the timeline boundary for the active node is changed.
  boundary_changed = pyqtSignal(Rectangle)
  
  # Emitted when the grid cell origin and/or dimensions for the active node are changed.
  grid_cell_changed = pyqtSignal(Rectangle)
  
  # Emitted when grid snapping settings for the active node are changed.
  snap_changed = pyqtSignal(tuple)
  
  # Emitted when grid line display settings for the active node are changed.
  show_lines_changed = pyqtSignal(tuple)
  
  # Emitted when a child node is added to the active node.
  child_added = pyqtSignal(SeqNode)
  
  # Emitted when a child node is removed from the active node.
  child_removed = pyqtSignal(str)
  
  # Convenience signal emitted when a change has occurred that might affect the displaying of the grid in the timeline
  # editor.
  grid_display_changed = pyqtSignal()
  
  # Convenience signal emitted when a change has occurred that might affect the displaying of markers in the timeline
  # editor.
  markers_display_changed = pyqtSignal()
  
  # Convenience signal emitted when a change has occurred that might affect the displaying of the timeline editor
  # background.
  timeline_bg_display_changed = pyqtSignal()
  
  # Convenience signal emitted when a change has occurred that might affect the displaying of the timeline properties
  # editor.
  timeline_props_display_changed = pyqtSignal()
  
  def __init__(self, seq_node):
    """Constructor
    seq_node -- Root Sequence Node for the project.
    """
    super().__init__()
    
    self.project_root = seq_node
    
    # Connect more specific signals to more generic ones.
    
    self.project_reloaded.connect(self.grid_display_changed.emit)
    self.active_seq_node_changed.connect(self.grid_display_changed.emit)
    self.boundary_changed.connect(self.grid_display_changed.emit)
    self.grid_cell_changed.connect(self.grid_display_changed.emit)
    self.show_lines_changed.connect(self.grid_display_changed.emit)
    
    self.project_reloaded.connect(self.markers_display_changed.emit)
    self.active_seq_node_changed.connect(self.markers_display_changed.emit)
    self.boundary_changed.connect(self.markers_display_changed.emit)
    
    self.project_reloaded.connect(self.timeline_bg_display_changed.emit)
    self.active_seq_node_changed.connect(self.timeline_bg_display_changed.emit)
    self.boundary_changed.connect(self.timeline_bg_display_changed.emit)
    
    self.project_reloaded.connect(self.timeline_props_display_changed.emit)
    self.active_seq_node_changed.connect(self.timeline_props_display_changed.emit)
    self.active_seq_node_name_changed.connect(self.timeline_props_display_changed.emit)
    self.boundary_changed.connect(self.timeline_props_display_changed.emit)
    self.grid_cell_changed.connect(self.timeline_props_display_changed.emit)
    self.snap_changed.connect(self.timeline_props_display_changed.emit)
    self.show_lines_changed.connect(self.timeline_props_display_changed.emit)
  
  @pyqtProperty(SeqNode)
  def project_root(self):
    """Property containing the root Sequence Node for the project.
    Assigning to this property is regarded as a project reload, and has the side effect of making the root node the
    active node.
    """
    return self._project_root
  
  @project_root.setter
  def project_root(self, project_root):
    self._project_root = project_root
    self._active_seq_node = project_root
    self.project_reloaded.emit(project_root)
    self.active_seq_node_changed.emit(project_root)
  
  @pyqtProperty(SeqNode)
  def active_seq_node(self):
    """Property containing the current active Sequence Node for the project."""
    return self._active_seq_node
  
  @active_seq_node.setter
  def active_seq_node(self, active_seq_node):
    self._active_seq_node = active_seq_node
    self.active_seq_node_changed.emit(active_seq_node)
  
  @pyqtProperty(str)
  def active_seq_node_name(self):
    """Property representing the name of the active Sequence Node"""
    return self.active_seq_node.name
  
  @active_seq_node_name.setter
  def active_seq_node_name(self, active_seq_node_name):
    self.active_seq_node.name = active_seq_node_name
    self.active_seq_node_name_changed.emit(active_seq_node_name)
  
  @pyqtProperty(Rectangle)
  def subspace_boundary(self):
    """Property representing the subspace boundary rectangle of the active Sequence Node"""
    return self.active_seq_node.subspace.boundary
  
  @subspace_boundary.setter
  def subspace_boundary(self, subspace_boundary):
    self.active_seq_node.subspace.boundary = subspace_boundary
    self.boundary_changed.emit(subspace_boundary)
  
  @pyqtProperty(Rectangle)
  def grid_cell(self):
    """Property representing the grid cell rectangle of the active Sequence Node"""
    return self.active_seq_node.subspace.grid_settings.first_cell
  
  @grid_cell.setter
  def grid_cell(self, grid_cell):
    self.active_seq_node.subspace.grid_settings.first_cell = grid_cell
    self.grid_cell_changed.emit(grid_cell)
  
  @pyqtProperty(tuple)
  def grid_snap(self):
    """Property representing the grid snap settings of the active Sequence Node"""
    return self.active_seq_node.subspace.grid_settings.snap_settings
  
  @grid_snap.setter
  def grid_snap(self, grid_snap):
    self.active_seq_node.subspace.grid_settings.snap_settings = grid_snap
    self.snap_changed.emit(grid_snap)
  
  @pyqtProperty(tuple)
  def grid_display(self):
    """Property representing the grid line display settings of the active Sequence Node"""
    return self.active_seq_node.subspace.grid_settings.line_display_settings
  
  @grid_display.setter
  def grid_display(self, grid_display):
    self.active_seq_node.subspace.grid_settings.line_display_settings = grid_display
    self.show_lines_changed.emit(grid_display)
  
  def add_child(self, child):
    """Adds the specified child node to the active Sequence Node.
    The active Sequence Node must not already contain a different child with the same name.
    child -- The child node to add.
    """
    self.active_seq_node.add_child(child)
    self.child_added.emit(child)
  
  def remove_child(self, child_name):
    """Removes the specified child node from the active Sequence Node.
    If no child with the specified name is found, does nothing.
    child_name -- Name of the child to remove.
    """
    self.active_seq_node.remove_child(child_name)
    self.child_removed.emit(child_name)
