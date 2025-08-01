# 🔐 EncryptSync

**EncryptSync** is a bidirectional GPG-based folder synchronization tool. It automatically encrypts/decrypts files between a plaintext folder and its secure, mirrored counterpart (e.g. synced via Syncthing, Nextcloud, etc.).

---

## ✨ Features

- 🔁 Real-time file encryption/decryption using `watchdog`  
- 🔐 GPG recipient-based file encryption  
- 🧹 Optional plaintext auto-wipe on shutdown  
- ⚙️ Fully configurable via `config.yaml`  
- 🧩 Modular CLI: `encrypt`, `decrypt`, `clear`, `install`, `start`, `stop`, `status`, etc.  
- 💡 Systemd integration: run as background service  

---

## 🚀 Installation

### ✅ Production install (recommended)

Installs globally via `pip install .`, makes `encryptsyncctl` available in your system path.

```bash
git clone https://github.com/justokaou/encryptsync.git
cd encryptsync
sudo pip install .
```

🔁 After install:

- You can run the CLI with `encryptsyncctl`  
- You can launch the installer:

```bash
encryptsyncctl install
```

This lets you choose between:

- Local installation  
- Installation to `/opt/encryptsync`  
- Setup of systemd services (watcher and clear-on-shutdown)

---

### 🧪 Development install (venv)

Use this if you want to run or develop from source directly:

```bash
git clone https://github.com/justokaou/encryptsync.git
cd encryptsync
python3 -m venv venv
source venv/bin/activate
pip install .
python encryptsyncctl.py install
```

In this mode, you run the CLI using:

```bash
python encryptsyncctl.py <command>
```

---

## ⚙️ Configuration

Edit `config.yaml`:

```yaml
syncs:
  - name: personal
    plain_dir: /home/user/Documents/plain
    encrypted_dir: /home/user/Documents/encrypted
    recipient: ABCDEF1234567890
    direction: both
```

---

## 🔐 Usage (CLI)

### Encrypt a single file

```bash
encryptsyncctl encrypt ~/Documents/plain/secrets.txt
```

### Encrypt a file to a custom directory

```bash
encryptsyncctl encrypt ~/Documents/plain/secrets.txt --output ~/Backup/encrypted
```

### Decrypt a full directory

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

### Control systemd services

```bash
encryptsyncctl start
encryptsyncctl stop
encryptsyncctl status
```

---

## 🖼️ Example

📁 Folder sync layout:

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
| `encryptsync`       | Main daemon (real-time watcher) |  
| `encryptsync-clear` | Clears plaintext at shutdown      |

You can inspect services:

```bash
systemctl status encryptsync
journalctl -u encryptsync
```

---

## 📁 Project Structure

```
encryptsync/
├── cli/               # Command-line tools
├── crypto/            # GPG wrapper
├── utils/             # Shared functions & config
├── watcher/           # Watchdog observers
├── scripts/           # Optional shell scripts
├── tests/             # Optional tests
├── encryptsyncctl.py   # CLI entrypoint
├── main.py             # Watcher runner
├── config.yaml         # User config
```
