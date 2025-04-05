this Python script is intended to assess the accessibility of a portfolio of e-books in EPUB format.
run_rwp_dir uses the rwp executable from the Readium Go Toolkit (https://github.com/readium/go-toolkit) on a directory with epub files to generate manifests in JSON format first.
extract_metadata_batch generates an overview in .csv format by parsing the JSON manifests.
feel free to use and let me know if you have suggestions how to improve the usability
