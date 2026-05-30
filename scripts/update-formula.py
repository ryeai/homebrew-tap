#!/usr/bin/env python3
"""Update Formula/rye.rb with new version, URLs, and SHA256 hashes.

This script is meant to be called from the main release flow after
homebrew tarballs have been uploaded to GCS.

Usage:
    python scripts/update-formula.py 0.7.2

It will:
  1. Download each platform tarball from GCS to compute SHA256.
  2. Rewrite Formula/rye.rb with the new version and hashes.
  3. Optionally commit and push (--push flag).
"""

import argparse
import hashlib
import os
import re
import subprocess
import sys
import tempfile
import urllib.request

BASE_URL = "https://storage.googleapis.com/barn.rye.ai/releases"
FORMULA_PATH = os.path.join(os.path.dirname(__file__), "..", "Formula", "rye.rb")

PLATFORMS = {
    "darwin-arm64": "PUT_DARWIN_ARM64_SHA256_HERE",
    "darwin-x64": "PUT_DARWIN_X64_SHA256_HERE",
    "linux-arm64-musl": "PUT_LINUX_ARM64_SHA256_HERE",
    "linux-x64-musl": "PUT_LINUX_X64_SHA256_HERE",
}


def sha256_url(url: str) -> str:
    """Download a URL and return its SHA256 hex digest."""
    print(f"  Fetching {url} ...")
    with urllib.request.urlopen(url) as resp:
        h = hashlib.sha256()
        while chunk := resp.read(8192):
            h.update(chunk)
        return h.hexdigest()


def tarball_url(version: str, platform: str) -> str:
    return f"{BASE_URL}/{version}/homebrew/rye-{version}-{platform}.tar.gz"


def update_formula(version: str, hashes: dict[str, str]):
    """Rewrite Formula/rye.rb with new version and hashes."""
    with open(FORMULA_PATH, "r") as f:
        content = f.read()

    # Update version
    content = re.sub(
        r'version ".*?"',
        f'version "{version}"',
        content,
    )

    # Update URLs and hashes for each platform
    for plat, sha in hashes.items():
        old_url_pattern = re.compile(
            rf'url "https://storage\.googleapis\.com/barn\.rye\.ai/releases/[^"]+/homebrew/rye-[^"]*-{re.escape(plat)}\.tar\.gz"'
        )
        new_url = f'url "{tarball_url(version, plat)}"'
        content = old_url_pattern.sub(new_url, content)

        # Update the sha256 that follows the URL for this platform
        # We rely on the ordering: url line followed by sha256 line
        old_sha_pattern = re.compile(
            rf'(url "{re.escape(tarball_url(version, plat))}")\n(\s+)sha256 "[^"]*"'
        )
        content = old_sha_pattern.sub(
            rf'\1\n\2sha256 "{sha}"',
            content,
        )

    with open(FORMULA_PATH, "w") as f:
        f.write(content)

    print(f"\nFormula updated: {FORMULA_PATH}")


def main():
    parser = argparse.ArgumentParser(description="Update homebrew formula")
    parser.add_argument("version", help="Release version (e.g., 0.7.2)")
    parser.add_argument("--push", action="store_true", help="Commit and push changes")
    parser.add_argument("--skip-download", action="store_true",
                        help="Skip downloading tarballs (use placeholder hashes)")
    args = parser.parse_args()

    version = args.version
    print(f"Updating formula to version {version}\n")

    if args.skip_download:
        hashes = {plat: f"PLACEHOLDER_{plat.upper().replace('-', '_')}" for plat in PLATFORMS}
    else:
        hashes = {}
        for plat in PLATFORMS:
            url = tarball_url(version, plat)
            try:
                hashes[plat] = sha256_url(url)
            except Exception as e:
                print(f"  WARNING: Failed to fetch {url}: {e}")
                hashes[plat] = f"FAILED_TO_FETCH_{plat.upper().replace('-', '_')}"

    update_formula(version, hashes)

    if args.push:
        repo_dir = os.path.join(os.path.dirname(__file__), "..")
        subprocess.run(["git", "add", "Formula/rye.rb"], cwd=repo_dir, check=True)
        subprocess.run(
            ["git", "commit", "-m", f"Update rye to {version}"],
            cwd=repo_dir, check=True,
        )
        subprocess.run(["git", "push"], cwd=repo_dir, check=True)
        print("Pushed to remote.")


if __name__ == "__main__":
    main()
