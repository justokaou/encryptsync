import time

recent_outputs = {}

def mark_recent_output(path):
    recent_outputs[path] = time.time()

def is_recent_output(path, window=2.0):
    now = time.time()
    # Clean expired entries
    to_delete = [p for p, t in recent_outputs.items() if now - t > window]
    for p in to_delete:
        del recent_outputs[p]

    return path in recent_outputs
