import rox, gtk, os
import pixmaps

version = (0, 3, 0)

try:
    import wnck
except ImportError:
    wnck = None

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

XDG_DATA_DIRS = os.getenv("XDG_DATA_DIRS")
if not XDG_DATA_DIRS:
    XDG_DATA_DIRS = ['/usr/share', '/usr/local/share']
else:
    XDG_DATA_DIRS = XDG_DATA_DIRS.split(os.pathsep)
    
XDG_CONFIG_DIRS = os.getenv("XDG_CONFIG_DIRS")
if XDG_CONFIG_DIRS:
    XDG_CONFIG_DIRS = XDG_CONFIG_DIRS.split(':')
else:
    XDG_CONFIG_DIRS = ['/etc/xdg']

XDG_CONFIG_HOME = os.getenv("XDG_CONFIG_HOME")
if XDG_CONFIG_HOME:
    XDG_CONFIG_DIRS.append(XDG_CONFIG_HOME)
else:
    XDG_CONFIG_HOME = os.path.expanduser('~/.config')
    XDG_CONFIG_DIRS.insert(0, XDG_CONFIG_HOME)

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
