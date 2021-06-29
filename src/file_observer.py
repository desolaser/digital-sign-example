from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler
from src.signer import sign_pdf
from src.qrcode import insert_qrcode
from pdfrw.errors import PdfParseError

QRCODE_PDF_SUFFIX = '-qr.pdf'
SIGNED_PDF_SUFFIX = '-signed.pdf'


def on_created(event):
    if event.src_path.endswith(QRCODE_PDF_SUFFIX) or \
            event.src_path.endswith(SIGNED_PDF_SUFFIX):
        return

    # file_name = event.src_path.split('\\')[2]
    print(f"Archivo {event.src_path} ha sido detectado")
    try:
        file_path = event.src_path
        qrcode_pdf_file_path = file_path.replace('.pdf', QRCODE_PDF_SUFFIX)
        signed_pdf_file_path = qrcode_pdf_file_path.replace(
            '.pdf', 
            SIGNED_PDF_SUFFIX
        )
        insert_qrcode(file_path, qrcode_pdf_file_path, 123456889846)
        sign_pdf(qrcode_pdf_file_path, signed_pdf_file_path)
    except (TypeError, PdfParseError):
        print("No se pudo firmar el archivo")
    print(f"El archivo {event.src_path} ha sido firmado exitosamente")


def create_file_observer(folder):
    patterns = ["*.pdf"]
    ignore_patterns = None
    ignore_directories = False
    case_sensitive = True
    my_event_handler = PatternMatchingEventHandler(
        patterns,
        ignore_patterns,
        ignore_directories,
        case_sensitive
    )
    my_event_handler.on_created = on_created
    path = folder
    go_recursively = True
    file_observer = Observer()
    file_observer.schedule(
        my_event_handler,
        path,
        recursive=go_recursively
    )
    return file_observer
