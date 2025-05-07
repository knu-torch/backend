import os
import zipfile
from google import genai
from model.enums import summary_options
from pydantic import BaseModel

class Recipe(BaseModel):
    title: str
    libs: str
    deploy_info: str
    another: str

def setup_gemini():
    os.environ["GEMINI_API_KEY"] = "AIzaSyCpFzXsjw_NP_sSEGpKpsxmVlgVk33KNW4"
    return genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

client = setup_gemini()

#================================= AI Functions ================================

def read_project_files(zip_path: str) -> dict:
    extracted_code = {}
    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        for file_name in zip_ref.namelist():
            if not file_name.endswith('/'):
                with zip_ref.open(file_name) as file:
                    try:
                        extracted_code[file_name] = file.read()
                    except Exception as e:
                        print(f"파일 읽기 오류 ({file_name}): {e}")
    return extracted_code

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

def generate_prompt(options: list[summary_options.SummaryOption], code_text: str) -> list:
    prompt = []

    if summary_options.SummaryOption.Project in options:
        prompt.append(
            "이 schema를 따라줘 : {'title': str, 'libs': str, 'deploy_info': str, 'another': str}"
            "이 json 요소들의 내용들은 다음과 같아"
            "title: 이 프로젝트의 핵심 기능과 목적을 한 줄로 요약해줘"
            "libs: 사용된 라이브러리 종류와 버전 정보를 알려주고 주요 라이브러리와 역할을 포함해줘. (예: 웹 프레임워크, 데이터베이스, 머신러닝 등) 그리고 디펜던시 트리에서 Depth 2까지 포함해줘."
            "deploy_info: 배포 관련 정보를 분석하여 정리해줘, git action, 서비스 파일, Dockerfile 등의 자동화 빌드 및 배포 정보 포함 되어야 하고 설정 파일(config, env 파일) 샘플 및 형식 제공해줘"
            "another: 앞에서 들어가지 않은 내용들을 넣어줘"
            "title은 한 줄로 쓰고 나머지는 길게 설명해줘"
            "한국어로 작성해줘."
        )

    if summary_options.SummaryOption.Package in options:
        prompt.append(
            "이 schema를 따라줘 : {'title': str, 'libs': str, 'deploy_info': str, 'another': str}"
            "이 json 요소들의 내용들은 다음과 같아"
            "title: 프로젝트의 각 패키지 역할을 분석하여 최대 2줄로 요약하고 각 패키지가 담당하는 기능을 명확하게 작성해줘"
            "libs: 해당 없음"
            "deploy_info: 해당 없음"
            "another: 프로젝트 내부에서 사용되는 패키지들의 의존성을 정리해줘. 외부 라이브러리는 제외하고, 내부 패키지 간의 관계만 다뤄줘. 의존성을 트리 구조 또는 표 형태로 표현해줘"
            "title은 각 패키지별로 구분해서 작성하고 another는 전체 의존성 구조를 보여줘"
            "한국어로 작성해줘."
        )
    
    if summary_options.SummaryOption.File in options:
        prompt.append(
            "이 schema를 따라줘 : {'title': str, 'libs': str, 'deploy_info': str, 'another': str}"
            "이 json 요소들의 내용들은 다음과 같아"
            "title: 각 파일 이름과 해당 파일의 기능을 1~2줄로 요약하고 표 형식으로 제공해줘"
            "libs: 해당 없음"
            "deploy_info: 해당 없음"
            "another: 내부 모듈 간 상호작용을 분석해줘 (있다면)"
            "title은 파일별로 구분해서 작성하고 another는 파일간 관계를 보여줘"
            "한국어로 작성해줘."
        )

    if summary_options.SummaryOption.Function in options:
        prompt.append(
            "이 schema를 따라줘 : {'title': str, 'libs': str, 'deploy_info': str, 'another': str}"
            "이 json 요소들의 내용들은 다음과 같아"
            "title: 함수 이름과 해당 함수의 역할을 1~2줄로 요약하고 표 형식으로 제공해줘"
            "libs: 해당 없음"
            "deploy_info: 해당 없음"
            "another: 함수 간 호출 관계를 분석해줘 (있다면 함수 호출 트리로 표현)"
            "title은 함수별로 구분해서 작성하고 another는 함수 간 호출 구조를 보여줘"
            "한국어로 작성해줘."
            "모든 섹션을 반드시 포함해주세요. 정보가 없으면 '해당 없음'으로 작성해주세요."
        )
    
    if isinstance(code_text, dict):
        prompt.extend([str(code_text)])
    else:
        prompt.append(code_text)
        
    return prompt

def analyze_project(project_data):
    prompt = """
    다음 프로젝트의 내용을 분석해 주세요:
    {project_data}
    """.format(project_data=str(project_data)[:50000])

    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt,
        config= {
            'response_mime_type': 'application/json',
            'response_schema': Recipe,
        },
    )
    return response.text

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
        response = analyze_project(prompt)
        if response:
            return Recipe.parse_raw(response).dict()
        else:
            return {"title": "", "libs": "", "deploy_info": "", "another": ""}
    except Exception as e:
        return {"title": "", "libs": "", "deploy_info": "", "another": f"요약 중 오류 발생: {e}"}

def select_zip_file():
    import tkinter as tk
    from tkinter import filedialog
    
    root = tk.Tk()
    root.withdraw() 
    zip_file_path = filedialog.askopenfilename(
        title="ZIP 파일 선택",
        filetypes=[("ZIP Files", "*.zip")]  
    )
    return zip_file_path

#================================= Extern ================================

def AI(zip_path: str, options: list[summary_options.SummaryOption]) -> dict:
    extracted_code = extract_code_from_zip(zip_path)

    if extracted_code == "코드 파일이 없습니다.":
        return {"title": "", "libs": "", "deploy_info": "", "another": "ZIP 파일 내에 코드 파일이 없습니다."}

    return summarize_code(extracted_code, options)

# for test
if __name__ == "__main__":
    project_path = select_zip_file()
    if project_path:
        project_data = read_project_files(project_path)
        generated_prompt = generate_prompt([summary_options.SummaryOption.Function], project_data)
        analysis = analyze_project(generated_prompt)
        print(analysis)
    else:
        print("폴더를 선택하지 않았습니다.")
