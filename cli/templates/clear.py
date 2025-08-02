CLEAR_TEMPLATE = """
[Unit]
Description=Clear plaintext files before shutdown
DefaultDependencies=no
Before=shutdown.target

[Service]
Type=oneshot
WorkingDirectory={project_path}
ExecStart={python} {project_path}/encryptsyncctl.py clear --yes
Environment="PATH={venv_bin}:/usr/bin:/bin"

[Install]
WantedBy=shutdown.target
"""