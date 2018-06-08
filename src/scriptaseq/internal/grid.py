"""Functionality related to grid display and snapping"""

# TODO: Probably remove this file.

# Default grid settings.
DEFAULT_SNAP = True
DEFAULT_DIVS_PER_BEAT = 4

class GridBehavior:
  """Represents settings for grid and snapping behavior."""
  
  def __init__(self, snap=DEFAULT_SNAP, divs_per_beat=DEFAULT_DIVS_PER_BEAT):
    """Constructor
    snap -- Boolean indicating whether to snap objects to the grid.
    divs_per_beat -- Number of grid divisions per beat. Need not be an integer. If snapping is disabled, the
      grids-per-beat value should only affect the displaying of the grid.
    """
    self.snap = snap
    self.divs_per_beat = divs_per_beat