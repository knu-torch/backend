import os
import json
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_summary_upload():
    test_zip_path = "tests/sample_project.zip"
    assert os.path.exists(test_zip_path), "테스트용 zip 파일이 존재하지 않습니다."

    summary_options = json.dumps(["ProjectSummary", "DirectorySummary"])

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
    request_id = "2144ed06-9943-4fb2-8072-98b1dc3f5e4a"

    # 요청
    response = client.get(f"/summary/download/{request_id}")

    # 검증
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    assert response.content.startswith(b"%PDF")  # 실제 PDF의 시작 바이트


    # PDF 저장 확인용
    with open(f"saved_{request_id}.pdf", "wb") as out_f:
        out_f.write(response.content)
