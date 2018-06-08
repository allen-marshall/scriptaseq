"""Utilities related to interacting with Qt"""

from PyQt5.Qt import QColor

def make_qcolor(red=0, green=0, blue=0, alpha=1):
  """Makes a QColor with specified component values.
  red -- Red component. Should be in the range [0, 1].
  green -- Green component. Should be in the range [0, 1].
  blue -- Blue component. Should be in the range [0, 1].
  alpha -- Alpha component. Should be in the range [0, 1].
  """
  scaled_comps = [round(comp * 255) for comp in (red, green, blue, alpha)]
  return QColor(*scaled_comps)