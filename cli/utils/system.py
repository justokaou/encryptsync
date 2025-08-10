import os, hashlib

def current_session_id() -> str:
    xdg = os.environ.get("XDG_SESSION_ID")
    if xdg:
        return xdg
    disp = os.environ.get("DISPLAY")
    if disp:
        seat = os.environ.get("XDG_SEAT", "seat0")
        return ("disp:%s_%s" % (disp, seat)).replace("/", "__").replace(".", "__")
    pam_tty = os.environ.get("PAM_TTY")
    if pam_tty:
        return ("tty:%s" % pam_tty).replace("/", "__").replace(".", "__")
    h = hashlib.md5(f"{os.environ.get('USER','')}:{os.getpid()}".encode()).hexdigest()
    return "sess:" + h[:12]

def unit_name(base: str, user_scope: bool) -> str:
    # base = "encryptsync" | "encryptsync-clear"
    if user_scope:
        return f"{base}@{current_session_id()}.service"
    return f"{base}.service"
