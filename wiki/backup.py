import os
import shutil
import time

BACKUPDIR = 'backup'


def create_backup() -> bool:
    """ Create backup of DBNAME in backup/
    return True on success
    """
    src = 'data.db'
    fname = time.strftime('%Y%m%d-%H%M%S.db')
    dst = os.path.join(BACKUPDIR, fname)
    try:
        os.makedirs(BACKUPDIR)
    except FileExistsError:
        pass
    res = shutil.copy(src, dst)
    return res == dst
    if res != dst:
        log.fail('Failed to create backup!')
        msg = 'Failed to create backup!'
    else:
        msg = 'Backup created successfully: <b>' + fname + '</b>'
    ctx = {'v_title': f'Backup Created', 'v_message': msg}
    return flask.render_template('redirect.html', **ctx)
