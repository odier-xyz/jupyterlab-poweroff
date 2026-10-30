# JupyterLab Poweroff

A JupyterLab 4 extension that adds **Power off** and **Reboot** buttons to the top bar. Each button requests confirmation before shutting down or restarting the Linux host running JupyterLab.

The front end is written in **plain JavaScript (ES6)**, with no TypeScript source files or TypeScript compiler. The server-side extension uses Python and Jupyter Server 2.

> **Security warning:** Any authenticated user who can use these buttons can shut down or reboot the **entire host**, not just their Jupyter kernel or JupyterLab session. Only install this extension on a trusted JupyterLab instance where this is an acceptable privilege. The extension does not grant system privileges automatically.

## Requirements

- Linux with systemd
- JupyterLab 4.x and Jupyter Server 2.x
- Python 3.9 or newer
- `sudo`, configured to permit the required commands
- Node.js and npm **only when building from source**

## Installation

### Install from GitHub

Install `git`, `nodejs`, `npm`, and `sudo` on the host if they are not already available:

```bash
sudo apt install git nodejs npm sudo
```

Install the Python package in the environment that runs JupyterLab. For example, if JupyterLab is installed in `/opt/jupyterlab`:

```bash
/opt/jupyterlab/bin/pip install 'git+https://github.com/YOUR_USERNAME/jupyterlab-poweroff.git'
```

Source installations build the JavaScript bundle automatically. The package provides both a JupyterLab front-end extension and a Jupyter Server extension.

### Install a prebuilt wheel

The GitHub Actions workflow builds a wheel (`.whl`) that includes the JavaScript bundle. Download a wheel from the workflow artifacts or a GitHub release and install it using:

```bash
/opt/jupyterlab/bin/pip install jupyterlab_poweroff-0.2.0-py3-none-any.whl
```

Installing a prebuilt wheel does **not** require Node.js or npm on the target machine.

## Allow power management without root login

Run JupyterLab as an unprivileged user. The administrator must explicitly allow that user to run the two exact commands via `sudo` without a password.

Create a dedicated sudoers file:

```bash
sudo visudo -f /etc/sudoers.d/jupyterlab-poweroff
```

Add these lines, replacing `jupyter` with the Linux user that runs the JupyterLab service:

```sudoers
jupyter ALL=(root) NOPASSWD: /usr/bin/systemctl poweroff
jupyter ALL=(root) NOPASSWD: /usr/bin/systemctl reboot
```

**Do not** grant `NOPASSWD: ALL` or unrestricted access to `systemctl`.

Verify both permissions without actually triggering a shutdown or reboot:

```bash
sudo -u jupyter sudo -n -l /usr/bin/systemctl poweroff
sudo -u jupyter sudo -n -l /usr/bin/systemctl reboot
```

The `sudo -l` checks list matching permissions; they do **not** execute the power management commands.

## Activate and verify

Restart the JupyterLab service if it is running under systemd:

```bash
sudo systemctl restart jupyterlab.service
```

Check that both extensions are discovered:

```bash
/opt/jupyterlab/bin/jupyter server extension list
/opt/jupyterlab/bin/jupyter labextension list
```

Refresh the JupyterLab browser tab. Two buttons should appear in the top bar:

- **Power off**: requests confirmation, then powers down the host.
- **Reboot**: requests confirmation, then restarts the host.

## How it works

1. A button opens JupyterLab's native confirmation dialog.
2. After confirmation, the browser sends an authenticated, XSRF-protected `POST` request to `/api/poweroff` or `/api/reboot`, relative to the configured Jupyter Server base URL.
3. The server checks the corresponding `sudo` permission using `sudo -n -l`.
4. If authorized, the server returns `202 Accepted` and schedules the command one second later so the HTTP response can finish.
5. The server runs the fixed command `sudo -n /usr/bin/systemctl poweroff` or `sudo -n /usr/bin/systemctl reboot` without invoking a shell.

Only these two actions are supported. The client cannot provide an arbitrary command or command arguments.

**Important:** The confirmation dialog protects against accidental clicks, not against a malicious authenticated user. Keep JupyterLab authentication and XSRF protection enabled, and restrict network access to the server.

## Development

Clone the repository and install the JavaScript dependencies:

```bash
git clone https://github.com/YOUR_USERNAME/jupyterlab-poweroff.git
cd jupyterlab-poweroff
npm install
```

Build the prebuilt front-end extension:

```bash
python -m pip install jupyter-builder
npm run build:prod
```

Build a Python wheel:

```bash
python -m pip install build
python -m build
```

Install locally for development:

```bash
python -m pip install -e .
```

Run the tests:

```bash
python -m pip install pytest
python -m pytest -q tests
```

The `.github/workflows/build.yml` workflow builds the wheel, runs the Python tests, checks extension registration, and uploads the wheel as a GitHub Actions artifact.

## License

MIT. See [LICENSE](LICENSE).
