# 🔐 EncryptSync

**EncryptSync** is a bidirectional folder sync tool powered by GPG. It automatically encrypts files from a local plaintext folder into an encrypted mirror — which you can then safely synchronize using tools like Syncthing or OwnCloud. Decryption works the same way in reverse, restoring files to their original location as needed.

---

## ✨ Features

- 🔁 Real-time file encryption and decryption using `watchdog`  
- 🔐 GPG-based encryption using a specified public key ID  
- 🧹 Optional plaintext auto-wipe on shutdown  
- ⚙️ Fully configurable via `config.yaml`  
- 🧩 Modular CLI: `encrypt`, `decrypt`, `clear`, `install`, `uninstall`, `run`, `start`, `stop`, `status`, etc.  
- 💡 Systemd integration: run as a background service  

---

## ❓ Why EncryptSync?

Cloud storage solutions like Nextcloud or OwnCloud offer basic encryption options — but they come with compromises. Server-side encryption means storing the keys on the same machine, reducing actual security. Full-disk encryption isn’t convenient for remote access.

I wanted a reliable client-side encryption system that:

- 🔒 Encrypts files *before* they’re synced  
- 🔑 Lets me decrypt them automatically and on-demand  
- 🛡️ Offers persistent protection even if the server is compromised  

While tools like **VeraCrypt** exist, I’ve had reliability issues with corrupted containers in the past — especially when syncing large encrypted volumes. I also wanted something:

- 🧩 Modular and transparent  
- 🔐 Based on **GPG**, which I already use and trust  
- 📁 Per-folder, supporting multiple keys if needed  
- ⚙️ Integrated with **systemd** and my workflow  

**EncryptSync** was born from that need: a simple, scriptable, and extensible way to mirror folders with GPG encryption. It offers:

- 🟢 Live encryption/decryption with `watchdog`  
- 🧹 Wiping plaintext at shutdown  
- 🛠️ Automatic decryption at boot or login  

Unlike VeraCrypt, which encrypts full volumes, EncryptSync takes a **granular** approach: per-file encryption, with optional key caching (via GPG agent). If your system is already secured (e.g. encrypted `/home`), you can skip passphrases — otherwise, **GPG** offers flexibility with smartcards and hardware tokens (even if I haven’t used those yet myself).

---

## 🚀 Installation

### ✅ Production install (recommended)

Download the latest `.deb` package from the [GitHub Releases page](https://github.com/justokaou/encryptsync/releases).

```bash
sudo apt install ./encryptsync_0.2.0_all.deb
```

This installs:

- All required files to `/usr/lib/encryptsync`  
- The CLI tool as `encryptsyncctl` in `/usr/bin`

Then run the service installer (with sudo add `sudo $(which python3)` before):

```bash
encryptsyncctl install
```

This will install:

- Systemd services for `encryptsync` and `encryptsync-clear`
- The default config file at:
  - `/etc/encryptsync/config.yaml` (system)

Or for a **user-level install** (recommended if your GPG keys are in your session):

```bash
encryptsyncctl install --user
```

Use `--user` if:

- You installed via the `.deb` but want **per-user systemd services**
- Your **GPG keys are not accessible as root** (common with GPG agents)

This will install:

- Systemd services for `encryptsync` and `encryptsync-clear`
- The default config file at:
  - `~/.encryptsync/config.yaml` (user)

Check service status with:

```bash
encryptsyncctl status --service all
```

Or for user mode:

```bash
encryptsyncctl status --service all --user
```

> ⚠️ **Note**: The `.deb` package does *not* install or activate any systemd service automatically.  
> You must run `encryptsyncctl install` to set them up.

---

### 🧪 Development install (from repo)

```bash
git clone https://github.com/justokaou/encryptsync.git
cd encryptsync
python3 -m venv encryptsync-venv
source encryptsync-venv/bin/activate
pip install -r requirements.txt
python3 encryptsyncctl.py install --user
```

By default, selecting option `2` during install will copy the project into:

```
~/.encryptsync/code
```

Use the CLI like:

```bash
python3 encryptsyncctl.py status --service all --user
```

> ℹ️ If your GPG key is available only in your **user session**, always use `--user` mode.  
> System-wide services will not have access to your agent or smartcard in that case.

---

## ⚙️ Configuration

Edit the `config.yaml`:

```yaml
syncs:
  - name: personal
    plain_dir: /home/user/Documents/plain
    encrypted_dir: /home/user/Documents/encrypted
    gpg_key: ABCDEF1234567890 # or your GPG email
    direction: both
```

---

## 🔐 CLI Usage

### Encrypt a file

```bash
encryptsyncctl encrypt ~/Documents/plain/secrets.txt
```

### Encrypt a file to a custom directory

```bash
encryptsyncctl encrypt ~/Documents/plain/secrets.txt --output ~/Backup/encrypted
```

### Decrypt an entire directory

```bash
encryptsyncctl decrypt ~/Documents/encrypted/
```

### Decrypt to a custom output directory

```bash
encryptsyncctl decrypt ~/Documents/encrypted/ --output ~/Restored/plain
```

### Clear all plaintext

```bash
encryptsyncctl clear
```

### 📝 Edit configuration

The `edit` command opens your configuration file in `nano` and **automatically restarts** the daemon service to apply changes.
To skip the restart, use the `--no-restart` flag — but note that **changes won’t take effect until the service is restarted**.

```bash
encryptsyncctl edit --user
```

> ℹ️ Always pass `--user` if you're managing EncryptSync as a user-level service  
> (e.g. config in `~/.encryptsync/config.yaml`, services in `~/.config/systemd/user`).  
> Without it, the tool assumes system-level usage, which requires root and expects GPG keys to be accessible by `root`.

If you're in development mode and need to run as root (e.g. to restart system services), use:

```bash
sudo $(which python3) encryptsyncctl.py edit
```

> ❗ EncryptSync requires access to your GPG key.  
> If the key is only available in your user session (via `gpg-agent`), using `--user` is **required**.

### 🛠️ Control systemd services

You can control EncryptSync services manually via CLI:

```bash
encryptsyncctl start --service daemon --user  
encryptsyncctl stop --service clear --user  
encryptsyncctl status --service all --user  
encryptsyncctl enable --service all --user  
encryptsyncctl disable --service all --user
```

> ℹ️ Always pass `--user` when managing EncryptSync as a user-level service  
> (e.g. if it was installed via `encryptsyncctl install --user`).  
> This ensures services and configs under your user environment are correctly targeted.

---

If you're running in **system-wide mode** (installed via `.deb` and configured via `encryptsyncctl install` **as root**), use:

```bash
sudo encryptsyncctl start --service daemon
```

Or, for any other service command (`stop`, `restart`, etc.):

```bash
sudo encryptsyncctl stop --service all
```

---

If you're in **development mode**, running from the repo with a virtual environment as root, use:

```bash
sudo $(which python3) encryptsyncctl.py start --service daemon
```

> ⚠️ If your GPG key is only available to your user session (via `gpg-agent`),  
> the system-wide service **will not work** unless the key is accessible by `root`.  
> In that case, prefer using the `--user` installation method.

### ▶️ Run manually (CLI foreground mode)

To run the EncryptSync watcher manually (without systemd), use:

```bash
encryptsyncctl run
```

This is useful if you installed the .deb but prefer to run it interactively, or for testing purposes.
⚠️ Make sure the systemd service encryptsync is not already running to avoid duplicate processes.

---

## 📄 Logs

EncryptSync produces logs depending on how it is run:

- 🛠️ **System service (`root`)**  
  - `/var/log/encryptsync/encryptsync.log` — main daemon service (`encryptsync`) or manual execution of `main.py`  
  - `/var/log/encryptsync/encryptsync-clear.log` — used by both the service (`encryptsync-clear`) and the `encryptsyncctl clear` command

- 🧪 **CLI tool as root (`encryptsyncctl`)**  
  - `/var/log/encryptsync/encryptsync-cli.log` any direct CLI invocation as root like `encrypt`, `decrypt`, `status`, etc. (*except* `clear`, which uses its own log)

- 👤 **User-level service (`--user`)**  
  - `~/.encryptsync/logs/encryptsync.log` — main daemon service or manual execution of `main.py`  
  - `~/.encryptsync/logs/encryptsync-clear.log` — used by both the service and the `encryptsyncctl clear` command

- 🧪 **CLI tool (`encryptsyncctl`)**  
  - `~/.encryptsync/logs/encryptsync-cli.log` — any direct CLI invocation like `encrypt`, `decrypt`, `status`, etc. (*except* `clear`, which uses its own log)

> ℹ️ The path used for logs depends on whether EncryptSync is run as a **system service**, a **user-level service**, or manually via CLI.  
> In **user mode**, logs are stored under `~/.encryptsync/logs/`

> ⚠️ The file `encryptsync-clear.log` is shared between the shutdown service (`encryptsync-clear.service`) and the `encryptsyncctl clear` command, regardless of install mode.

---

### 🔧 Uninstall EncryptSync services

To remove the installed **systemd services** (from either the `.deb` install or development mode), use :

```bash
encryptsyncctl uninstall
```

To skip confirmation prompts:

```bash
encryptsyncctl uninstall --force
```

> ⚠️ This only removes the **services**, not the full application or its files.

---

#### 🧼 Full uninstall (production install)

If EncryptSync was installed via `.deb`, you can remove the core files and CLI with:

> ⚠️ **Purge does not automatically remove user services.**  
> To remove user services, run:

```bash
encryptsyncctl uninstall           # for system-wide install  
encryptsyncctl uninstall --user   # for user install
```

Then :

```bash
sudo apt purge encryptsync
```

This removes:

- CLI binary (`/usr/bin/encryptsyncctl`)
- Core app files (`/usr/lib/encryptsync/`)

> 🛡️ **Privacy note:**  
> The configuration file is not deleted automatically. Depending on your setup, you may need to remove it manually:

- For system-wide installs:

```bash
sudo rm /etc/encryptsync/config.yaml
```

- For user installs:

```bash
rm ~/.encryptsync/config/config.yaml
```

---

## 📦 Version

**This is version 0.2.0** — a follow-up release adding full support for user-level systemd services (`--user`), improved logging structure, clearer file separation, and updated default paths.


⚠️ EncryptSync is still under active testing. Core features are stable, but feedback is welcome before releasing `v1.0.0`.

---

## 🖼️ Example folder layout

```
plain/
└── notes.txt

encrypted/
└── notes.txt.gpg
```

---

## 🛠️ Systemd Services

EncryptSync installs two Systemd units, available in both **system mode (root)** and **user mode** using the `--user` flag:

| Service               | Description                      |  
|----------------------|----------------------------------|  
| `encryptsync`        | Main daemon (real-time watcher) |  
| `encryptsync-clear`  | Clears plaintext at shutdown     |

### 🔧 Check system-level services

```bash
systemctl status encryptsync  
journalctl -u encryptsync
```

### 👤 Check user-level services

```bash
systemctl --user status encryptsync  
journalctl --user -u encryptsync
```

> ℹ️ If you installed the services using `--user`, you must include the `--user` flag in all `systemctl` commands.

---

## 📦 Debian Packaging

### Build requirements

```bash
sudo apt install devscripts dh-python python3-all debhelper
```

### Build the `.deb` package

```bash
debuild -us -uc
```

This creates:

```
../encryptsync_0.2.0_all.deb
```

### Install it

```bash
sudo apt install ./encryptsync_0.2.0_all.deb
```

---

## 🧭 Portability

EncryptSync is currently Linux-only and relies on systemd for background service management.

Although its architecture is modular and cross-platform at the Python level, adapting it to other systems (such as Windows or macOS) would require alternative mechanisms to replicate service behavior.

There are no immediate plans to support other platforms.

---

## 📁 Project Structure

```
encryptsync/
├── cli/                    # CLI commands: encrypt, decrypt, install, etc.
├── crypto/                 # GPG-based encryption/decryption logic
├── debian/                 # Debian packaging files
├── ressources/             # Logrotate config for system logs (used by Debian)
├── utils/                  # Utility functions: logger, hashing, config loader, etc.
├── watcher/                # Watchdog-based real-time sync handlers
├── scripts/                # Reserved for helper or maintenance scripts
├── tests/                  # Placeholder for future unit/integration tests
├── encryptsyncctl.py       # CLI entry point
├── main.py                 # Main daemon launcher (runs watchers)
├── config.template.yaml    # Example configuration (locate in /etc/encryptsync in .deb mode)
└── requirements.txt        # Python dev dependencies
```

---

## 📫 Feedback

This project is still under active testing.  
If you encounter bugs or have suggestions, feel free to open an [issue on GitHub](https://github.com/justokaou/encryptsync/issues) or contact me directly.

---
