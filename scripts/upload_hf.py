"""Script to upload Leke tokenizer bundle to Hugging Face Hub."""

import argparse
from pathlib import Path

from huggingface_hub import HfApi


def upload_to_hub(
    model_dir: Path,
    repo_id: str,
    private: bool = False,
    commit_message: str = "Release Leke Kwa subword tokenizer bundle",
):
    api = HfApi()
    print(f"Uploading files from {model_dir} to Hugging Face Hub: {repo_id}...")

    # Create repo if not exists
    api.create_repo(repo_id=repo_id, repo_type="model", private=private, exist_ok=True)

    # Upload folder
    api.upload_folder(
        folder_path=str(model_dir),
        repo_id=repo_id,
        repo_type="model",
        commit_message=commit_message,
    )
    print(f"Upload complete! View at: https://huggingface.co/{repo_id}")


def main():
    parser = argparse.ArgumentParser(description="Upload Leke tokenizer to Hugging Face Hub.")
    parser.add_argument(
        "--model-dir",
        type=str,
        default="models/bpe-16k",
        help="Local directory containing model files",
    )
    parser.add_argument(
        "--repo-id",
        type=str,
        default="acquayefrank/leke-bpe-16k",
        help="Target Hugging Face repo ID",
    )
    parser.add_argument("--private", action="store_true", help="Make repository private")
    parser.add_argument(
        "--commit-message",
        type=str,
        default="Release Leke Kwa subword tokenizer bundle",
        help="Commit message for the Hugging Face upload",
    )

    args = parser.parse_args()
    upload_to_hub(
        model_dir=Path(args.model_dir),
        repo_id=args.repo_id,
        private=args.private,
        commit_message=args.commit_message,
    )


if __name__ == "__main__":
    main()
