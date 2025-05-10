import os
import requests
from fastapi import HTTPException

GITHUB_API_TOKEN = os.getenv("GITHUB_API_TOKEN")  # 비공개 리포 접근용


def get_default_branch(user: str, repo: str) -> str:
    url = f"https://api.github.com/repos/{user}/{repo}"
    headers = {"Accept": "application/vnd.github.v3+json"}
    if GITHUB_API_TOKEN:
        headers["Authorization"] = f"Bearer {GITHUB_API_TOKEN}"

    resp = requests.get(url, headers=headers, timeout=5)
    if resp.status_code != 200:
        raise HTTPException(400, f"GitHub API error: {resp.status_code}, {resp.text}")

    return resp.json()["default_branch"]


def resolve_and_download_github_zip(git_url: str, save_path: str):
    # https://github.com/user/repo.git → user, repo 추출
    cleaned = git_url.rstrip("/").removesuffix(".git")
    parts = cleaned.split("/")
    if len(parts) < 2:
        raise HTTPException(400, detail="Invalid GitHub .git URL format")

    user, repo = parts[-2], parts[-1]
    branch = get_default_branch(user, repo)
    zip_url = f"https://github.com/{user}/{repo}/archive/refs/heads/{branch}.zip"

    # 실제 다운로드
    print(f"🔗 Downloading zip from: {zip_url}")
    response = requests.get(zip_url, timeout=10)
    if response.status_code != 200 or "zip" not in response.headers.get("Content-Type", ""):
        raise HTTPException(400,
                            detail=f"Download failed or not a zip: {response.status_code}, {response.headers.get('Content-Type')}")

    with open(save_path, "wb") as f:
        f.write(response.content)

    print(f"✅ Saved to {save_path}")