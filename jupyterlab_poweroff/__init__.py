########################################################################################################################

import subprocess

from jupyter_server.base.handlers import JupyterHandler
from jupyter_server.utils import url_path_join

from tornado import web
from tornado.ioloop import IOLoop

########################################################################################################################

POWEROFF_COMMAND = ['/usr/bin/sudo', '-n', '/usr/bin/systemctl', 'poweroff']
REBOOT_COMMAND = ['/usr/bin/sudo', '-n', '/usr/bin/systemctl', 'reboot']

########################################################################################################################
# POWEROFF                                                                                                             #
########################################################################################################################

def _is_poweroff_authorized():

    try:

        result = subprocess.run(
            ['/usr/bin/sudo', '-n', '-l', '/usr/bin/systemctl', 'poweroff'],
            stdin = subprocess.DEVNULL,
            stdout = subprocess.DEVNULL,
            stderr = subprocess.DEVNULL,
            timeout = 5,
            check = False,
        )

        return result.returncode == 0

    except (OSError, subprocess.TimeoutExpired):

        return False


########################################################################################################################

def _poweroff():

    subprocess.Popen(
        POWEROFF_COMMAND,
        stdin = subprocess.DEVNULL,
        stdout = subprocess.DEVNULL,
        stderr = subprocess.DEVNULL,
        start_new_session = True,
    )

########################################################################################################################
# POWEROFF HANDLER                                                                                                     #
########################################################################################################################

class PoweroffHandler(JupyterHandler):

    @web.authenticated
    async def post(self):

        if not _is_poweroff_authorized():

            raise web.HTTPError(403, 'Poweroff is not authorized for the JupyterLab user')

        self.set_status(202)
        self.finish({'status': 'accepted'})

        IOLoop.current().call_later(1.0, _poweroff)

########################################################################################################################
# REBOOT                                                                                                               #
########################################################################################################################

def _is_reboot_authorized():

    try:

        result = subprocess.run(
            ['/usr/bin/sudo', '-n', '-l', '/usr/bin/systemctl', 'reboot'],
            stdin = subprocess.DEVNULL,
            stdout = subprocess.DEVNULL,
            stderr = subprocess.DEVNULL,
            timeout = 5,
            check = False,
        )

        return result.returncode == 0

    except (OSError, subprocess.TimeoutExpired):

        return False


########################################################################################################################

def _reboot():

    subprocess.Popen(
        REBOOT_COMMAND,
        stdin = subprocess.DEVNULL,
        stdout = subprocess.DEVNULL,
        stderr = subprocess.DEVNULL,
        start_new_session = True,
    )

########################################################################################################################
# REBOOT HANDLER                                                                                                       #
########################################################################################################################

class RebootHandler(JupyterHandler):

    @web.authenticated
    async def post(self):

        if not _is_reboot_authorized():

            raise web.HTTPError(403, 'Reboot is not authorized for the JupyterLab user')

        self.set_status(202)
        self.finish({'status': 'accepted'})

        IOLoop.current().call_later(1.0, _reboot)

########################################################################################################################
# JUPYTER SERVER EXTENSION                                                                                             #
########################################################################################################################

def _jupyter_server_extension_points():

    return [{'module': 'jupyterlab_poweroff'}]


########################################################################################################################

def _load_jupyter_server_extension(serverapp):

    serverapp.web_app.add_handlers('.*$', [
        (url_path_join(serverapp.web_app.settings['base_url'], 'api', 'poweroff'), PoweroffHandler),
        (url_path_join(serverapp.web_app.settings['base_url'], 'api', 'reboot'), RebootHandler),
    ])

########################################################################################################################
