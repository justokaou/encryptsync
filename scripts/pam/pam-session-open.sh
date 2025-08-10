#!/bin/sh
sid() {
  if [ -n "$XDG_SESSION_ID" ]; then echo "$XDG_SESSION_ID"; return; fi
  if [ -n "$DISPLAY" ]; then echo "disp:${DISPLAY}_${XDG_SEAT:-seat0}" | tr '/.' '__'; return; fi
  if [ -n "$PAM_TTY" ]; then echo "tty:${PAM_TTY}" | tr '/.' '__'; return; fi
  echo "sess:$(printf '%s' "$PAM_USER:$PAM_SERVICE:$$" | md5sum | cut -c1-12)"
}
SID="$(sid)"
exec /bin/systemctl --user start "encryptsync@${SID}.service" "encryptsync-clear@${SID}.service"
