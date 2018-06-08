"""Functionality related to real-time playback of a Sequence Node tree"""

# Script role to trigger in order to compute the start and end times of a Sequence Node.
RT_PLAYBACK_TIME_ROLE = 'playback.get_time'

# Script role to trigger when real-time playback of a Sequence Node begins.
RT_PLAYBACK_START_ROLE = 'playback.start'

# Script role to trigger when real-time playback of a Sequence Node ends.
RT_PLAYBACK_END_ROLE = 'playback.end'

# TODO: Figure out how this should be implemented. It should probably run in a background thread so it can sleep or
# otherwise wait for scheduled event times.