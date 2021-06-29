import pyqrcode
from fpdf import FPDF
from pdfrw import PageMerge, PdfReader, PdfWriter, PdfParseError

QR_CODE_PATH = 'code.png'
ON_PAGE_INDEX = 0
LINK_FORMAT = \
    "http://fojas.cl/?cod=&motv=ver_cert&cons=cbr_pvaras&codigo_doc={0}"

TEXT_FORMAT = "Certificado emitido con "
TEXT_FORMAT += "Firma Electrónica Avanzada "
TEXT_FORMAT += "Ley N 19799 Autoacordado "
TEXT_FORMAT += "de la Excma Corte Suprema "
TEXT_FORMAT += "de Chile.- "
TEXT_FORMAT += "Cert N {0} Verifique "
TEXT_FORMAT += "validez en http://fojas.cl"


def create_qrcode(document_code):
    if not isinstance(document_code, (int, float)):
        raise TypeError('Invalid document code, input should be numeric')

    qrcode = pyqrcode.create(LINK_FORMAT.format(document_code))
    qrcode.png(
        QR_CODE_PATH,
        scale=4,
        module_color=[0, 0, 0, 128],
        background=[0xff, 0xff, 0xff]
    )
    text = TEXT_FORMAT.format(document_code)
    return text


def add_qr_to_pdf(file_input, file_output, text):
    pdf_file = PdfReader(file_input)
    writer = PdfWriter(trailer=pdf_file)
    PageMerge(pdf_file.pages[ON_PAGE_INDEX]).add(
        new_content(text),
        prepend=False).render()
    writer.write(file_output)


def new_content(text):
    fpdf = FPDF()
    fpdf.add_page()
    fpdf.image(QR_CODE_PATH, 9, 230, 24)
    fpdf.set_font('Helvetica', size=4)
    fpdf.set_y(253)
    fpdf.multi_cell(22, 2, text)
    reader = PdfReader(fdata=bytes(fpdf.output()))
    return reader.pages[0]


def insert_qrcode(file_input, file_output, document_code):
    try:
        text = create_qrcode(document_code)
        add_qr_to_pdf(file_input, file_output, text)
    except (TypeError, PdfParseError) as e:
        print(e)