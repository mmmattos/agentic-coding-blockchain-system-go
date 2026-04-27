import subprocess
import time
import requests
import os


def run_system(output_dir):
    procs = []
    ports = ["8001", "8002", "8003"]

    print("\n🚀 Starting nodes...\n")

    # Start nodes
    for p in ports:
        env = os.environ.copy()
        env["PORT"] = p

        if p == "8003":
            env["ADVERSARIAL"] = "true"

        proc = subprocess.Popen(
            ["go", "run", "."],
            cwd=output_dir,
            env=env,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

        procs.append(proc)

    time.sleep(3)

    # -------------------------
    # TRANSACTIONS
    # -------------------------
    print("📥 Sending transactions...\n")

    for i in range(5):
        tx = {"id": f"tx{i}", "amount": i * 100}
        requests.post("http://localhost:8001/transaction", json=tx)
        print(f"→ tx{i}")

    # -------------------------
    # MINING
    # -------------------------
    print("\n⛏ Mining blocks...\n")

    for i in range(3):
        requests.post("http://localhost:8001/mine")
        print(f"→ block {i+1}")
        time.sleep(1)

    # Allow sync
    time.sleep(4)

    # -------------------------
    # FETCH CHAINS
    # -------------------------
    chains = []
    print("\n📡 Fetching chains...\n")

    for p in ports:
        try:
            chain = requests.get(f"http://localhost:{p}/chain").json()
            chains.append(chain)
        except Exception:
            chains.append([])

    # -------------------------
    # DASHBOARD
    # -------------------------
    print("\n📊 DASHBOARD\n")

    for i, c in enumerate(chains):
        print(f"Node {i+1}:")
        print(f"  Blocks: {len(c)}")

        if c:
            last = c[-1]
            h = last.get("hash") or last.get("Hash")
            print(f"  Last hash: {str(h)[:12]}...")

        print()

    # Show adversarial divergence explicitly
    if len(chains) >= 3 and chains[2]:
        last = chains[2][-1]
        h = last.get("hash") or last.get("Hash")
        print(f"⚠️ Adversarial node hash: {h[:12]}...\n")

    # Cleanup
    for p in procs:
        p.kill()

    return chains, ""