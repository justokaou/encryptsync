#!/bin/sh
set -eu

qdir="${XDG_RUNTIME_DIR:-/run/user/$(id -u)}/encryptsync"
mkdir -p "$qdir"

exec 9>"$qdir/.lock"
if ! flock -n 9; then
  exit 0
fi

for f in "$qdir"/open-* "$qdir"/close-*; do
  [ -e "$f" ] || continue
  b="$(basename -- "$f")"
  sid="${b##*-}"
  case "$b" in
    open-*)  systemctl --user start "encryptsync@${sid}.service" "encryptsync-clear@${sid}.service" || true ;;
    close-*) systemctl --user stop  "encryptsync@${sid}.service" "encryptsync-clear@${sid}.service" || true ;;
  esac
  rm -f -- "$f" 2>/dev/null || true
done

if command -v loginctl >/dev/null 2>&1; then
  active="$(loginctl list-sessions --no-legend 2>/dev/null | awk '{print $1}')"
  for u in $(systemctl --user --plain --no-legend --no-pager list-units 'encryptsync@*.service' | awk '{print $1}'); do
    sid="${u#encryptsync@}"; sid="${sid%.service}"
    echo "$active" | grep -qx "$sid" || systemctl --user stop "encryptsync@${sid}.service" "encryptsync-clear@${sid}.service" || true
  done
fi
