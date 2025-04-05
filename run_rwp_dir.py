import os
import subprocess
import sys
import hashlib

def load_preferences(pref_path):
	prefs = {}
	with open(pref_path, 'r', encoding='utf-8') as f:
		for line in f:
			if '=' in line:
				key, value = line.strip().split('=', 1)
				prefs[key.strip()] = value.strip()
	return prefs.get("rwp_path"), prefs.get("output_dir")

def sanitize_filename(path):
	# Turn a full path into a safe, flat filename using a hash
	hash_prefix = hashlib.md5(path.encode()).hexdigest()[:8]
	base_name = os.path.splitext(os.path.basename(path))[0]
	return f"{base_name}_{hash_prefix}.json"

def run_rwp_on_file(rwp_path, input_file, output_file):
	try:
		result = subprocess.run(
			[rwp_path, "manifest", "--indent", "  ", "--infer-a11y=merged", input_file],
			capture_output=True,
			text=True,
			check=True
		)
		with open(output_file, 'w', encoding='utf-8') as out_f:
			out_f.write(result.stdout)
		print(f"Processed: {input_file}")
	except subprocess.CalledProcessError as e:
		print(f"Error processing {input_file}:\n{e.stderr}")

def process_directory(input_dir, rwp_path, output_dir, exceptions_file):
	if not os.path.exists(output_dir):
		os.makedirs(output_dir)

	with open(exceptions_file, 'w', encoding='utf-8') as exc_file:
		for root, _, files in os.walk(input_dir):
			for filename in files:
				input_path = os.path.join(root, filename)
				if filename.lower().endswith(".epub"):
					output_filename = sanitize_filename(input_path)
					output_path = os.path.join(output_dir, output_filename)
					run_rwp_on_file(rwp_path, input_path, output_path)
				else:
					exc_file.write(input_path + '\n')
					print(f"Skipped (wrong extension): {input_path}")

if __name__ == "__main__":
	if len(sys.argv) < 3:
		print("Usage: python run_rwp_dir.py <input_directory> <preferences.txt>")
		sys.exit(1)

	input_dir = sys.argv[1]
	pref_file = sys.argv[2]

	rwp_path, output_dir = load_preferences(pref_file)
	if not rwp_path or not output_dir:
		print("Error: preferences.txt must define 'rwp_path' and 'output_dir'")
		sys.exit(1)

	exceptions_txt = os.path.join(output_dir, "exceptions.txt")
	process_directory(input_dir, rwp_path, output_dir, exceptions_txt)