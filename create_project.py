"""
Project : Smart_Bourse

File : create_project.py

Version : 0.0.1

Author :
Mehdi Jalali
ChatGPT

Description :
This file creates the complete Smart_Bourse project structure.
"""

"""
Project : Smart_Bourse

File : create_project.py

Version : 0.0.3

Author :
Mehdi Jalali
ChatGPT

Description :
Create all project folders.
"""

from pathlib import Path
from project_config import PROJECT_PATH

# تبدیل مسیر متنی به مسیر قابل استفاده
project = Path(PROJECT_PATH)

folders = [
    "data",
    "indicators",
    "strategy",
    "reports",
    "charts",
    "logs",
    "tests",
    "docs",
    "backup",
    "utils"
]

print("=" * 40)
print("Creating project folders...")
print("=" * 40)

for folder in folders:

    folder_path = project / folder

    folder_path.mkdir(exist_ok=True)

    print(f"✓ {folder} created")

print("=" * 40)
print("Finished Successfully")
print("=" * 40)
