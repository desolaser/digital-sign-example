import unittest
import mock
import os
import sys
import PyKCS11 as PK11
from src.signer import Signer


class SignerTestCase(unittest.TestCase):
    def setUp(self):
        # self.mock_signer = mock.create_autospec(Signer)
        if sys.platform == 'win32':
            dllpath = os.environ['PKCS11_MODULE']
        else:
            dllpath = '/usr/lib/WatchData/ProxKey/lib/libwdpkcs_SignatureP11.so'
        self.mock_signer = Signer(dllpath)

    def test_certificate_success(self):
        self.mock_signer.session = mock.MagicMock()
        mock_pk11_object = mock.MagicMock()
        self.mock_signer.session.findObjects.return_value = [mock_pk11_object]
        self.mock_signer.session.getAttributeValue.return_value = [
            (1, 2), (1, 2)]
        all_attributes = [PK11.CKA_VALUE, PK11.CKA_ID]
        keyid, cert = self.mock_signer.certificate()
        self.assertIsInstance(keyid, bytes)
        self.assertIsInstance(cert, bytes)
