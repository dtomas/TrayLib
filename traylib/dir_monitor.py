import gobject, os

MONITOR_TYPE_NONE = 0
MONITOR_TYPE_GAMIN = 1
MONITOR_TYPE_FAM = 2

_monitor_type = MONITOR_TYPE_NONE
try:
    import gamin
    _monitor_type = MONITOR_TYPE_GAMIN
except ImportError:
    try:
        import _fam
        _monitor_type = MONITOR_TYPE_FAM
    except ImportError:
        pass

if _monitor_type == MONITOR_TYPE_GAMIN:
    _monitor = gamin.WatchMonitor()
    EVENT_CREATED = gamin.GAMCreated
    EVENT_DELETED = gamin.GAMDeleted
    EVENT_CHANGED = gamin.GAMChanged
elif _monitor_type == MONITOR_TYPE_FAM:
    _fam_conn = _fam.open()
    EVENT_CREATED = _fam.Created
    EVENT_DELETED = _fam.Deleted
    EVENT_CHANGED = _fam.Changed
    
_objects = {}
    
def _event(leaf, event, path):
    for obj in _objects[path]:
        if event == EVENT_CREATED:
            if hasattr(obj, 'file_created'):
                obj.file_created(path, leaf)
        elif event == EVENT_DELETED:
            if hasattr(obj, 'file_deleted'):
                obj.file_deleted(path, leaf)
        elif event == EVENT_CHANGED:
            if hasattr(obj, 'file_changed'):
                obj.file_changed(path, leaf)

def add(dir, obj):
    if _monitor_type == MONITOR_TYPE_GAMIN:
        if os.path.isdir(dir):
            _monitor.watch_directory(dir, _event, dir)
        else:
            _monitor.watch_file(dir, _event, dir)
    elif _monitor_type == MONITOR_TYPE_FAM:
        if os.path.isdir(dir):
            fam_request = _fam_conn.monitorDirectory(dir, None)
        else:
            fam_request = _fam_conn.monitorFile(dir, None)
    else:
        return
    _objects.setdefault(dir, set()).add(obj)

def _watch():
    if _monitor_type == MONITOR_TYPE_GAMIN:
        _monitor.handle_events()
    elif _monitor_type == MONITOR_TYPE_FAM:
        while _fam_conn.pending():
            fam_event = _fam_conn.nextEvent()
            _event(fam_event.filename, fam_event.code, )
    else:
        return False
    return True

gobject.timeout_add(1000, _watch)
