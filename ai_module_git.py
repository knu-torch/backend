import os
import tempfile
import shutil
import subprocess
from pathlib import Path
from google import genai
from model.enums import summary_options
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

class Recipe(BaseModel):
    title: str
    libs: str
    deploy_info: str
    another: str
    improvements: str  

def setup_gemini():
    api_key = os.getenv("GEMINI_API_KEY")
    
    if not api_key:
        raise ValueError("GEMINI_API_KEY 환경변수가 설정되지 않았습니다. 환경변수를 설정해주세요.")
    
    return genai.Client(api_key=api_key)

client = setup_gemini()

#================================= AI Functions ================================

def clone_github_repo(github_url: str) -> str:
    temp_dir = tempfile.mkdtemp()
    try:
        subprocess.run(["git", "clone", github_url, temp_dir], check=True, capture_output=True)
        return temp_dir
    except subprocess.CalledProcessError as e:
        print(f"GitHub 저장소 클론 실패: {e}")
        shutil.rmtree(temp_dir, ignore_errors=True)
        return None

def extract_code_from_repo(repo_path: str) -> str:
    extracted_code = []
    
    ignore_dirs = ['.git', '__pycache__', 'node_modules', 'venv', 'env', '.venv']
    ignore_exts = ['.pyc', '.pyo', '.so', '.o', '.a', '.dll', '.exe', '.bin', '.dat', '.db', '.sqlite', '.sqlite3']
    binary_exts = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.ico', '.pdf', '.zip', '.tar', '.gz', '.7z', '.rar']
    
    for root, dirs, files in os.walk(repo_path):
        dirs[:] = [d for d in dirs if d not in ignore_dirs and not d.startswith('.')]
        
        rel_path = os.path.relpath(root, repo_path)
        if rel_path == '.':
            rel_path = ''
        
        for file in files:
            file_path = os.path.join(root, file)
            file_rel_path = os.path.join(rel_path, file) if rel_path else file
            
            _, ext = os.path.splitext(file)
            if ext.lower() in ignore_exts or ext.lower() in binary_exts:
                continue
                
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    try:
                        content = f.read()
                        if len(content.strip()) > 0:  
                            extracted_code.append(f"### {file_rel_path}\n{content}")
                    except Exception as e:
                        print(f"파일 읽기 오류 ({file_path}): {e}")
            except Exception as e:
                print(f"파일 접근 오류 ({file_path}): {e}")
    
    return "\n\n".join(extracted_code) if extracted_code else "코드 파일이 없습니다."

def generate_prompt(options: list[summary_options.SummaryOption], code_text: str) -> str:
    title_requirements = []
    libs_requirements = []
    deploy_requirements = []
    another_requirements = []
    improvements_requirements = []  
    
    has_project = summary_options.SummaryOption.Project in options
    has_package = summary_options.SummaryOption.Package in options
    has_file = summary_options.SummaryOption.File in options
    has_function = summary_options.SummaryOption.Function in options
    
    selected_options = []
    if has_project:
        selected_options.append("Project")
    if has_package:
        selected_options.append("Package")
    if has_file:
        selected_options.append("File")
    if has_function:
        selected_options.append("Function")
    
    if has_project:
        title_requirements.append("- 프로젝트의 핵심 기능과 목적을 한 줄로 요약")
        libs_requirements.append("- 사용된 라이브러리 종류와 버전 정보를 알려주고 주요 라이브러리와 역할을 포함 (예: 웹 프레임워크, 데이터베이스, 머신러닝 등)")
        libs_requirements.append("- 디펜던시 트리에서 Depth 2까지 포함")
        deploy_requirements.append("- 배포 관련 정보를 분석하여 정리 (git action, 서비스 파일, Dockerfile 등의 자동화 빌드 및 배포 정보)")
        deploy_requirements.append("- 설정 파일(config, env 파일) 샘플 및 형식 제공")
        another_requirements.append("- Project 관점: 앞에서 들어가지 않은 중요한 프로젝트 정보")
        improvements_requirements.append("- 프로젝트 구조, 코드 품질, 보안, 성능, 유지보수성 측면에서 개선 가능한 부분 제안")
        improvements_requirements.append("- 현대적인 개발 관행과 비교하여 업데이트가 필요한 부분 식별")

    if has_package:
        title_requirements.append("- 프로젝트의 각 패키지 역할을 최대 2줄로 요약하고 각 패키지가 담당하는 기능을 명확하게 작성")
        another_requirements.append("- Package 관점: 프로젝트 내부에서 사용되는 패키지들의 의존성 정리 (외부 라이브러리 제외, 내부 패키지 간의 관계만)")
        another_requirements.append("- 패키지 의존성을 트리 구조 또는 표 형태로 표현")
        improvements_requirements.append("- 패키지 구조 개선점 (의존성 관계, 모듈화, 응집도/결합도 측면)")
    
    if has_file:
        title_requirements.append("- 각 파일 이름과 해당 파일의 기능을 1~2줄로 요약하고 표 형식으로 제공")
        another_requirements.append("- File 관점: 내부 모듈 간 상호작용 분석")
        improvements_requirements.append("- 파일 구조와 조직에 대한 개선점 (네이밍, 분리, 통합 등)")
    
    if has_function:
        title_requirements.append("- 함수 이름과 해당 함수의 역할을 1~2줄로 요약하고 표 형식으로 제공")
        another_requirements.append("- Function 관점: 함수 간 호출 관계 분석 (가능하면 함수 호출 트리로 표현)")
        improvements_requirements.append("- 함수 설계, 복잡성, 재사용성, 단일 책임 원칙 준수 등에 대한 개선점")
    
    prompt_parts = []
    
    prompt_parts.append(
        f"다음은 코드 프로젝트를 분석하여 요약하는 작업입니다. 선택된 옵션은 {', '.join(selected_options)}입니다.\n\n"
        "모든 선택된 옵션에 대한 내용을 통합하여 다음 스키마에 맞게 제공해주세요:\n"
        "{\n"
        "  \"title\": \"프로젝트/패키지/파일/함수 요약 (선택된 옵션에 따라)\",\n"
        "  \"libs\": \"라이브러리 정보 (Project 옵션 선택 시)\",\n"
        "  \"deploy_info\": \"배포 관련 정보 (Project 옵션 선택 시)\",\n"
        "  \"another\": \"기타 중요 정보 (모든 옵션 통합)\",\n"
        "  \"improvements\": \"개선점 및 제안사항 (모든 옵션 통합)\"\n" 
        "}\n\n"
        "중요: 모든 옵션에 대한 내용을 통합하여 제공해주세요. 각 필드에 다음 내용을 포함해야 합니다:\n"
    )
    
    prompt_parts.append("## title 필드 요구사항:")
    for req in title_requirements:
        prompt_parts.append(req)
    
    prompt_parts.append("\n## libs 필드 요구사항:")
    if libs_requirements:
        for req in libs_requirements:
            prompt_parts.append(req)
    else:
        prompt_parts.append("- Project 옵션이 선택되지 않았으므로 '해당 없음'으로 표시")
    
    prompt_parts.append("\n## deploy_info 필드 요구사항:")
    if deploy_requirements:
        for req in deploy_requirements:
            prompt_parts.append(req)
    else:
        prompt_parts.append("- Project 옵션이 선택되지 않았으므로 '해당 없음'으로 표시")
    
    prompt_parts.append("\n## another 필드 요구사항:")
    for req in another_requirements:
        prompt_parts.append(req)
    
    prompt_parts.append("\n## improvements 필드 요구사항:")
    if improvements_requirements:
        for req in improvements_requirements:
            prompt_parts.append(req)
    else:
        prompt_parts.append("- 선택된 옵션에 따른 개선점이 없으므로 '해당 없음'으로 표시")
    
    prompt_parts.append(
        "\n\n중요 지침:"
        "\n- 여러 옵션이 선택되었다면 각 필드에 모든 관련 옵션의 내용을 통합하여 제공하세요."
        "\n- 선택되지 않은 옵션에 대한 내용은 포함하지 마세요."
        "\n- 모든 필드에 반드시 내용을 채워주세요. 해당 정보가 없으면 '해당 없음'이라고 표시하세요."
        "\n- 한국어로 응답해주세요."
        "\n\n이 형식을 엄격하게 준수하여 응답을 JSON 형식으로 제공해주세요."
    )
    
    prompt_parts.append("\n\n## 분석할 코드:")
    if isinstance(code_text, dict):
        prompt_parts.append(str(code_text))
    else:
        prompt_parts.append(code_text)
    
    return "\n".join(prompt_parts)

def analyze_project(prompt):
    try:
        if len(prompt) > 50000:
            prompt = prompt[:49700] + "\n\n... (코드 일부 생략) ...\n\n코드를 기반으로 위 요구사항에 맞게 분석해주세요."
        
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt,
            config={
                'response_mime_type': 'application/json',
                'response_schema': Recipe,
            }
        )
        return response.text
    except Exception as e:
        return None

def summarize_code(code_text: str, options: list[summary_options.SummaryOption]) -> dict:
    prompt = generate_prompt(options, code_text)
    
    try:
        response = analyze_project(prompt)
        if response:
            try:
                result = Recipe.model_validate_json(response).model_dump()
                return result
            except Exception as e:
                return {
                    "title": "응답 파싱 오류가 발생했습니다.",
                    "libs": "원본 응답:",
                    "deploy_info": "-",
                    "another": response[:1000] + "..." if len(response) > 1000 else response,
                    "improvements": "-"  
                }
        else:
            return {"title": "", "libs": "", "deploy_info": "", "another": "응답을 받지 못했습니다.", "improvements": ""}
    except Exception as e:
        return {"title": "", "libs": "", "deploy_info": "", "another": f"요약 중 오류 발생: {e}", "improvements": ""}

def get_github_link():
    """GitHub 링크를 사용자로부터 입력받습니다."""
    import tkinter as tk
    from tkinter import simpledialog
    
    root = tk.Tk()
    root.withdraw()
    github_url = simpledialog.askstring(
        title="GitHub 링크 입력",
        prompt="GitHub 저장소 링크를 입력하세요 (예: https://github.com/username/repository):"
    )
    return github_url

def analyze_options_separately(github_url: str, options: list[summary_options.SummaryOption]) -> dict:
    repo_path = clone_github_repo(github_url)
    if not repo_path:
        return {"title": "", "libs": "", "deploy_info": "", "another": "GitHub 저장소 클론에 실패했습니다.", "improvements": ""}
    
    try:
        extracted_code = extract_code_from_repo(repo_path)
        
        if extracted_code == "코드 파일이 없습니다.":
            return {"title": "", "libs": "", "deploy_info": "", "another": "저장소 내에 분석 가능한 코드 파일이 없습니다.", "improvements": ""}
        
        combined_result = {
            "title": [],
            "libs": [],
            "deploy_info": [],
            "another": [],
            "improvements": []
        }

        for option in options:
            result = summarize_code(extracted_code, [option])
        
            if result["title"]:
                combined_result["title"].append(f"[{option} 옵션] {result['title']}")
        
            if option == summary_options.SummaryOption.Project:
                if result["libs"]:
                    combined_result["libs"].append(result["libs"])
                if result["deploy_info"]:
                    combined_result["deploy_info"].append(result["deploy_info"])
        
            if result["another"]:
                combined_result["another"].append(f"[{option} 옵션] {result['another']}")
            
            if "improvements" in result and result["improvements"]:
                combined_result["improvements"].append(f"[{option} 옵션] {result['improvements']}")
    
        final_result = {
            "title": "\n\n".join(combined_result["title"]) if combined_result["title"] else "정보 없음",
            "libs": "\n\n".join(combined_result["libs"]) if combined_result["libs"] else "해당 없음",
            "deploy_info": "\n\n".join(combined_result["deploy_info"]) if combined_result["deploy_info"] else "해당 없음",
            "another": "\n\n".join(combined_result["another"]) if combined_result["another"] else "정보 없음",
            "improvements": "\n\n".join(combined_result["improvements"]) if combined_result["improvements"] else "개선점 없음"
        }
    
        return final_result
    finally:
        shutil.rmtree(repo_path, ignore_errors=True)

#================================= Extern ================================

def AI(github_url: str, options: list[summary_options.SummaryOption]) -> dict:
    
    return analyze_options_separately(github_url, options)

# for test
if __name__ == "__main__":
    github_url = get_github_link()
    if github_url:
        options = [
            summary_options.SummaryOption.Project,
            summary_options.SummaryOption.Package,
            summary_options.SummaryOption.Function
        ]  
        separate_analysis = analyze_options_separately(github_url, options)
        print(separate_analysis)
    else:
        print("GitHub 링크를 입력하지 않았습니다.")
