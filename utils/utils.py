from fpdf import FPDF
import platform
import os
import requests

# 폰트 다운로드 URL
FONT_URL = "https://raw.githubusercontent.com/notofonts/noto-cjk/main/google-fonts/NotoSansKR%5Bwght%5D.ttf"

# 폰트 저장 경로
FONT_DIR = "./fonts"
FONT_PATH = os.path.join(FONT_DIR, "NotoSansKR-Regular.ttf")


def ensure_font():
    # 폰트 폴더가 없으면 생성
    if not os.path.exists(FONT_DIR):
        os.makedirs(FONT_DIR)

    # 폰트 파일이 없으면 다운로드
    if not os.path.exists(FONT_PATH):
        print(f"Downloading font from {FONT_URL}...")
        response = requests.get(FONT_URL)
        if response.status_code == 200:
            with open(FONT_PATH, "wb") as f:
                f.write(response.content)
            print("Font downloaded successfully.")
        else:
            raise Exception(f"Failed to download font: {response.status_code}")


# pdf 파일 생성 및 저장
def create_pdf(summary_text: str, output_path: str):
    ensure_font()
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    pdf.add_font("NotoSansKR-Regular", "", FONT_PATH, uni=True)
    pdf.set_font("NotoSansKR-Regular", size=12)

    for line in summary_text.split('\n'):
        pdf.multi_cell(0, 10, line)

    pdf.output(output_path)

