from datasketch import MinHash, MinHashLSH
import argparse
import shutil
from pathlib import Path
import re


def tibetan_tokenizer(text):
    """
    A tokenizer for Tibetan text that splits the text into syllables
    using the tsek character (་) as a delimiter, and then creates shingles.
    """
    shingles = set()
    for i in range(len(text) - 2):
        shingles.add(text[i:i+3])
    return shingles


def run_pipeline(input_dir: Path, output_dir: Path, threshold=0.8, num_perm=128):
    """
    Deduplicates files in an input directory and saves unique files to an output directory.

    Args:
        input_dir (Path): Path to the input directory.
        output_dir (Path): Path to the output directory for unique files.
        threshold (float): Jaccard similarity threshold for deduplication.
        num_perm (int): Number of permutation functions for MinHash.
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    files = sorted([f for f in input_dir.iterdir() if f.is_file()])

    if not files:
        print("No files to process.")
        return

    print(f"Found {len(files)} files. Starting deduplication...")

    # Create MinHashLSH index
    lsh = MinHashLSH(threshold=threshold, num_perm=num_perm)

    # Create MinHash for each file and add to LSH
    minhashes = {}
    for filepath in files:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        if not content.strip():
            continue

        shingles = tibetan_tokenizer(content)
        m = MinHash(num_perm=num_perm)
        for s in shingles:
            m.update(s.encode('utf8'))
        minhashes[str(filepath)] = m
        lsh.insert(str(filepath), m)

    # Identify and filter out duplicates
    unique_files = []
    processed_files = set()
    for filepath in files:
        filepath_str = str(filepath)
        if filepath_str in processed_files:
            continue

        unique_files.append(filepath)
        processed_files.add(filepath_str)

        # Add all near-duplicates to the processed set to avoid them being added to uniques
        neighbors = lsh.query(minhashes[filepath_str])
        for neighbor in neighbors:
            processed_files.add(neighbor)

    # Copy unique files to the output directory
    for filepath in unique_files:
        dest_path = output_dir / filepath.name
        shutil.copy2(filepath, dest_path)

    print(f"Found {len(files) - len(unique_files)} duplicate files.")
    print(f"{len(unique_files)} unique files saved to '{output_dir}'.")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Deduplicate a corpus of Tibetan text files.")
    parser.add_argument("input_dir", type=Path, help="Path to the directory containing the corpus files.")
    parser.add_argument("output_dir", type=Path, help="Path to the directory where unique files will be saved.")
    parser.add_argument("--threshold", type=float, default=0.8, help="Jaccard similarity threshold for deduplication. Default is 0.8.")
    parser.add_argument("--num_perm", type=int, default=128, help="Number of permutation functions for MinHash. Default is 128.")

    args = parser.parse_args()

    run_pipeline(args.input_dir, args.output_dir, threshold=args.threshold, num_perm=args.num_perm)
