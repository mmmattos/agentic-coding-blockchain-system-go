from planner import plan_system
from generator import generate_system
from executor import run_system
from validator import validate

OUTPUT = "../generated_go"


def main():
    # 1. Generate system
    plan = plan_system("blockchain")
    generate_system(plan, OUTPUT)

    # 2. Run system
    chains, _ = run_system(OUTPUT)

    # 3. DEBUG OUTPUT (important for troubleshooting)
    # print("\n=== DEBUG CHAINS ===")
    # for i, c in enumerate(chains):
    #     print(f"\nNode {i+1}:")
    #     print(c)
    # print("\n====================\n")

    # 4. Validate
    if validate(chains):
        print("OK")
    else:
        print("FAIL")


if __name__ == "__main__":
    main()