import requests, time, statistics, sys

BASE = "http://127.0.0.1:8080"

def one():
    s = requests.Session()
    t = time.time()
    try:
        r = s.post(BASE + "/login", data={"username": "testuser", "password": "bankofanthos"}, timeout=5)
        r2 = s.get(BASE + "/home", timeout=5)
        ok = r.status_code < 400 and r2.status_code == 200
    except Exception:
        ok = False
    return ok, time.time() - t

def run(seconds):
    res = []
    end = time.time() + seconds
    while time.time() - end < 0:
        res.append(one())
        time.sleep(1)
    err = 1 - sum(o for o, _ in res) / len(res)
    lat = statistics.median(l for _, l in res)
    return err, lat

if __name__ == "__main__":
    e, l = run(int(sys.argv[1]))
    print(f"error_rate={e:.2f} p50_latency={l:.2f}s")