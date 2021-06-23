import unittest
import mock
from pdfrw.objects.pdfname import PdfName
from pdfrw.errors import PdfParseError
from src.qrcode import LINK_FORMAT, ON_PAGE_INDEX, TEXT_FORMAT, QR_CODE_PATH
from src.qrcode import create_qrcode, add_qr_to_pdf
from src.qrcode import new_content, insert_qrcode
from src.qrcode import pyqrcode
from src.qrcode import PdfReader
from src.qrcode import FPDF


class CreateQrCodeTestCase(unittest.TestCase):
    '''
    create_qrcode should return a text image and create a png file calling
    pyqrcode.create method and qrcode.png method
    '''
    @mock.patch.object(pyqrcode.QRCode, 'png')
    @mock.patch('src.qrcode.pyqrcode')
    def test_create_qrcode_success(self, mock_pyqrcode, mock_qrcode_png):
        mock_pyqrcode.create.return_value = mock_qrcode_png
        document_code = 1234568898446

        text = create_qrcode(document_code)

        mock_pyqrcode.create.assert_called_with(
            LINK_FORMAT.format(document_code))
        mock_qrcode_png.png.assert_called_with(
            QR_CODE_PATH,
            scale=4,
            module_color=[0, 0, 0, 128],
            background=[0xff, 0xff, 0xff]
        )
        self.assertEqual(text, TEXT_FORMAT.format(document_code))

    '''
    Document code should't be an string of characters, it should be a numeric
    input. Should return TypeError.
    '''

    def test_create_qrcode_invalid_document_code(self):
        document_code = 'This is an invalid document code'
        with self.assertRaises(TypeError) as context:
            text = create_qrcode(document_code)
        self.assertEquals(
            context.exception.message,
            'Invalid document code, input should be numeric'
        )
        self.assertEquals(text, None)


class AddQrToPdfTestCase(unittest.TestCase):
    text = LINK_FORMAT.format(1234568898446)

    '''
    This method should write the pdf with the qr code into the file output if
    input file is a valid one
    '''
    @mock.patch('src.qrcode.new_content', autospec=True)
    @mock.patch('src.qrcode.PdfWriter', autospec=True)
    @mock.patch('src.qrcode.PdfReader', autospec=True)
    @mock.patch('src.qrcode.PageMerge', autospec=True)
    def test_add_qr_to_pdf_success(
        self,
        mock_page_merge,
        mock_pdf_reader,
        mock_pdf_writer,
        mock_new_content
    ):
        mock_pdf_file = mock.MagicMock(spec=PdfReader)
        mock_pdf_file.pages = [mock.MagicMock(spec=PdfName)]
        mock_pdf_reader.return_value = mock_pdf_file

        add_qr_to_pdf('input.pdf', 'output.pdf', self.text)

        mock_pdf_reader.assert_called_with('input.pdf')
        mock_pdf_writer.assert_called_with(trailer=mock_pdf_file)
        mock_page_merge.assert_called_with(mock_pdf_file.pages[ON_PAGE_INDEX])
        mock_page_merge.add.assert_called_with(
            mock_new_content(QR_CODE_PATH, self.text),
            Prepend=False
        )
        mock_page_merge.render.assert_called_once()
        mock_pdf_writer.write.assert_called_with('output.pdf')

    @mock.patch('src.qrcode.PdfReader', autospec=True)
    def test_add_qr_to_pdf_file_not_found(self, mock_pdf_reader):
        input_file = 'notfound.pdf'
        mock_pdf_reader.side_effect = PdfParseError(
            f'Could not read PDF file {input_file}'
        )

        with self.assertRaises(PdfParseError) as context:
            add_qr_to_pdf(input_file, 'output.pdf', self.text)

        mock_pdf_reader.assert_called_with(input_file)
        self.assertEquals(context.exception.message,
                          'Could not read PDF file notfound.pdf')


class NewContentTestCase(unittest.TestCase):
    text = LINK_FORMAT.format(1234568898446)

    @mock.patch('src.qrcode.PdfReader')
    @mock.patch('src.qrcode.FPDF')
    def test_new_content_success(self, mock_fpdf, mock_pdf_reader):
        mock_fpdf_object = mock.MagicMock(return_value=FPDF)
        mock_fpdf.return_value = mock_fpdf_object

        content = new_content(self.text)

        mock_fpdf.assert_called_once()
        mock_fpdf_object.add_page.assert_called_once()
        mock_fpdf_object.image.assert_called_once_with(QR_CODE_PATH, 9, 230, 24)
        mock_fpdf_object.set_font.assert_called_once_with('Helvetica', size=4)
        mock_fpdf_object.set_y(253)
        mock_fpdf_object.multi_cell(22, 2, self.text)
        mock_pdf_reader.assert_called_once_with(
            fdata=bytes(mock_fpdf_object.output()))
        self.assertIsInstance(content, PdfName)

    @mock.patch('src.qrcode.PdfReader')
    @mock.patch('src.qrcode.FPDF')
    def test_new_content_image_not_found(self, mock_fpdf):
        with self.assertRaises(FileNotFoundError):
            content = new_content(self.text)
        self.assertEquals(content, None)


class InsertQrCodeTestCase(unittest.TestCase):
    @mock.patch('src.qrcode.add_qr_to_pdf')
    @mock.patch('src.qrcode.create_qrcode')
    def test_insert_qr_code_success(self, mock_create_qr, mock_add_qr):
        insert_qrcode('input.pdf', 'output.pdf', 1234568898446)
        mock_create_qr.assert_called_once_with(1234568898446)
        mock_add_qr.assert_called_once_with(
            'input.pdf', 'output.pdf', 1234568898446)

    @mock.patch('src.qrcode.add_qr_to_pdf')
    @mock.patch('src.qrcode.create_qrcode')
    def test_insert_qr_code_create_qr_code_error(self, mock_create_qr, mock_add_qr):
        mock_create_qr.side_effect = TypeError(
            'Invalid document code, input should be numeric')

        insert_qrcode('input.pdf', 'output.pdf', 1234568898446)

        mock_create_qr.assert_called_once_with(1234568898446)
        mock_add_qr.assert_not_called()

    @mock.patch('src.qrcode.add_qr_to_pdf')
    @mock.patch('src.qrcode.create_qrcode')
    def test_insert_qr_code_add_qr_to_pdf_error(self, mock_create_qr, mock_add_qr):
        mock_create_qr.side_effect = PdfParseError(
            'Could not read PDF file notfound.pdf'
        )

        insert_qrcode('input.pdf', 'output.pdf', 1234568898446)

        mock_create_qr.assert_called_once_with(1234568898446)
        mock_add_qr.assert_called_once_with(
            'input.pdf', 'output.pdf', 1234568898446)
