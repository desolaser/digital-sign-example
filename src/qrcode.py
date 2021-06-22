import pyqrcode
from fpdf import FPDF
from pdfrw import PageMerge, PdfReader, PdfWriter

IN_FILEPATH = './pdf/hello.pdf'
OUT_FILEPATH = './pdf/hello-qr.pdf'
DOCUMENT_CODE = 12345889846
QR_CODE_PATH = 'code.png'
ON_PAGE_INDEX = 1
# if True, new content will be placed underneath page (painted first)
UNDERNEATH = False


def create_qrcode(document_code):
    qrcode = pyqrcode.create(
        f"http://fojas.cl/?cod=&motv=ver_cert&cons=cbr_pvaras&codigo_doc={document_code}")
    qrcode.png(
        QR_CODE_PATH,
        scale=4,
        module_color=[0, 0, 0, 128],
        background=[0xff, 0xff, 0xff]
    )
    text = "Certificado emitido con "
    text += "Firma Electrónica Avanzada "
    text += "Ley N 19799 Autoacordado "
    text += "de la Excma Corte Suprema "
    text += "de Chile.- "
    text += f"Cert N {document_code} Verifique "
    text += "validez en http://fojas.cl"
    return QR_CODE_PATH, text


def insert_qrcode(image_path, text):
    pdf_file = PdfReader(IN_FILEPATH)
    writer = PdfWriter(trailer=pdf_file)
    PageMerge(pdf_file.pages[0]).add(
        new_content(image_path, text),
        prepend=UNDERNEATH).render()
    writer.write(OUT_FILEPATH)


def new_content(image_path, text):
    fpdf = FPDF()
    fpdf.add_page()
    fpdf.image(image_path, 9, 230, 24)
    fpdf.set_font('Helvetica', size=4)
    fpdf.set_y(253)
    fpdf.multi_cell(22, 2, text)
    reader = PdfReader(fdata=bytes(fpdf.output()))
    return reader.pages[0]
