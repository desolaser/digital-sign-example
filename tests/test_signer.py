import unittest
import hashlib
import mock
import os
import sys
from endesive import pdf
from src.signer import Signer, sign_pdf


class SignerTestCase(unittest.TestCase):
    def setUp(self):
        # self.mock_signer = mock.create_autospec(Signer)
        if sys.platform == 'win32':
            dllpath = os.environ['PKCS11_MODULE']
        else:
            dllpath = \
                '/usr/lib/WatchData/ProxKey/lib/libwdpkcs_SignatureP11.so'
        self.signer = Signer(dllpath)

    def tearDown(self):
        self.signer = None

    def test_certificate_success(self):
        pk11_object = mock.MagicMock()
        self.signer.session = mock.MagicMock()
        self.signer.session.findObjects = mock.MagicMock(
            return_value=[pk11_object])
        self.signer.session.getAttributeValue = mock.MagicMock(
            return_value=[(1, 2), (1, 2)])
        keyid, cert = self.signer.certificate()
        self.assertIsInstance(keyid, bytes)
        self.assertIsInstance(cert, bytes)

    def test_certificate_no_token_detected(self):
        self.signer.session = mock.MagicMock(return_value=None)
        keyid, cert = self.signer.certificate()
        self.assertRaises(AttributeError)
        self.assertEqual(keyid, None)
        self.assertEqual(cert, None)

    def test_sign_success(self):
        keyid = [0x02, 0xa1, 0xb7, 0x9d]
        keyid = bytes(keyid)
        sign_return = hashlib.sha256(b"10101010").digest()

        pk11_object = mock.MagicMock()
        self.signer.session = mock.MagicMock()
        self.signer.session.findObjects = mock.MagicMock(
            return_value=[pk11_object])
        self.signer.session.sign = mock.MagicMock(return_value=sign_return)
        signature = self.signer.sign(keyid, 'This is an example', 'sha256')
        self.assertIsInstance(signature, bytes)

    def test_sign_no_token_detected(self):
        keyid = [0x02, 0xa1, 0xb7, 0x9d]
        keyid = bytes(keyid)

        self.signer.session = mock.MagicMock(return_value=None)
        self.signer.session.findObjects = mock.MagicMock(return_value=None)
        signature = self.signer.sign(keyid, 'This is an example', 'sha256')
        self.assertEqual(signature, None)


class SignPdfTestCase(unittest.TestCase):
    @mock.patch('src.signer.pdf')
    @mock.patch('src.signer.open')
    @mock.patch('src.signer.os')
    def test_sign_pdf_success(self, mock_os, mock_open, mock_pdf):
        mock_os.path.exists.return_value = True
        mock_open.return_value = mock.MagicMock()
        mock_pdf.spec = pdf
        sign_pdf('test.pdf', 'test-signed.pdf')
        mock_open.assert_any_call('test.pdf', 'rb')
        mock_open.assert_any_call('test-signed.pdf', 'wb')
        self.assertEqual(2, mock_open.call_count)
        mock_pdf.cms.sign.assert_called_once()

    @mock.patch('src.signer.pdf')
    @mock.patch('src.signer.open')
    @mock.patch('src.signer.os')
    def test_sign_pdf_input_file_not_found(self, mock_os, mock_open, mock_pdf):
        mock_os.path.exists.return_value = False
        with self.assertRaises(FileNotFoundError) as context:
            sign_pdf('not-existent-file.pdf', 'not-existent-file-signed.pdf')
        self.assertIsInstance(context.exception, FileNotFoundError)
        mock_open.assert_not_called()
        mock_pdf.cms.sign.assert_not_called()

    @mock.patch('src.signer.pdf')
    @mock.patch('src.signer.open')
    @mock.patch('src.signer.os')
    def test_sign_pdf_input_file_cant_be_read(
        self,
        mock_os,
        mock_open,
        mock_pdf
    ):
        mock_os.path.exists.return_value = True
        mock_open.return_value = mock.MagicMock()
        mock_open.side_effect = OSError(2, "File can't be read")
        with self.assertRaises(OSError) as context:
            sign_pdf('unreadable-file.pdf', 'unreadable-file-signed.pdf')
        self.assertIsInstance(context.exception, FileNotFoundError)
        mock_open.assert_called_once_with('unreadable-file.pdf', 'rb')
        mock_pdf.cms.sign.assert_not_called()
