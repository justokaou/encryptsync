#!/bin/sh
set -eu

case "${PAM_SERVICE:-}" in
  cron|sudo|su|su-l|polkit-1|systemd-user|systemd-user-resume) exit 0 ;;
esac

sid="$(sed -n 's/.*session-\([0-9]\+\)\.scope.*/\1/p' /proc/$$/cgroup | tail -n1)"
if [ -z "${sid:-}" ] && command -v loginctl >/dev/null 2>&1; then
  sid="$(loginctl list-sessions --no-legend 2>/dev/null | awk -v u="$PAM_USER" '$3==u{print $1}' | tail -n1 || true)"
fi
[ -z "${sid:-}" ] && exit 0

uid="${PAM_UID:-$(id -u "$PAM_USER" 2>/dev/null || id -u)}"
gid="$(getent passwd "$PAM_USER" | awk -F: '{print $4}' 2>/dev/null || id -g)"
rundir="${XDG_RUNTIME_DIR:-/run/user/$uid}"
qdir="$rundir/encryptsync"
install -d -m 700 -o "$uid" -g "$gid" "$qdir" 2>/dev/null || mkdir -p "$qdir"

case "${PAM_TYPE:-}" in
  open_session)
    : > "$qdir/open-$sid" 2>/dev/null || exit 0
    chown "$uid:$gid" "$qdir/open-$sid" 2>/dev/null || true
    ;;
  close_session)
    : > "$qdir/close-$sid" 2>/dev/null || exit 0
    chown "$uid:$gid" "$qdir/close-$sid" 2>/dev/null || true
    ;;
esac
exit 0