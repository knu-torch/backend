from fpdf import FPDF


# pdf 파일 생성 및 저장
def create_pdf(summary_text: str, output_path: str):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    font_path = "C:/Windows/Fonts/malgun.ttf"
    pdf.add_font("malgun", "", font_path, uni=True)
    pdf.set_font("malgun", size=12)

    for line in summary_text.split('\n'):
        pdf.multi_cell(0, 10, line)

    pdf.output(output_path)

