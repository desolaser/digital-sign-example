import pyqrcode
from fpdf import FPDF
from pdfrw import PageMerge, PdfReader, PdfWriter

QR_CODE_PATH = 'code.png'
ON_PAGE_INDEX = 0


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


def add_qr_to_pdf(file_input, file_output, image_path, text):
    pdf_file = PdfReader(file_input)
    writer = PdfWriter(trailer=pdf_file)
    PageMerge(pdf_file.pages[ON_PAGE_INDEX]).add(
        new_content(image_path, text),
        prepend=False).render()
    writer.write(file_output)


def new_content(image_path, text):
    fpdf = FPDF()
    fpdf.add_page()
    fpdf.image(image_path, 9, 230, 24)
    fpdf.set_font('Helvetica', size=4)
    fpdf.set_y(253)
    fpdf.multi_cell(22, 2, text)
    reader = PdfReader(fdata=bytes(fpdf.output()))
    return reader.pages[0]


def insert_qrcode(file_input, file_output, document_code):
    image_path, text = create_qrcode(document_code)
    add_qr_to_pdf(file_input, file_output, image_path, text)

insert_qrcode('./files/hello.pdf', './files/hello-qr.pdf', 123456889846)