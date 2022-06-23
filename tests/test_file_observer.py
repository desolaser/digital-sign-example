import unittest
import mock
from src.file_observer import on_created, create_file_observer
from watchdog.events import FileSystemEvent

'''
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
    except Exception:
        print("No se pudo firmar el archivo")
    print(f"El archivo {event.src_path} ha sido firmado exitosamente")
'''

class FileObserverOnCreateTestCase(unittest.TestCase):
    document_code = 123456889846
    file_path = 'input.pdf'
    qrcode_pdf_file_path = 'input-qr.pdf'
    signed_pdf_file_path = 'input-qr-signed.pdf'

    @mock.patch('src.file_observer.sign_pdf')
    @mock.patch('src.file_observer.insert_qrcode')
    def test_on_create_success(self, mock_insert_qrcode, mock_sign_pdf):
        mock_event = mock.MagicMock(spec=FileSystemEvent)
        mock_event.src_path = self.file_path
        on_created(mock_event)
        mock_insert_qrcode.assert_called_once_with(
            self.file_path, self.qrcode_pdf_file_path, self.document_code)
        mock_sign_pdf.assert_called_once_with(
            self.qrcode_pdf_file_path, self.signed_pdf_file_path)

    @mock.patch('src.file_observer.sign_pdf')
    @mock.patch('src.file_observer.insert_qrcode')
    def test_on_create_is_signed_or_has_qr_code(
            self, mock_insert_qrcode, mock_sign_pdf):
        mock_event = mock.MagicMock(spec=FileSystemEvent)
        mock_event.src_path = 'input-qr.pdf'
        on_created(mock_event)        
        mock_insert_qrcode.assert_not_called()
        mock_sign_pdf.assert_not_called()

        mock_event.src_path = 'input-signed.pdf'
        on_created(mock_event)        
        mock_insert_qrcode.assert_not_called()
        mock_sign_pdf.assert_not_called()

    @mock.patch('src.file_observer.insert_qrcode')
    def test_on_create_on_insert_qrcode_failed(self, mock_insert_qrcode):
        mock_insert_qrcode.side_effect = TypeError(
            'Invalid document code, input should be numeric')
        mock_event = mock.MagicMock(spec=FileSystemEvent)
        mock_event.src_path = self.file_path
        with self.assertRaises(TypeError):
            on_created(mock_event)
            mock_insert_qrcode.assert_called_once_with(
                self.file_path, self.qrcode_pdf_file_path, self.document_code)

    @mock.patch('src.file_observer.sign_pdf')
    @mock.patch('src.file_observer.insert_qrcode')
    def test_on_create_on_sign_pdf_failed(
            self, mock_insert_qrcode, mock_sign_pdf):
        mock_event = mock.MagicMock(spec=FileSystemEvent)
        mock_event.src_path = self.file_path
        on_created(mock_event)
        mock_insert_qrcode.assert_called_once_with(
            self.file_path, self.qrcode_pdf_file_path, self.document_code)
        mock_sign_pdf.assert_called_once_with(
            self.qrcode_pdf_file_path, self.signed_pdf_file_path)