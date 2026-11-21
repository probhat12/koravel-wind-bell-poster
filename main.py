"""Write Koravel's finished travel poster to the bounty's required output path."""

from pathlib import Path
from shutil import copyfile


ROOT = Path(__file__).resolve().parent
OUTPUT = Path("/output")
OUTPUT.mkdir(parents=True, exist_ok=True)
copyfile(ROOT / "poster.png", OUTPUT / "entry.png")
