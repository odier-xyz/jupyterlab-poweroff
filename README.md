# JupyterLab Poweroff

Extension pour **JupyterLab 4** permettant d'éteindre la machine Linux qui héberge le serveur JupyterLab.
Un bouton **Power off** est ajouté dans la zone supérieure. Il ouvre une confirmation avant toute action.

> **Sécurité :** toute personne authentifiée auprès du serveur JupyterLab peut demander l'arrêt de l'hôte. Le paquet n'accorde aucun droit privilégié : la commande n'est exécutée que si l'administrateur l'a autorisée. Ne pas installer sur une instance multi-utilisateur sans en accepter les conséquences.

## Installation depuis GitHub

Le plugin est écrit en **JavaScript natif** (aucun fichier TypeScript). Une construction du bundle JupyterLab reste nécessaire **si l'installation se fait depuis les sources**. Installer une fois `git`, `nodejs` et `npm` (Node.js 20 ou 22 recommandé), ainsi que `sudo` :

```bash
sudo apt install git nodejs npm sudo
```

Pour ton environnement JupyterLab sous `/opt/jupyterlab`, après avoir publié le dépôt GitHub :

```bash
/opt/jupyterlab/bin/pip install 'git+https://github.com/TON_COMPTE/jupyterlab-poweroff.git'
```

Une alternative sans Node.js sur la machine cible consiste à installer le fichier `.whl` construit par GitHub Actions (ou publié dans une release GitHub). Le wheel contient déjà les ressources JavaScript assemblées (bundle JupyterLab).

## Autorisation système (à faire une seule fois)

JupyterLab **ne doit pas être lancé en root**. Par contre, l'administrateur doit autoriser explicitement l'utilisateur Linux du service JupyterLab à lancer **une seule** commande :

```bash
sudo visudo -f /etc/sudoers.d/jupyterlab-poweroff
```

Remplacer `jupyter` ci-dessous par la valeur de `jupyter_user` :

```sudoers
jupyter ALL=(root) NOPASSWD: /usr/bin/systemctl poweroff
```

Vérifier l'autorisation **sans éteindre la machine** :

```bash
sudo -u jupyter sudo -n -l /usr/bin/systemctl poweroff
```

Si l'utilisateur du service est déjà connecté, on peut également utiliser directement :

```bash
sudo -n -l /usr/bin/systemctl poweroff
```

Ne **jamais** ajouter `NOPASSWD: ALL`. La règle ci-dessus ne concerne que la commande `systemctl poweroff`, sans argument supplémentaire.

## Redémarrage et vérification

```bash
sudo systemctl restart jupyterlab.service
/opt/jupyterlab/bin/jupyter server extension list
/opt/jupyterlab/bin/jupyter labextension list
```

Actualiser JupyterLab dans le navigateur. Un bouton **Power off** apparaît dans la zone supérieure.

## Intégration pyinfra

Dans la liste de tes paquets `pip.packages(..., virtualenv = JUPYTER_VENV, ...)`, ajouter simplement :

```python
'git+https://github.com/TON_COMPTE/jupyterlab-poweroff.git',
```

La règle `sudoers` reste à gérer par `pyinfra`, séparément du plugin. Installer également les prérequis `git`, `nodejs`, `npm` et `sudo` si le déploiement construit le paquet depuis GitHub.

## Fonctionnement

1. Le bouton ouvre une confirmation native JupyterLab.
2. Après confirmation, le navigateur envoie `POST <base_url>/api/poweroff` avec les informations d'authentification / XSRF de JupyterLab.
3. Le serveur vérifie l'autorisation `sudo -n -l /usr/bin/systemctl poweroff`.
4. Le serveur répond `202 Accepted`, puis lance une seconde plus tard `sudo -n /usr/bin/systemctl poweroff`.

L'extension ne lance jamais de shell et ne prend pas d'argument de commande fourni par le navigateur.

## Développement

```bash
npm install
npm run build:prod
python -m pip install -e .
```

La construction du bundle utilise `jupyter-builder` (installé automatiquement dans l'environnement de build par `pip`). Aucun compilateur TypeScript n'est utilisé. Pour une construction manuelle :

```bash
python -m pip install build
python -m build
```

Le workflow `.github/workflows/build.yml` construit un wheel à chaque push et le conserve comme artefact GitHub Actions.

## Compatibilité

JupyterLab 4.x, Jupyter Server 2.x, Linux avec systemd et `sudo`.

## Licence

MIT.
