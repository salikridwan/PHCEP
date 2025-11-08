# remove.py
import sys
import os

def remove_comments_and_mdash(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    clean_lines = []
    inside_triple = False
    removed_count = 0

    for line in lines:
        stripped = line.strip()

        # Toggle triple-quote blocks
        if '"""' in stripped:
            inside_triple = not inside_triple
            removed_count += 1
            continue

        # Skip lines inside triple-quote block
        if inside_triple:
            removed_count += 1
            continue

        # Skip lines with # or m-dash (—)
        if "#" in stripped or "—" in stripped:
            removed_count += 1
            continue

        clean_lines.append(line)

    with open(file_path, "w", encoding="utf-8") as f:
        f.writelines(clean_lines)

    print(f"🧹 Cleaned {file_path}: removed {removed_count} lines.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python remove.py <file1> <file2> ...")
        sys.exit(1)

    for path in sys.argv[1:]:
        if os.path.isfile(path):
            remove_comments_and_mdash(path)
        else:
            print(f"⚠️ Skipping: {path} (not found)")
