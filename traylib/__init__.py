import os

from gi.repository import Gtk

import rox

_ = rox.i18n.translation(
    os.path.join(os.path.dirname(os.path.dirname(__file__)), 'Messages')
)


version = (3, 0, 0)

try:
    import gi
    gi.require_version('Wnck', '3.0')
    from gi.repository import Wnck
except ImportError:
    Wnck = None

ICON_THEME = Gtk.IconTheme.get_default()

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
    APPDIRPATH = [
        os.path.expanduser('~/Apps'),
        '/usr/apps',
        '/usr/lib/apps',
        '/usr/share/apps',
        '/usr/local/apps',
        '/usr/local/lib/apps',
        '/usr/local/share/apps',
        '/opt',
    ]
else:
    APPDIRPATH = APPDIRPATH.split(os.pathsep)
