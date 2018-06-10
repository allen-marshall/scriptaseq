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

def fit_item_to_region(item, region):
  """Fits a Qt Quick item to the specified region by modifying its position and dimensions.
  item -- The Qt Quick item to fit. Nothing is done if this is None.
  region -- Rectangle object specifying the desired region, in units of pixels relative to the item's parent.
  """
  item.setProperty('x', region.x)
  item.setProperty('y', region.y)
  item.setProperty('width', region.width)
  item.setProperty('height', region.height)