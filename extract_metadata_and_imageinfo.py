import os
import json
import csv
import re
import argparse

def extract_isbn(identifier, filename):
	if isinstance(identifier, str):
		isbn_match = re.search(r"978\d{10}", identifier)
		if isbn_match:
			return isbn_match.group(0)
	file_match = re.search(r"978\d{10}", filename)
	if file_match:
		return file_match.group(0)
	return ""

def process_file(filepath, log_path):
	try:
		with open(filepath, "r", encoding="utf-8") as f:
			data = json.load(f)
	except Exception as e:
		with open(log_path, "a", encoding="utf-8") as log:
			log.write(f"Failed to load JSON file {filepath}: {e}\n")
		return None

	metadata = data.get("metadata", {})
	resources = data.get("resources", [])

	filename = os.path.basename(filepath)
	fileName = filename
	identifier = metadata.get("identifier", "")
	title = metadata.get("title", "")
	author = metadata.get("author", "")
	publisher = metadata.get("publisher", "")
	language = metadata.get("language", "")
	version = metadata.get("http://www.idpf.org/2007/opf#version", "")
	layout = metadata.get("presentation", {}).get("layout", "")
	isbn = extract_isbn(identifier, filename)

	access_mode = metadata.get("accessibility", {}).get("accessMode", [])
	access_mode_sufficient_raw = metadata.get("accessibility", {}).get("accessModeSufficient", [])
	summary = metadata.get("accessibility", {}).get("summary", "")
	hazard = metadata.get("accessibility", {}).get("hazard", [])
	features = metadata.get("accessibility", {}).get("feature", [])

	if isinstance(access_mode, list):
		access_mode = ",".join(access_mode)
	if isinstance(hazard, list):
		hazard = ",".join(hazard)

	access_mode_sufficient = []
	non_visual_reading = 0
	if isinstance(access_mode_sufficient_raw, list):
		for item in access_mode_sufficient_raw:
			if isinstance(item, list):
				access_mode_sufficient.append(",".join(item))
				if item == ["textual"]:
					non_visual_reading = 1
			elif isinstance(item, str):
				access_mode_sufficient.append(item)
	elif isinstance(access_mode_sufficient_raw, str):
		access_mode_sufficient = [access_mode_sufficient_raw]
		if access_mode_sufficient_raw == "textual":
			non_visual_reading = 1
	access_mode_sufficient = ";".join(access_mode_sufficient)

	all_feature_labels = [
		"structuralNavigation", "tableOfContents", "alternativeText",
		"ARIA", "pageBreakMarkers", "pageNavigation", "printPageNumbers"
	]
	feature_flags = {label: 0 for label in all_feature_labels}
	other_features = []

	for feature in features:
		if feature in feature_flags:
			feature_flags[feature] = 1
		else:
			other_features.append(feature)

	feature_flags["otherAccessibilityFeatures"] = ",".join(other_features)

	jpeg_count = png_count = gif_count = 0
	small_count = medium_count = large_count = 0

	for res in resources:
		img_type = res.get("type", "").lower()
		width = res.get("width")
		height = res.get("height")

		if img_type == "image/jpeg":
			jpeg_count += 1
		elif img_type == "image/png":
			png_count += 1
		elif img_type == "image/gif":
			gif_count += 1
		else:
			continue

		try:
			if isinstance(width, int) and isinstance(height, int):
				area = width * height
				if area < 1000:
					small_count += 1
				elif area <= 10000:
					medium_count += 1
				else:
					large_count += 1
		except:
			continue

	total_images = jpeg_count + png_count + gif_count

	row = {
		"fileName": fileName,
		"identifier": identifier,
		"ISBN": isbn,
		"title": title,
		"author": author,
		"publisher": publisher,
		"language": language,
		"#jpeg": jpeg_count,
		"#png": png_count,
		"#gif": gif_count,
		"#images": total_images,
		"#small_images": small_count,
		"#medium_images": medium_count,
		"#large_images": large_count,
		"version": version,
		"layout": layout,
		"accessMode": access_mode,
		"accessModeSufficient": access_mode_sufficient,
		"nonVisualReading": non_visual_reading,
		"summary": summary,
		"hazard": hazard,
	}
	row.update(feature_flags)

	return row

def main():
	parser = argparse.ArgumentParser(description="Extract metadata and image stats from JSON files.")
	parser.add_argument("--input", required=True, help="Path to input directory with JSON files")
	parser.add_argument("--output", required=True, help="Path to output CSV file")
	args = parser.parse_args()

	input_dir = args.input
	output_csv = args.output
	log_path = os.path.join(os.path.dirname(output_csv), "log.txt")

	os.makedirs(input_dir, exist_ok=True)
	files = [f for f in os.listdir(input_dir) if f.endswith(".json")]
	rows = []

	for file in files:
		path = os.path.join(input_dir, file)
		result = process_file(path, log_path)
		if result:
			rows.append(result)

	if not rows:
		print("No valid JSON files found.")
		return

	fieldnames = list(rows[0].keys())
	with open(output_csv, "w", encoding="utf-8", newline="") as csvfile:
		writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
		writer.writeheader()
		writer.writerows(rows)

	print(f"Processed {len(rows)} files. Output written to {output_csv}")

if __name__ == "__main__":
	main()