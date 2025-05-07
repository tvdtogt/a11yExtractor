this Python script is intended to get metadata (on accessibility) of a portfolio of e-books in EPUB format.
run_rwp_dir uses the rwp executable from the Readium Go Toolkit (https://github.com/readium/go-toolkit) on a directory with epub files to generate manifests in JSON format first.
run_readium_dir does the same with the newer executable readium https://github.com/readium/cli 
usage: % python run_readium_dir.py ./inputdirectorywithepubs preferences2.txt
extract_metadata_batch generates an overview in .csv format by parsing the JSON manifests.
extract_metadata_and_imageinfo includes additional info on a11y and images
usage: python extract_metadata_and_imageinfo.py --input ./yourinputdirectorywithjsons --output metadata_and_imageinfo.csv

feel free to use and let me know if you have suggestions how to improve the usability
