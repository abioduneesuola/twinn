import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import DATASET_PATH, HF_TOKEN, HF_DATASET_REPO


def ensure_dataset_available():
    """
    Checks if dataset exists locally.
    If not, downloads from HuggingFace.
    Works both locally and on server.
    """
    if os.path.exists(DATASET_PATH):
        print(f"✅ Dataset found locally: {DATASET_PATH}")
        return True

    print(f"📥 Dataset not found locally. Downloading from HuggingFace...")

    if not HF_TOKEN or not HF_DATASET_REPO:
        print("❌ HF_TOKEN or HF_DATASET_REPO not set in environment")
        return False

    try:
        from huggingface_hub import hf_hub_download

        # Create data directory if it doesn't exist
        os.makedirs(os.path.dirname(DATASET_PATH), exist_ok=True)

        # Download file
        downloaded_path = hf_hub_download(
            repo_id=HF_DATASET_REPO,
            filename="Digital_Music_5.json.gz",
            repo_type="dataset",
            token=HF_TOKEN,
            local_dir=os.path.dirname(DATASET_PATH)
        )

        print(f"✅ Dataset downloaded to: {downloaded_path}")
        return True

    except Exception as e:
        print(f"❌ Download failed: {e}")
        return False


if __name__ == "__main__":
    ensure_dataset_available()