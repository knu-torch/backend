import os
import zipfile
from google.generativeai import configure, GenerativeModel
from model.enums import summary_options

def setup_gemini():
    os.environ["GEMINI_API_KEY"] = "AIzaSyBCDzf3655Cj29hdtPsbd65b-V2bpHMoKI"
    configure(api_key=os.getenv("GEMINI_API_KEY"))
    return GenerativeModel("models/gemini-2.5-flash-preview-04-17")

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
            "다음은 코드 분석 요약 요청입니다. 반드시 아래와 같은 마크다운 형식으로 출력해 주세요:\n\n"
            "## title\n"
            "- 이 프로젝트의 핵심 기능과 목적을 한 줄로 요약\n\n"
            "## libs\n"
            "- 사용된 주요 라이브러리 및 프레임워크\n"
            "- 각 라이브러리의 버전 정보\n"
            "- 디펜던시 트리 (depth 2)\n"
            "- 표 형식으로 각 라이브러리의 역할 명시\n\n"
            "## deploy_info\n"
            "- 서비스 파일 (자동 빌드 및 배포 관련 내용)\n"
            "- 설정 파일 (config/env 등) 형식이나 예시\n\n"
            "## another\n"
            "- 기타 정보\n\n"
            "모든 섹션을 빠짐없이 포함하며, 정보가 없을 경우 '해당 없음'이라고 작성해주세요. 한국어로, 마크다운 형식으로 작성해 주세요."
        )

    if summary_options.SummaryOption.Package in options:
        prompts.append(
            "다음은 패키지 분석 요약 요청입니다. 반드시 아래와 같은 마크다운 형식으로 출력해 주세요:\n\n"
            "## title\n"
            "- 각 패키지의 역할 분석 (각 패키지가 어떤 기능을 담당하는지 최대 2줄 요약)\n\n"
            "## libs\n"
            "해당 없음\n\n"
            "## deploy_info\n"
            "해당 없음\n\n"
            "## another\n"
            "- 각 패키지의 역할 분석 (각 패키지가 어떤 기능을 담당하는지 최대 2줄 요약)\n"
            "- 외부 라이브러리를 제외한 내부 패키지 간 의존성 분석\n"
            "- 트리 구조 또는 표 형태로 제공\n\n"
            "모든 섹션을 반드시 포함해주세요. 정보가 없으면 '해당 없음'으로 작성해주세요."
        )
    
    if summary_options.SummaryOption.File in options:
        prompts.append(
            "다음은 파일 단위 요약 요청입니다. 반드시 아래와 같은 마크다운 형식으로 출력해 주세요:\n\n"
            "## title\n"
            "- 각 파일 이름과 해당 파일의 기능을 1~2줄로 요약\n"
            "- 표 형식으로 제공\n\n"
            "## libs\n"
            "해당 없음\n\n"
            "## deploy_info\n"
            "해당 없음\n\n"
            "## another\n"
            "- 내부 모듈 간 상호작용 (있다면)\n\n"
            "모든 섹션을 반드시 포함해주세요. 정보가 없으면 '해당 없음'으로 작성해주세요."
        )

    if summary_options.SummaryOption.Function in options:
        prompts.append(
            "다음은 함수 단위 요약 요청입니다. 반드시 아래와 같은 마크다운 형식으로 출력해 주세요:\n\n"
            "## title\n"
            "- 함수 이름과 해당 함수의 역할을 1~2줄로 요약\n"
            "- 표 형식으로 제공\n\n"
            "## libs\n"
            "해당 없음\n\n"
            "## deploy_info\n"
            "해당 없음\n\n"
            "## another\n"
            "- 함수 간 호출 관계 (있다면 함수 호출 트리로 표현)\n\n"
            "모든 섹션을 반드시 포함해주세요. 정보가 없으면 '해당 없음'으로 작성해주세요."
        )
    
    return "\n\n" + "\n\n".join(prompts) + f"\n\n{code_text}"

def parse_markdown_sections(text: str) -> dict:
    sections = {"title": "", "libs": "", "deploy_info": "", "another": ""}
    current_section = None
    buffer = []

    for line in text.splitlines():
        line = line.strip()
        if line.startswith("## "):
            if current_section and current_section in sections:
                sections[current_section] = "\n".join(buffer).strip()
            current_section = line[3:].strip().lower()
            buffer = []
        else:
            buffer.append(line)

    if current_section and current_section in sections:
        sections[current_section] = "\n".join(buffer).strip()

    return sections

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
    options = [summary_options.SummaryOption.Function]
    result = AI(zip_path="../../a.zip", options=options)
    print(result)
