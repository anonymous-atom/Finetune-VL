import json
import re
import argparse

def extract_page_number(path):
    match = re.search(r'_page_(\d+)\.png$', path)
    return int(match.group(1)) if match else None

def process_data(data):
    for entry in data:
        # Rule 1: Filter image paths to pages <= 8
        filtered_images = [
            path for path in entry.get("image", [])
            if (page_num := extract_page_number(path)) is not None and page_num <= 8
        ]
        entry["image"] = filtered_images

        # Rule 2: Update the <image>\n tokens in "from": "human"
        for convo in entry.get("conversations", []):
            if convo.get("from") == "human":
                # Remove any existing <image>\n tokens from the beginning
                cleaned_value = re.sub(r'^(<image>\n)+', '', convo["value"]).strip()
                # Add the correct number of new tokens
                new_prefix = "<image>\n" * len(filtered_images)
                convo["value"] = f"{new_prefix}{cleaned_value}"
    return data

def main(input_path, output_path):
    with open(input_path, 'r') as infile:
        data = json.load(infile)

    processed = process_data(data)

    with open(output_path, 'w') as outfile:
        json.dump(processed, outfile, indent=2)

    print(f"✅ Processed JSON saved to {output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process JSON file: filter images and update image tokens")
    parser.add_argument("input", help="Path to input JSON file")
    parser.add_argument("output", help="Path to output JSON file")
    args = parser.parse_args()

    main(args.input, args.output)

