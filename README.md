# 🔐 EncryptSync

**EncryptSync** is a bidirectional folder sync tool powered by GPG.  
It automatically encrypts files from a local plaintext folder into an encrypted mirror — ready to sync with tools like Syncthing or OwnCloud.  
Decryption works the same way in reverse.

---

## ✨ Features

- 🔁 Real-time encryption & decryption with `watchdog`  
- 🔐 GPG-based per-file encryption using your public key  
- 🧹 Optional plaintext auto-wipe on shutdown  
- ⚙️ YAML configuration file  
- 🧩 Modular CLI (`encrypt`, `decrypt`, `clear`, `install`, `uninstall`, `run`, `start`, `stop`, `status`, etc.)  
- 💡 **Systemd integration** — system or user mode (auto-detected)

---

## ❓ Why EncryptSync?

- Client-side encryption before syncing  
- Per-file granularity (no giant encrypted containers)  
- Fully scriptable and transparent  
- Works with GPG agent, smartcards, and hardware tokens  
- Avoids corruption issues from container-based tools

---

## 🚀 Installation

### ✅ From `.deb` (recommended)

Download from [GitHub Releases](https://github.com/justokaou/encryptsync/releases):

```bash
sudo apt install ./encryptsync_<version>_all.deb
```

This installs:

- Core files → `/usr/lib/encryptsync`  
- CLI tool → `/usr/bin/encryptsyncctl`

Then run:

```bash
encryptsyncctl install
```

or for user mode (recommended if your GPG keys are in your session):

```bash
encryptsyncctl install --user
```

> ℹ️ If you omit `--user`, the CLI will try to auto-detect your mode.  
> This also applies to all service commands.

---

## 🧪 Development install

```bash
git clone https://github.com/justokaou/encryptsync.git
cd encryptsync
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 encryptsyncctl.py run
```

---

## ⚙️ Configuration

Config file location depends on mode:

- System mode → `/etc/encryptsync/config.yaml`  
- User mode → `~/.encryptsync/config.yaml`

Example:

```yaml
syncs:
  - name: personal
    plain_dir: /home/user/plain
    encrypted_dir: /home/user/encrypted
    gpg_key: ABCDEF1234567890 # or GPG email
    direction: both
```

Edit via:

```bash
encryptsyncctl edit
```

---

## 🔐 CLI Usage

Encrypt a file:

```bash
encryptsyncctl encrypt ~/Documents/plain/secrets.txt
```

Decrypt a directory:

```bash
encryptsyncctl decrypt ~/Documents/encrypted
```

Clear plaintext:

```bash
encryptsyncctl clear
```

Service control (auto mode detection):

```bash
encryptsyncctl start --service all
encryptsyncctl status
```

Run in foreground:

```bash
encryptsyncctl run
```

---

### 📖 Help & Command Reference

Show general help and list all commands:  
```bash
encryptsyncctl --help
```

Show detailed help for a specific command (example with `status`):  
```bash
encryptsyncctl status --help
```

> ℹ️ Every subcommand supports `--help` to display its available arguments and options.

---

## 📄 Logs

**System mode**:

```
/var/log/encryptsync/encryptsync.log
/var/log/encryptsync/encryptsync-clear.log
```

**User mode**:

```
~/.encryptsync/logs/encryptsync.log
~/.encryptsync/logs/encryptsync-clear.log
```

---

## 🔧 Uninstall

Remove **only** configuration and log files (auto-detect mode):

```bash
encryptsyncctl uninstall
```

Force without prompt:

```bash
encryptsyncctl uninstall --force
```

> ⚠️ This does **not** remove systemd services or binaries.  
> To remove the application itself (from a `.deb` install):

```bash
sudo apt purge encryptsync
```

---

## 🛠️ Systemd Services

| Service | Description |  
| --------------------- | ---------------------- |  
| `encryptsync` | Main daemon |  
| `encryptsync-clear` | Clears plaintext on shutdown |

Check status:

```bash
systemctl status encryptsync
# or
systemctl --user status encryptsync
```

---

## 📦 Build `.deb`

```bash
sudo apt install devscripts dh-python python3-all debhelper
debuild -us -uc
```

Output:

```
../encryptsync_<version>_all.deb
```

---

## 🧭 Portability

Linux-only, relies on systemd for background services.

---

## 📁 Structure

```
encryptsync/
├── cli/              # CLI commands
├── crypto/           # GPG encryption logic
├── debian/           # Packaging
├── ressources/       # Logrotate configs
├── scripts/          # Bash scripts
├── utils/            # Helpers (logger, config, etc.)
├── watcher/          # Real-time sync
├── encryptsyncctl.py  # CLI entry
├── main.py            # Daemon
└── config.template.yaml
```

---

## 📫 Feedback

Report issues on [GitHub](https://github.com/justokaou/encryptsync/issues).