########################################################################################################################

from unittest.mock import Mock
from unittest.mock import patch

import jupyterlab_poweroff

########################################################################################################################

def test_extension_points():

    assert jupyterlab_poweroff._jupyter_server_extension_points() == [{'module': 'jupyterlab_poweroff'}]


########################################################################################################################

def test_permission_granted():

    with patch('jupyterlab_poweroff.subprocess.run', return_value = Mock(returncode = 0)) as run:

        assert jupyterlab_poweroff._is_poweroff_authorized()
        assert run.call_args.args[0] == ['/usr/bin/sudo', '-n', '-l', '/usr/bin/systemctl', 'poweroff']


########################################################################################################################

def test_permission_denied():

    with patch('jupyterlab_poweroff.subprocess.run', return_value = Mock(returncode = 1)):

        assert not jupyterlab_poweroff._is_poweroff_authorized()


########################################################################################################################

def test_poweroff_command():

    with patch('jupyterlab_poweroff.subprocess.Popen') as popen:

        jupyterlab_poweroff._poweroff()
        assert popen.call_args.args[0] == ['/usr/bin/sudo', '-n', '/usr/bin/systemctl', 'poweroff']
        assert popen.call_args.kwargs['start_new_session'] is True

########################################################################################################################

def test_register_handler_respects_base_url():

    from unittest.mock import Mock

    serverapp = Mock()
    serverapp.web_app.settings = {'base_url': '/jupyter/'}

    jupyterlab_poweroff._load_jupyter_server_extension(serverapp)

    route = serverapp.web_app.add_handlers.call_args.args[1][0][0]
    assert route == '/jupyter/api/poweroff'


########################################################################################################################

def test_permission_check_handles_missing_sudo():

    with patch('jupyterlab_poweroff.subprocess.run', side_effect = OSError('sudo not found')):

        assert not jupyterlab_poweroff._is_poweroff_authorized()

########################################################################################################################

########################################################################################################################
# REBOOT TESTS                                                                                                         #
########################################################################################################################

def test_reboot_permission_granted():

    with patch('jupyterlab_poweroff.subprocess.run', return_value = Mock(returncode = 0)) as run:

        assert jupyterlab_poweroff._is_reboot_authorized()
        assert run.call_args.args[0] == ['/usr/bin/sudo', '-n', '-l', '/usr/bin/systemctl', 'reboot']


########################################################################################################################

def test_reboot_permission_denied():

    with patch('jupyterlab_poweroff.subprocess.run', return_value = Mock(returncode = 1)):

        assert not jupyterlab_poweroff._is_reboot_authorized()


########################################################################################################################

def test_reboot_command():

    with patch('jupyterlab_poweroff.subprocess.Popen') as popen:

        jupyterlab_poweroff._reboot()
        assert popen.call_args.args[0] == ['/usr/bin/sudo', '-n', '/usr/bin/systemctl', 'reboot']
        assert popen.call_args.kwargs['start_new_session'] is True


########################################################################################################################

def test_register_reboot_handler_respects_base_url():

    serverapp = Mock()
    serverapp.web_app.settings = {'base_url': '/jupyter/'}

    jupyterlab_poweroff._load_jupyter_server_extension(serverapp)

    route, handler = serverapp.web_app.add_handlers.call_args.args[1][1]
    assert route == '/jupyter/api/reboot'
    assert handler == jupyterlab_poweroff.RebootHandler


########################################################################################################################

def test_reboot_permission_check_handles_missing_sudo():

    with patch('jupyterlab_poweroff.subprocess.run', side_effect = OSError('sudo not found')):

        assert not jupyterlab_poweroff._is_reboot_authorized()

########################################################################################################################
