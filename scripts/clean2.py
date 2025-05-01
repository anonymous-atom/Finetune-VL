import json
import sys
import os

def update_image_paths(json_path, base_url, local_path):
    if not os.path.exists(json_path):
        print(f"❌ File not found: {json_path}")
        return

    # Load the JSON
    with open(json_path, "r") as f:
        data = json.load(f)

    # Update image paths
    for entry in data:
        if "image" in entry:
            entry["image"] = [path.replace(base_url, local_path) for path in entry["image"]]

    # Save the updated JSON
    output_path = json_path.replace(".json", "er.json")
    with open(output_path, "w") as f:
        json.dump(data, f, indent=2)

    print(f"✅ Updated JSON saved to: {output_path}")
    print(json.dumps(data[0], indent=2))  # Show preview of first entry

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python update_image_paths.py <json_path> <base_url> <local_path>")
        sys.exit(1)

    json_path = sys.argv[1]
    base_url = sys.argv[2]
    local_path = sys.argv[3]

    update_image_paths(json_path, base_url, local_path)

