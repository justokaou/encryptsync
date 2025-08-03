DAEMON_TEMPLATE = """
[Unit]
Description=EncryptedSync daemon (main watcher)
After=network.target
Wants=network.target

[Service]
Type=simple
WorkingDirectory={project_path}
ExecStartPre=/bin/bash -c 'if mountpoint -q /home; then while ! mountpoint -q /home; do sleep 5; done; else echo "/home is not a mount point, continuing"; fi'
ExecStart={python} {project_path}/main.py
StandardOutput=null
StandardError=append:/var/log/encryptsync/encryptsync.log
Restart=always
RestartSec=3
Environment="PATH={venv_bin}:/usr/bin:/bin"

[Install]
WantedBy=multi-user.target
"""