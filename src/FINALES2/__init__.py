from pathlib import Path

with open(Path(__file__).parent/'VERSION') as f:
    __version__ = f.readline().strip()
