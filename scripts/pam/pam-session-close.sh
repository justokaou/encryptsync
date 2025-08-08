#!/bin/sh
systemctl --user stop encryptsync.service encryptsync-clear.service >/dev/null 2>&1 || true