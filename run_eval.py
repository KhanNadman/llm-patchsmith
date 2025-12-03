import json
from llm_client import generate_patch_struct

def evaluate():
    with open("tests.json", "r") as f:
        tests = json.load(f)

    passed = 0
    total = len(tests)

    for idx, t in enumerate(tests, 1):
        bullets = t["input"]
        expected_patterns = t["expected"]

        struct = generate_patch_struct(bullets)
        output_text = json.dumps(struct).lower()

        match = all(exp.lower() in output_text for exp in expected_patterns)

        if match:
            passed += 1
            status = "PASS"
        else:
            status = "FAIL"

        print(f"Test {idx}/{total}: {status}")

    print("\n--- SUMMARY ---")
    print(f"Passed: {passed}/{total}")
    print(f"Pass rate: {round((passed / total) * 100, 2)}%")

if __name__ == "__main__":
    evaluate()
