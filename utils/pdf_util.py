# pdf_util.py

import os
import requests
import markdown
from weasyprint import HTML, CSS
from weasyprint.text.fonts import FontConfiguration


# 웹폰트 다운로드 URL
FONT_URL = "https://fonts.google.com/share?selection.family=Noto+Sans+KR:wght@100..900"
FONT_DIR = "./fonts"
#FONT_PATH = os.path.join(FONT_DIR, "NotoSansKR-Regular.ttf")
FONT_PATH = os.path.join(FONT_DIR, "Pretendard-Regular.ttf")


def ensure_font():
    if not os.path.exists(FONT_DIR):
        os.makedirs(FONT_DIR)

    if not os.path.exists(FONT_PATH):
        print("Downloading font...")
        response = requests.get(FONT_URL)
        if response.status_code == 200:
            with open(FONT_PATH, "wb") as f:
                f.write(response.content)
            print("Font downloaded successfully.")
        else:
            raise Exception(f"Font download failed: {response.status_code}")


def create_pdf(markdown_text: str, output_path: str):
    ensure_font()

    html_body = markdown.markdown(markdown_text, extensions=["extra", "codehilite", "nl2br"])

    html_template = f"""
    <html>
    <head>

    </head>
    <body>
        {html_body}
    </body>
    </html>
    """
    font_config = FontConfiguration()
    css = CSS(string='''
            @font-face {
            font-family: "cfont";
            src: url("file:///app/Pretendard-Regular.ttf") format("ttf");
            font-style: normal;
            }

            body {{
                font-family: "cfont", sans-serif;
                font-size: 14px;
                line-height: 1.6;
                margin: 2em;
            }}
            h1, h2, h3 {{ font-weight: bold; }}
            code {{
                background-color: #f4f4f4;
                padding: 2px 4px;
                border-radius: 4px;
            }}
            pre code {{
                display: block;
                padding: 1em;
                background: #f0f0f0;
                overflow-x: auto;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin: 1em 0;
            }}
            th, td {{
                border: 1px solid #ccc;
                padding: 8px 12px;
                text-align: left;
            }}
            th {{
                background-color: #f5f5f5;
            }}

        ''', font_config=font_config)


    HTML(string=html_template).write_pdf(output_path, stylesheets=[css], font_config=font_config)
    print("PDF generation has been completed.")