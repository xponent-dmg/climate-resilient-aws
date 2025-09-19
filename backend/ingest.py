import os
import shutil

DATA_FILE = os.path.join(os.path.dirname(__file__), "data", "421820-2023.csv")
RAW_DIR = os.path.join(os.path.dirname(__file__), "raw")


def ingest():
    os.makedirs(RAW_DIR, exist_ok=True)
    if not os.path.exists(DATA_FILE):
        raise FileNotFoundError(f"Input CSV not found: {DATA_FILE}")
    dst = os.path.join(RAW_DIR, os.path.basename(DATA_FILE))
    shutil.copyfile(DATA_FILE, dst)
    print("Data ingested—let's process this heat! ->", dst)


if __name__ == "__main__":
    ingest()
