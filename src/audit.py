import os

def audit_nicmar_os():
    print("=== NICMAR OS CORE RC1: ARCHITECTURE AUDIT ===")
    src_dir = "src"
    total_files = 0
    total_lines = 0
    large_files = []

    for root, dirs, files in os.walk(src_dir):
        for file in files:
            if file.endswith(".py"):
                total_files += 1
                path = os.path.join(root, file)
                with open(path, "r", encoding="utf-8") as f:
                    lines = f.readlines()
                    line_count = len(lines)
                    total_lines += line_count
                    if line_count > 300:
                        large_files.append((path, line_count))
                        
                print(f"  [OK] {path} ({line_count} lines)")

    print("-" * 45)
    print(f"Total Python modules: {total_files}")
    print(f"Total lines of code: {total_lines}")
    if large_files:
        print("\nWarning: Files exceeding 300 lines:")
        for path, count in large_files:
            print(f"  - {path}: {count} lines")
    else:
        print("\nArchitecture Check Passed: All modules are modular and under 300 lines.")
    print("===============================================")

if __name__ == "__main__":
    audit_nicmar_os()
