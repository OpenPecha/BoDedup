import shutil
from pathlib import Path
from BoDedup.minhash import run_pipeline

# Define the paths to the test data directories
# Assumes the test is run from the root of the project
DATA_DIR = Path(__file__).parent / "data"
INPUT_DIR = DATA_DIR / "input"
OUTPUT_DIR = DATA_DIR / "output"

def test_run_pipeline():
    """Create and clean the output directory for testing."""
    if OUTPUT_DIR.exists():
        shutil.rmtree(OUTPUT_DIR)
    OUTPUT_DIR.mkdir(parents=True)

    # Run the pipeline
    run_pipeline(INPUT_DIR, OUTPUT_DIR, threshold=0.5)

    # Check the results
    output_files = sorted([f.name for f in OUTPUT_DIR.iterdir()])

    # text1.txt and text2.txt are similar enough to be considered duplicates
    # text3.txt is unique
    # So we expect either [text1.txt, text3.txt] or [text2.txt, text3.txt]
    assert len(output_files) == 2
    assert "text3.txt" in output_files
    assert ("text1.txt" in output_files) or ("text2.txt" in output_files)

    # Check content of the unique files
    if "text1.txt" in output_files:
        content = (OUTPUT_DIR / "text1.txt").read_text(encoding='utf-8')
        assert content == (INPUT_DIR / "text1.txt").read_text(encoding='utf-8')
    else:
        content = (OUTPUT_DIR / "text2.txt").read_text(encoding='utf-8')
        assert content == (INPUT_DIR / "text2.txt").read_text(encoding='utf-8')

    content_doc3 = (OUTPUT_DIR / "text3.txt").read_text(encoding='utf-8')
    assert content_doc3 == (INPUT_DIR / "text3.txt").read_text(encoding='utf-8')
    
    # Teardown: remove the output directory after the test
    shutil.rmtree(OUTPUT_DIR)

if __name__ == "__main__":
    test_run_pipeline()