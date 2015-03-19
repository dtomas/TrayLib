import os

import gtk

import rox

# These are just for backwards compatibility and may be removed in next
# major version.
from rox.basedir import xdg_config_home as XDG_CONFIG_HOME
from rox.basedir import xdg_config_dirs as XDG_CONFIG_DIRS
from rox.basedir import xdg_data_home as XDG_DATA_HOME
from rox.basedir import xdg_data_dirs as XDG_DATA_DIRS

from traylib import pixmaps


_ = rox.i18n.translation(
    os.path.join(os.path.dirname(os.path.dirname(__file__)), 'Messages')
)


version = (0, 4, 2)

try:
    import wnck
except ImportError:
    wnck = None

# Deprecated.
SCREEN = None
if wnck:
    SCREEN = wnck.screen_get_default()
    SCREEN.force_update()

TOOLTIPS = gtk.Tooltips()
ICON_THEME = gtk.icon_theme_get_default()

TARGET_URI_LIST = 0
TARGET_MOZ_URL = 1
TARGET_WNCK_WINDOW_ID = 2

LEFT = 1
RIGHT = 2
TOP = 3
BOTTOM = 4

XDG_CACHE_HOME = os.getenv("XDG_CACHE_HOME")
if not XDG_CACHE_HOME:
    XDG_CACHE_HOME = os.path.expanduser(os.path.join('~', '.cache'))


APPDIRPATH = os.getenv("APPDIRPATH")
if not APPDIRPATH:
    APPDIRPATH = [os.path.expanduser('~/Apps'),
            '/usr/apps',
            '/usr/lib/apps',
            '/usr/share/apps',
            '/usr/local/apps',
            '/usr/local/lib/apps',
            '/usr/local/share/apps',
            '/opt']
else:
    APPDIRPATH = APPDIRPATH.split(os.pathsep)
