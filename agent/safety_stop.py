import sys, time, subprocess, requests
BASE = "http://localhost:8080"

def probe():
    try:
        s = requests.Session()
        s.post(BASE + "/login", data={"username": "testuser", "password": "bankofanthos"}, timeout=4)
        if "token" not in s.cookies:
            return False
        r = s.get(BASE + "/home", timeout=4)
        return r.status_code == 200 and "/login" not in r.url
    except Exception:
        return False

yaml_file = sys.argv[1]
duration = int(sys.argv[2]) if len(sys.argv) > 2 else 90
print("baseline probe ok:", probe())
subprocess.run(["kubectl", "apply", "-f", yaml_file])
t0 = time.time()
window, aborted = [], False
try:
    while time.time() - t0 < duration:
        window = (window + [probe()])[-10:]
        errs = window.count(False)
        print(f"t={time.time()-t0:5.0f}s errors in last {len(window)}: {errs}", flush=True)
        if len(window) == 10 and errs / 10 > 0.8:
            print("SAFETY ABORT: >80% errors, rolling back")
            aborted = True
            break
        time.sleep(1)
finally:
    subprocess.run(["kubectl", "delete", "-f", yaml_file])
t1 = time.time(); ok = 0
while ok < 3:
    ok = ok + 1 if probe() else 0
    time.sleep(1)
print(f"RECOVERED in {time.time()-t1:.0f}s after rollback (aborted={aborted})")
