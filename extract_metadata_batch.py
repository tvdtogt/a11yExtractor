import os
import json
import csv
import sys

# Fields to extract from metadata
TARGET_FIELDS = ["identifier", "title", "author", "publisher", "language"]

def extract_fields_from_json(file_path):
	with open(file_path, 'r', encoding='utf-8') as f:
		try:
			data = json.load(f)
			metadata = data.get("metadata", {})
			return {field: metadata.get(field, "") for field in TARGET_FIELDS}
		except json.JSONDecodeError:
			print(f"Warning: Could not parse JSON from {file_path}")
			return {field: "" for field in TARGET_FIELDS}

def process_directory(input_dir, output_csv):
	all_data = []

	for filename in os.listdir(input_dir):
		if filename.lower().endswith(".json"):
			file_path = os.path.join(input_dir, filename)
			row = extract_fields_from_json(file_path)
			row["filename"] = filename  # Optional: track source file
			all_data.append(row)

	with open(output_csv, 'w', newline='', encoding='utf-8') as csvfile:
		fieldnames = ["filename"] + TARGET_FIELDS
		writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
		writer.writeheader()
		for row in all_data:
			writer.writerow(row)

	print(f"Combined metadata written to {output_csv}")

# Command-line usage
if __name__ == "__main__":
	if len(sys.argv) < 3:
		print("Usage: python extract_metadata_batch.py <input_directory> <output_csv>")
		sys.exit(1)

	input_dir = sys.argv[1]
	output_csv = sys.argv[2]

	process_directory(input_dir, output_csv)