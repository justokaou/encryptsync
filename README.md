# 🔐 EncryptSync

**EncryptSync** is a bidirectional folder sync tool powered by GPG. It automatically encrypts files from a local plaintext folder into an encrypted mirror — which you can then safely synchronize using tools like Syncthing or OwnCloud. Decryption works the same way in reverse, restoring files to their original location as needed.

---

## ✨ Features

- 🔁 Real-time file encryption and decryption using `watchdog`  
- 🔐 GPG-based encryption using a specified public key ID  
- 🧹 Optional plaintext auto-wipe on shutdown  
- ⚙️ Fully configurable via `config.yaml`  
- 🧩 Modular CLI: `encrypt`, `decrypt`, `clear`, `install`, `start`, `stop`, `status`, etc.  
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
sudo apt install ./encryptsync_0.1.0_all.deb
```

This installs:

- All required files to `/usr/lib/encryptsync`  
- The CLI as `encryptsyncctl` in `/usr/bin`  

Then run the installer:

```bash
encryptsyncctl install
```

or to force reinstall services :

```bash
encryptsyncctl install -f
```

This installs : 

- Systemd services  
- Default config at `/etc/encryptsync/config.yaml`

To check service status :

```bash
encryptsyncctl status --service all
```

---

### 🧪 Development install (virtualenv)

```bash
git clone https://github.com/justokaou/encryptsync.git
cd encryptsync
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python encryptsyncctl.py install
```

Use the CLI with:

```bash
python encryptsyncctl.py <command>
```

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

### Edit configuration

The `edit` command opens your configuration file in editor and **automatically restarts** the daemon service to apply changes.
To skip the restart (e.g. when running as a non-root user), use the `--no-restart` flag — but note that **changes won’t take effect until the service is restarted**.

```bash
encryptsyncctl edit
```

### Control systemd services

```bash
encryptsyncctl start --service daemon  
encryptsyncctl stop --service clear  
encryptsyncctl status --service all
```

---

## 📄 Logs

- 🛠️ **When run as a systemd service**:  
  - `/var/log/encryptsync/encryptsync.log`  
  - `/var/log/encryptsync/encryptsync-clear.log`

- 🧪 **When run manually (CLI)**:  
  - `~/.local/state/encryptsync/logs/encryptsync-cli.log`

---

## 📦 Version

**This is version `0.1.0`** — the first stable release, but still undergoing testing across different environments and sync workflows.

⚠️ While core features are complete and reliable, feedback is welcome before releasing `v1.0.0`.

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

| Service               | Description                      |  
|----------------------|----------------------------------|  
| `encryptsync`        | Main daemon (real-time watcher) |  
| `encryptsync-clear`  | Clears plaintext at shutdown     |

```bash
systemctl status encryptsync  
journalctl -u encryptsync
```

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
../encryptsync_0.1.0_all.deb
```

### Install it

```bash
sudo apt install ./encryptsync_0.1.0_all.deb
```

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
