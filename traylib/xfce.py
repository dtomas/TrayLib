import os

import rox

from rox.basedir import xdg_data_dirs


def install_panel_plugin(name, start_script):
    for data_dir in xdg_data_dirs:
        panel_plugins_dir = os.path.join(data_dir, 'xfce4', 'panel-plugins')
        if os.path.isdir(panel_plugins_dir):
            break
    else:
        rox.croak("XFCE4 panel plugins directory not found!")
        return

    with open(os.path.join(panel_plugins_dir, '%s.desktop' % name), 'w') as f:
        f.write('[Xfce Panel]\n')
        f.write('Name=%s\n' % name)
        f.write('Icon=%s\n' % os.path.join(rox.app_dir, '.DirIcon'))
        f.write('X-XFCE-Exec=%s\n' % os.path.join(rox.app_dir, start_script))

    rox.info("%s has been installed as XFCE panel plugin." % name)
