import os
from pathlib import Path

# Base paths
ROOT_DIR = Path(__file__).parent.parent
DATA_DIR = ROOT_DIR / "data"
CHROMA_DIR = DATA_DIR / "chroma"
TRANSCRIPTS_DIR = DATA_DIR / "transcripts"
RECORDINGS_DIR = DATA_DIR / "recordings"

# Create directories if they don't exist
def create_directories():
    for directory in [DATA_DIR, CHROMA_DIR, TRANSCRIPTS_DIR, RECORDINGS_DIR]:
        directory.mkdir(parents=True, exist_ok=True)

# Ensure directories exist
create_directories()