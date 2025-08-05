CLEAR_USER_TEMPLATE = """
[Unit]
Description=EncryptedSync clear text files before logout
Before=exit.target

[Service]
Type=oneshot
WorkingDirectory={project_path}
ExecStart={python} {project_path}/encryptsyncctl.py clear --yes
Environment="PATH={venv_bin}:/usr/bin:/bin"

[Install]
WantedBy=default.target
"""