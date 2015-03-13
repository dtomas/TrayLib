import sys
import os

import rox

from traylib import XDG_DATA_DIRS


def install_panel_plugin(name, start_script):
    for data_dir in XDG_DATA_DIRS:
        panel_plugins_dir = os.path.join(data_dir, 'xfce4', 'panel-plugins')
        if os.path.isdir(panel_plugins_dir):
            break
    else:
        rox.croak("XFCE4 panel plugins directory not found!")
        sys.exit(1)

    with open(os.path.join(panel_plugins_dir, '%s.desktop' % name), 'w') as f:
        f.write('[Xfce Panel]\n')
        f.write('Name=%s\n' % name)
        f.write('Icon=%s\n' % os.path.join(rox.app_dir, '.DirIcon'))
        f.write('X-XFCE-Exec=%s\n' % os.path.join(rox.app_dir, start_script))

    rox.info("MediaTray has been installed as XFCE panel plugin.")
