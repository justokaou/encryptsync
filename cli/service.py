import subprocess

def systemctl_cmd(action):
    try:
        subprocess.run(["systemctl", action, "encryptsync.service"], check=True)
        print(f"[{action}] Service encryptsync.service {action}ed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"[{action}] Failed to {action} service: {e}")