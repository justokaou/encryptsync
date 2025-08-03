# 🔐 EncryptSync

**EncryptSync** is a bidirectional GPG-based folder synchronization tool. It automatically encrypts and decrypts files between a plaintext folder and its secure mirrored counterpart (e.g. synced via Syncthing, Nextcloud, etc.)

---

## ✨ Features

- 🔁 Real-time file encryption and decryption using `watchdog`  
- 🔐 GPG-based encryption using a specified public key ID  
- 🧹 Optional plaintext auto-wipe on shutdown  
- ⚙️ Fully configurable via `config.yaml`  
- 🧩 Modular CLI: `encrypt`, `decrypt`, `clear`, `install`, `start`, `stop`, `status`, etc.  
- 💡 Systemd integration: run as a background service  

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
├── cli/  
├── crypto/  
├── debian/  
├── utils/  
├── watcher/  
├── scripts/  
├── tests/  
├── encryptsyncctl.py  
├── main.py  
├── config.yaml  
└── requirements.txt
```
