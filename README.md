# BoDedup

A Python package for deduplicating Tibetan text files in a directory using MinHash.

## Installation

To install the package, clone the repository and install the dependencies:

```bash
git clone https://github.com/OpenPecha/BoDedup.git
cd BoDedup
pip install .
```

Alternatively, to use this package in another project, you can install it directly from the GitHub repository:

```bash
pip install git+https://github.com/OpenPecha/BoDedup.git
```

For development, install with the `dev` dependencies:

```bash
pip install -e ".[dev]"
```

## Usage

### Deduplicating a Directory of Text Files

You can run the script to find and remove duplicate text files from a directory. The script saves the unique files to a specified output directory.

**Usage:**

To run the deduplication pipeline, use the `src/BoDedup/minhash.py` script:

```bash
python src/BoDedup/minhash.py <path_to_your_input_directory> <path_to_your_output_directory>
```

**Optional Arguments:**

You can also control the sensitivity of the duplicate detection:
*   `--threshold`: Jaccard similarity threshold. Must be between 0 and 1. A higher value means files must be more similar to be considered duplicates. Default is `0.8`.
*   `--num_perm`: The number of permutation functions used by MinHash. More permutations can lead to better accuracy but will be slower. Default is `128`.

Example with optional arguments:
```bash
python src/BoDedup/minhash.py ./corpus/input/ ./corpus/output/ --threshold 0.85 --num_perm 256
```

### Programmatic Usage

You can also import and use the `run_pipeline` function directly in your own Python code.

```python
from pathlib import Path
from BoDedup.minhash import run_pipeline

input_directory = Path("./path/to/input")
output_directory = Path("./path/to/output")

# Ensure the directories exist
input_directory.mkdir(parents=True, exist_ok=True)
output_directory.mkdir(parents=True, exist_ok=True)

# Create some dummy files for the example
(input_directory / "file1.txt").write_text("This is the first file.")
(input_directory / "file2.txt").write_text("This is the second file, very similar to the first.")
(input_directory / "file3.txt").write_text("This is a completely different document.")

# Run the pipeline with a threshold of 0.7
run_pipeline(input_directory, output_directory, threshold=0.7)
```

## Implementation

This project uses the **MinHash** algorithm to efficiently find duplicate and near-duplicate documents.

### What is MinHash?

MinHash is a technique for quickly estimating how similar two sets are. Instead of comparing the full content of two files, which can be very slow, MinHash creates a small, fixed-size "signature" for each document. The key idea is that if two documents are similar, their MinHash signatures will also be very similar.

This allows us to estimate the **Jaccard Similarity** between two documents (the ratio of their common elements to their total unique elements) by only comparing their compact signatures.

### How is it used in this pipeline?

The deduplication process follows these steps:

1.  **Shingling**: Each text file is read and broken down into a set of unique, overlapping character sequences called "shingles". For example, the text `"abcde"` with a shingle size of 3 would become `{"abc", "bcd", "cde"}`. This set of shingles represents the content of the document.

2.  **MinHashing**: The set of shingles for each document is then hashed into a compact MinHash signature. This signature is a small, fixed-length vector of numbers that represents the original text.

3.  **Locality Sensitive Hashing (LSH)**: To avoid the O(n²) problem of comparing every document to every other document, all MinHash signatures are indexed into an LSH data structure. LSH is a clever hashing technique that groups similar signatures together into the same "buckets". This means that to find potential duplicates for a document, we only need to look at other documents in the same bucket, which is extremely fast.

4.  **Querying and Deduplication**: The pipeline iterates through each document, queries the LSH index to find its neighbors (potential duplicates), and then filters them out to produce a final list of unique files.

## Reference Information

*   [MinHash Explained (YouTube)](https://www.youtube.com/watch?v=GRHsg0d5X8Y) - A video explaining the concepts behind the MinHash algorithm.

## Contributing

If you'd like to help out, check out our [contributing guidelines](/CONTRIBUTING.md).

## How to get help

* File an issue.
* Email us at openpecha[at]gmail.com.
* Join our [discord](https://discord.com/invite/7GFpPFSTeA).

## License

This project is licensed under the [MIT License](/LICENSE).
