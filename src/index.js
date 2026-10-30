import { Dialog, ToolbarButton, showDialog } from '@jupyterlab/apputils';
import { URLExt } from '@jupyterlab/coreutils';
import { ServerConnection } from '@jupyterlab/services';

const plugin = {
    id: 'jupyterlab-poweroff:plugin',
    description: 'Power off the Linux host after confirmation.',
    autoStart: true,
    activate: (app) => {

        let shuttingDown = false;

        const poweroff = async () => {

            if (shuttingDown) {
                return;
            }

            const confirmation = await showDialog({
                title: 'Power off this machine?',
                body: 'All running notebooks, kernels and processes will be stopped.',
                buttons: [Dialog.cancelButton(), Dialog.warnButton({ label: 'Power off' })],
            });

            if (!confirmation.button.accept) {
                return;
            }

            shuttingDown = true;

            try {

                const settings = ServerConnection.makeSettings();
                const url = URLExt.join(settings.baseUrl, 'api', 'poweroff');
                const response = await ServerConnection.makeRequest(url, { method: 'POST' }, settings);

                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}: ${await response.text()}`);
                }

            } catch (error) {

                shuttingDown = false;

                await showDialog({
                    title: 'Power off failed',
                    body: String(error),
                    buttons: [Dialog.okButton()],
                });
            }
        };

        const button = new ToolbarButton({
            label: 'Power off',
            tooltip: 'Power off the Linux machine',
            onClick: () => { void poweroff(); },
        });

        button.id = 'jp-jupyterlab-poweroff';
        app.shell.add(button, 'top', { rank: 1000 });
    },
};

export default plugin;
