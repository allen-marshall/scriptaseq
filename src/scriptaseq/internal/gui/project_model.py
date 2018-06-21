"""Functionality related to project modeling from a GUI perspective"""
from PyQt5.Qt import pyqtProperty, pyqtSignal, QObject

from scriptaseq.geom import Rectangle
from scriptaseq.seq_node import SeqNode


class ProjectModel(QObject):
  """Project wrapper model that adds functionality such as signals to keep the GUI up to date, etc."""
  
  # Emitted when the project is swapped out or reloaded as a whole.
  project_reloaded = pyqtSignal(SeqNode)
  
  # Emitted when the active Sequence Node is changed.
  active_seq_node_changed = pyqtSignal(SeqNode)
  
  # Emitted when a Sequence Node's name is changed.
  node_name_changed = pyqtSignal(SeqNode, str)
  
  # Emitted when the timeline boundary for a Sequence Node is changed.
  boundary_changed = pyqtSignal(SeqNode, Rectangle)
  
  # Emitted when the grid cell origin and/or dimensions for a Sequence Node are changed.
  grid_cell_changed = pyqtSignal(SeqNode, Rectangle)
  
  # Emitted when grid snapping settings for a Sequence Node are changed.
  snap_changed = pyqtSignal(SeqNode, bool, bool)
  
  # Emitted when grid line display settings for a Sequence Node are changed.
  show_lines_changed = pyqtSignal(SeqNode, bool, bool)
  
  # Emitted when a child node has been added to a parent node. The first argument is the parent, and the second is the
  # child.
  child_added = pyqtSignal(SeqNode, SeqNode)
  
  # Emitted when a child node has been removed from a parent node. The first argument is the parent, and the second is
  # the child.
  child_removed = pyqtSignal(SeqNode, SeqNode)
  
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
    self.node_name_changed.connect(self.timeline_props_display_changed.emit)
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
  
  def set_node_name(self, node, name):
    """Sets the name for the specified node, and emits any appropriate signals.
    node -- The Sequence Node to change.
    name -- The new name. If node has a parent, the parent must not already have another child with the specified name.
    """
    node.name = name
    self.node_name_changed.emit(node, name)
  
  def set_subspace_boundary(self, node, boundary):
    """Sets the subspace boundary for the specified node, and emits any appropriate signals.
    node -- The Sequence Node to change.
    boundary -- The new boundary rectangle.
    """
    node.subspace.boundary = boundary
    self.boundary_changed.emit(node, boundary)
  
  def set_grid_cell(self, node, grid_cell):
    """Sets the grid cell rectangle for the specified node, and emits any appropriate signals.
    node -- The Sequence Node to change.
    grid_cell -- The new grid cell rectangle.
    """
    node.subspace.grid_settings.first_cell = grid_cell
    self.grid_cell_changed.emit(node, grid_cell)
  
  def set_grid_snap(self, node, grid_snap):
    """Sets the grid snap configuration for the specified node, and emits any appropriate signals.
    node -- The Sequence Node to change.
    grid_snap -- The new grid snap settings.
    """
    node.subspace.grid_settings.snap_settings = grid_snap
    self.snap_changed.emit(node, *grid_snap)
  
  def set_grid_display(self, node, grid_display):
    """Sets the grid display configuration for the specified node, and emits any appropriate signals.
    node -- The Sequence Node to change.
    grid_display -- The new grid display settings.
    """
    node.subspace.grid_settings.line_display_settings = grid_display
    self.show_lines_changed.emit(node, *grid_display)
  
  def add_child(self, parent, child):
    """Adds the specified child node to the specified parent node.
    The parent node must not already contain a different child with the same name.
    parent -- The parent node.
    child -- The child node to add.
    """
    parent.add_child(child)
    self.child_added.emit(parent, child)
  
  def remove_child(self, parent, child_name):
    """Removes the specified child node from the specified parent node.
    If no child with the specified name is found, does nothing.
    parent -- The parent node.
    child_name -- Name of the child to remove.
    """
    if child_name in parent.children:
      child = parent.children[child_name]
      parent.remove_child(child_name)
      self.child_removed.emit(parent, child)
