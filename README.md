# 🔐 EncryptSync

EncryptSync is a bidirectional folder sync tool powered by GPG.
It automatically encrypts files from a local plaintext folder into an encrypted mirror — ready to sync with tools like Syncthing or OwnCloud.
Decryption works the same way in reverse.

---

## ✨ Features

- 🔁 Real-time encryption & decryption with `watchdog`
- 🔐 GPG-based per-file encryption using your public key
- 🧹 Optional plaintext auto-wipe on logout (per session)
- ⚙️ YAML configuration file
- 🧩 Modular CLI (`encrypt`, `decrypt`, `clear`, `install`, `uninstall`, `run`, `start`, `stop`, `status`, etc.)
- 💡 Systemd user-mode integration via **PAM → queue → dispatcher** (per-session, no race with the user bus)

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

Download from [Releases](https://git.justokaou.xyz/justokaou/encryptsync/releases) and install:

```bash
sudo apt install ./encryptsync_<version>_all.deb
```

This installs:
- Core files → `/usr/lib/encryptsync`
- CLI tool → `/usr/bin/encryptsyncctl`
- PAM profile → `/usr/share/pam-configs/encryptsync`
- systemd **user** units → `/usr/lib/systemd/user/`
  - `encryptsync-queue.path` (watches the per-session queue)
  - `encryptsync-dispatch.timer` (periodic sweep)
  - `encryptsync-dispatch.service` (oneshot dispatcher)
  - `encryptsync@.service` (per-session daemon)
  - `encryptsync-clear@.service` (per-session clear, oneshot)

User units are enabled by default via a preset (no `systemctl` in maintainer scripts).

Then run (optional but recommended to create/edit your config):

```bash
encryptsyncctl install
```

---

## 🔐 PAM integration (how sessions trigger EncryptSync)

- On login (SSH/TTY/GDM), PAM writes a marker `open-<SID>` to `%t/encryptsync` (i.e., `/run/user/$UID/encryptsync`).
- A systemd **path** unit (`encryptsync-queue.path`) or the **timer** (`encryptsync-dispatch.timer`) launches the **dispatcher**.
- The dispatcher starts `encryptsync@<SID>.service` and `encryptsync-clear@<SID>.service`, then removes the marker.
- On logout, PAM writes `close-<SID>`; the dispatcher stops the same services and cleans up plaintext.

The PAM line is installed via `pam-auth-update` from the profile at `/usr/share/pam-configs/encryptsync` (inserted after `pam_systemd`; interactive sessions only). No manual edits to `/etc/pam.d/common-session*` are required.

Tip: if you want your user manager running even without an open login session, enable linger:

```bash
loginctl enable-linger <your-username>
```

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

User config:

```text
~/.encryptsync/config.yaml
```

Example:

```yaml
syncs:
  - name: personal
    plain_dir: /home/user/plain
    encrypted_dir: /home/user/encrypted
    gpg_key: ABCDEF1234567890   # or a GPG email
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

Service control (per current session, through the queue/dispatcher):

```bash
encryptsyncctl start
encryptsyncctl status
encryptsyncctl stop
```

Notes:
- `start` / `stop` simulate login/logout for the **current** session by writing `open-<SID>` / `close-<SID>` into the queue and invoking the dispatcher.
- `status` shows watcher/timer state and currently running instances (`encryptsync@<SID>.service`).

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

Show detailed help for a specific command:

```bash
encryptsyncctl status --help
```

Every subcommand supports `--help` to display its options.

---

## 📄 Logs

User :

```text
~/.encryptsync/logs/encryptsync.log
~/.encryptsync/logs/encryptsync-clear.log
~/.encryptsync/logs/encryptsync-cli.log
```

Root :

```text
/var/log/encryptsync/encryptsync.log
/var/log/encryptsync/encryptsync-clear.log
/var/log/encryptsync/encryptsync-cli.log
```

---

## 🔧 Uninstall

Remove config and logs (keeps the package itself):

```bash
encryptsyncctl uninstall
# or
encryptsyncctl uninstall --force
```

>⚠️ This only removes the config.yaml and log files, not the full application.

Remove the application (if installed from `.deb`):

```bash
sudo apt purge encryptsync
```

The PAM profile is removed via `pam-auth-update`; systemd user units are handled declaratively via presets.

---

## 🛠️ Systemd (user) units

| Unit                           | Type  | Purpose                                              |
|------------------------------- |-------|------------------------------------------------------|
| `encryptsync-queue.path`       | user  | Watches `%t/encryptsync/{open,close}-*` markers      |
| `encryptsync-dispatch.timer`   | user  | Periodically triggers the dispatcher (safety net)    |
| `encryptsync-dispatch.service` | user  | One-shot: consumes queue and (start|stop)s sessions  |
| `encryptsync@.service`         | user  | Per-session daemon instance (`%i` = session ID)      |
| `encryptsync-clear@.service`   | user  | Per-session clear (oneshot; runs at start/stop)      |

Check status:

```bash
encryptsyncctl status
```

---

## 📦 Build `.deb`

```bash
sudo apt install devscripts dh-python python3-all debhelper
debuild -us -uc
```

Output:

```text
../encryptsync_<version>_all.deb
```

Packaging notes:
- User units are enabled via `/usr/lib/systemd/user-preset/90-encryptsync.preset`.
- PAM is configured via `/usr/share/pam-configs/encryptsync` (managed by `pam-auth-update`).
- No `systemctl` calls in maintainer scripts (Lintian-friendly).

---

## 🧭 Portability

Linux-only. Requires systemd (user manager) and PAM.

---

## 📁 Structure

```text
encryptsync/
├── cli/                       # CLI commands
├── crypto/                    # GPG encryption logic
├── debian/                    # Packaging (Debian)
├── ressources/
│   ├── pam/
│   │   └── encryptsync        # pam-auth-update profile (adds pam_exec after pam_systemd)
│   └── systemd/
│       ├── user/
│       │   ├── encryptsync-clear@.service     # per-session clear (oneshot)
│       │   ├── encryptsync-dispatch.service   # dispatcher (oneshot)
│       │   ├── encryptsync-dispatch.timer     # periodic sweep (safety net)
│       │   ├── encryptsync-queue.path         # watches %t/encryptsync/{open,close}-*
│       │   └── encryptsync@.service           # per-session daemon (%i = SID)
│       └── user-preset/
│           └── 90-encryptsync.preset          # enables queue.path + dispatch.timer by default
├── scripts/
│   ├── pam/
│   │   └── pam-dispatch.sh    # PAM hook: writes open-/close-<SID> markers
│   └── dispatch.sh            # runtime dispatcher (installed to /usr/lib/encryptsync/dispatch.sh)
├── utils/                     # Helpers (logger, config, etc.)
├── watcher/                   # Real-time file watching/sync
├── encryptsyncctl.py          # CLI entry
├── main.py                    # Daemon entrypoint
└── config.template.yaml       # Default config template
```

---

## 📫 Feedback

Report issues : https://git.justokaou.xyz/justokaou/encryptsync/issues
