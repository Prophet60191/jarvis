
import time
import signal
import sys

def signal_handler(signum, frame):
    print(f"Received signal {signum}, exiting...")
    sys.exit(0)

signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)

print("Test process started, PID:", os.getpid())
try:
    while True:
        time.sleep(1)
        print("Test process running...")
except KeyboardInterrupt:
    print("Test process interrupted")
    sys.exit(0)
