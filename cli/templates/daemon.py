DAEMON_TEMPLATE = """
[Unit]
Description=EncryptedSync daemon (main watcher)
After=network.target
Wants=network.target

[Service]
Type=simple
WorkingDirectory={project_path}
ExecStart={python} {project_path}/main.py
Restart=always
RestartSec=3
Environment="PATH={venv_bin}:/usr/bin:/bin"

[Install]
WantedBy=multi-user.target
"""
