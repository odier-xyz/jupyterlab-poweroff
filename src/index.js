import { Dialog, ToolbarButton, showDialog } from '@jupyterlab/apputils';
import { URLExt } from '@jupyterlab/coreutils';
import { ServerConnection } from '@jupyterlab/services';

const plugin = {
    id: 'jupyterlab-poweroff:plugin',
    description: 'Power off or reboot the Linux host after confirmation.',
    autoStart: true,
    activate: (app) => {

        let shuttingDown = false;

        const runAction = async (action, label) => {

            if (shuttingDown) {
                return;
            }

            const confirmation = await showDialog({
                title: `${label} this machine?`,
                body: 'All running notebooks, kernels and processes will be stopped.',
                buttons: [Dialog.cancelButton(), Dialog.warnButton({ label })],
            });

            if (!confirmation.button.accept) {
                return;
            }

            shuttingDown = true;

            try {

                const settings = ServerConnection.makeSettings();
                const url = URLExt.join(settings.baseUrl, 'api', action);
                const response = await ServerConnection.makeRequest(url, { method: 'POST' }, settings);

                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}: ${await response.text()}`);
                }

            } catch (error) {

                shuttingDown = false;

                await showDialog({
                    title: `${label} failed`,
                    body: String(error),
                    buttons: [Dialog.okButton()],
                });
            }
        };

        const poweroffButton = new ToolbarButton({
            label: 'Power off',
            tooltip: 'Power off the Linux machine',
            onClick: () => { void runAction('poweroff', 'Power off'); },
        });

        poweroffButton.id = 'jp-jupyterlab-poweroff';
        app.shell.add(poweroffButton, 'top', { rank: 1000 });

        const rebootButton = new ToolbarButton({
            label: 'Reboot',
            tooltip: 'Reboot the Linux machine',
            onClick: () => { void runAction('reboot', 'Reboot'); },
        });

        rebootButton.id = 'jp-jupyterlab-reboot';
        app.shell.add(rebootButton, 'top', { rank: 1001 });
    },
};

export default plugin;
