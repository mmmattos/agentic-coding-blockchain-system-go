try:
    # module mode
    from .planner import plan_system
    from .generator import generate_system
    from .executor import run_system
    from .validator import validate
except ImportError:
    # script mode
    from planner import plan_system
    from generator import generate_system
    from executor import run_system
    from validator import validate

import os


# Resolve path relative to THIS file (works in all modes)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT = os.path.join(BASE_DIR, "..", "generated_go")


def main():
    print("\n🧠 Agent starting...\n")

    # 1. Plan
    plan = plan_system("blockchain")

    # 2. Generate
    print("⚙️ Generating system...\n")
    generate_system(plan, OUTPUT)

    # 3. Run
    chains, _ = run_system(OUTPUT)

    # 4. Validate
    if validate(chains):
        print("\n✅ SUCCESS: Honest nodes converged\n")
    else:
        print("\n❌ FAIL: Nodes did not converge\n")


if __name__ == "__main__":
    main()