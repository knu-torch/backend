import os
import zipfile
from google.generativeai import configure, GenerativeModel
from model.enums import summary_options

def setup_gemini():
    os.environ["GEMINI_API_KEY"] = "AIzaSyAlX1D_kIgCvoXXU72JgltquG8zWX2xu7Y"
    configure(api_key=os.getenv("GEMINI_API_KEY"))
    return GenerativeModel("gemini-2.0-flash")

gemini_model = setup_gemini()

def extract_code_from_zip(zip_path: str) -> str:
    extracted_code = []
    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        for file_name in zip_ref.namelist():
            if not file_name.endswith('/'):
                with zip_ref.open(file_name) as file:
                    try:
                        extracted_code.append(f"### {file_name}\n" + file.read().decode("utf-8", errors="ignore"))
                    except Exception as e:
                        print(f"파일 읽기 오류 ({file_name}): {e}")
    return "\n\n".join(extracted_code) if extracted_code else "코드 파일이 없습니다."

def generate_prompt(options: list[summary_options.SummaryOption], code_text: str) -> str:
    prompts = []

    if summary_options.SummaryOption.Project in options:
        prompts.append(
            "1 이 프로젝트의 핵심 기능과 목적을 한 줄로 요약해줘."
            "2 사용된 라이브러리 종류와 버전 정보를 알려줘."
            "2-1 주요 라이브러리와 역할을 포함해줘. (예: 웹 프레임워크, 데이터베이스, 머신러닝 등)"
            "2-2 디펜던시 트리에서 Depth 2까지 포함해줘."
            "3 배포 관련 정보를 분석하여 정리해줘."
            "3-1 git action, 서비스 파일, Dockerfile 등의 자동화 빌드 및 배포 정보 포함"
            "3-2 설정 파일(config, env 파일) 샘플 및 형식 제공"
            "4 한국어로 작성해줘."
            "5 마크다운 형식으로 작성해줘."
            "6 ## title, ## libs, ## deploy_info, ## another 영역으로 순서대로 나눠서 작성해줘."
            "7 libs 섹션에서 각 라이브러리의 역할을 설명하는 테이블 형식으로 제공해줘."
        )

    if summary_options.SummaryOption.Package in options:
        prompts.append(
            "1 프로젝트의 각 패키지 역할을 분석하여 최대 2줄로 요약해줘."
            "1-1 각 패키지가 담당하는 기능을 명확하게 작성해줘." 
            "2 프로젝트 내부에서 사용되는 패키지들의 의존성을 정리해줘."
            "2-1 외부 라이브러리는 제외하고, 내부 패키지 간의 관계만 다뤄줘." 
            "2-2 의존성을 트리 구조 또는 표 형태로 표현해줘."
            "3 한국어로 작성해줘."
            "4 마크다운 형식으로 작성해줘."
            "5 ## title, ## libs, ## deploy_info, ## another 영역으로 순서대로 나눠서 작성해줘." 
        )

    return "\n".join(prompts) + f"\n\n{code_text}"

def parse_markdown_sections(text: str) -> dict:
    sections = {"title": "", "libs": "", "deploy_info": "", "another": ""}
    current_section = None
    buffer = []

    for line in text.splitlines():
        line = line.strip()
        if line.startswith("## "):
            if current_section in sections:
                sections[current_section] = "\n".join(buffer).strip()
            current_section = line[3:].strip().lower()  
            buffer = []
        else:
            buffer.append(line)

    if current_section in sections:
        sections[current_section] = "\n".join(buffer).strip()

    return {
        "title": sections["title"],
        "libs": sections["libs"],
        "deploy_info": sections["deploy_info"],
        "another": sections["another"]
    }

def summarize_code(code_text: str, options: list[summary_options.SummaryOption]) -> dict:
    prompt = generate_prompt(options, code_text)
    try:
        response = gemini_model.generate_content(prompt)
        if response:
            return parse_markdown_sections(response.text)
        else:
            return {"title": "", "libs": "", "deploy_info": "", "another": ""}
    except Exception as e:
        return {"title": "", "libs": "", "deploy_info": "", "another": f"요약 중 오류 발생: {e}"}

def AI(zip_path: str, options: list[summary_options.SummaryOption]) -> dict:
    extracted_code = extract_code_from_zip(zip_path)
    
    if extracted_code == "코드 파일이 없습니다.":
        return {"title": "", "libs": "", "deploy_info": "", "another": "ZIP 파일 내에 코드 파일이 없습니다."}
    
    return summarize_code(extracted_code, options)

if __name__ == "__main__":
    options = [summary_options.SummaryOption.Project]
    result = AI(zip_path="../../../a.zip", options=options)
    print("🔸 결과 출력:", result)
