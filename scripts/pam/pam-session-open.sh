#!/bin/sh
systemctl --user start encryptsync.service encryptsync-clear.service >/dev/null 2>&1 || true