import os
import requests

def test_summarize():
    zip_path = "tests/sample_project.zip"
    assert os.path.exists(zip_path), "테스트용 zip 파일이 존재하지 않습니다."

    with open(zip_path, "rb") as f:
        files = {
            "zip_file": ("sample_project.zip", f, "application/zip")
        }
        data = {
            "text": "이 프로젝트는 FastAPI 기반 서버입니다.",
            "options": '{"language": "python", "detail_level": "medium", "include_comments": true}'
        }
        response = requests.post("http://127.0.0.1:8000/summarize", data=data, files=files)

    print("응답 코드:", response.status_code)
    if response.status_code == 200:
        with open("test_output.pdf", "wb") as out:
            out.write(response.content)
        print("✅ PDF 저장 완료: test_output.pdf")
    else:
        print("❌ 오류:", response.text)

if __name__ == "__main__":
    test_summarize()
