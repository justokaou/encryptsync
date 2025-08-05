DAEMON_USER_TEMPLATE = """
[Unit]
Description=EncryptedSync daemon (user mode)
After=default.target

[Service]
Type=simple
WorkingDirectory={project_path}
ExecStart={python} {project_path}/main.py
Restart=always
RestartSec=3
Environment="PATH={venv_bin}:/usr/bin:/bin"

[Install]
WantedBy=default.target
"""