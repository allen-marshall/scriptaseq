"""Functionality related to playback of Sequence Nodes during dragging"""

# Script role to trigger when dragging of a Sequence Node starts.
DRAG_START_ROLE = 'drag.start'

# Script role to trigger (between start and end of dragging) when a Sequence Node is changed by dragging.
DRAG_MOVED_ROLE = 'drag.move'

# Script role to trigger when a dragging of a Sequence Node ends.
DRAG_END_ROLE = 'drag.end'

class DragPlaybackOperation:
  """Manages playback state during a drag operation."""
  
  # TODO