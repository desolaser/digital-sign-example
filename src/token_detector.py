import os
import sys
import PyKCS11 as PK11


class TokenDetector():
    actual_token = None

    def __init__(self, database_helper):
        self.database_helper = database_helper

    def find_token(self):
        if self.actual_token is not None:
            return self.actual_token

        serial_number = self.get_serial_number()
        token = self.database_helper.get_token(serial_number)

        return token

    def get_serial_number(self):
        pkcs11 = PK11.PyKCS11Lib()
        if sys.platform == 'win32':
            dllpath = os.environ['PKCS11_MODULE']
        else:
            dllpath = \
                '/usr/lib/WatchData/ProxKey/lib/libwdpkcs_SignatureP11.so'
        pkcs11.load(dllpath)

        try:
            serial_number = pkcs11.getTokenInfo(0).serialNumber
            return serial_number.strip()
        except Exception as e:
            return None
