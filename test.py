import os
import json
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_summary_upload():
    test_zip_path = "tests/sample_project.zip"
    assert os.path.exists(test_zip_path), "테스트용 zip 파일이 존재하지 않습니다."

    summary_options = json.dumps(["project", "package"])

    with open(test_zip_path, "rb") as f:
        response = client.post(
            "/summary",
            data={"summary_options": summary_options},
            files={"project_file": ("test.zip", f, "application/zip")}
        )

    # 응답 확인
    print("응답 상태:", response.status_code)
    print("응답 본문:", response.json())

    # 기본적인 응답 체크
    assert response.status_code == 200
    assert response.json()["message"] == "OK"

if __name__ == "__main__":
    test_summary_upload()