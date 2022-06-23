import os
import sys
import datetime
import PyKCS11 as PK11
from endesive import pdf, hsm
from decouple import config
from src.database_helper import DatabaseHelper
from src.token_detector import TokenDetector
from endesive.pdf.PyPDF2_annotate.util.validation import instance_of

TOKEN_PASSWORD = config('TOKEN_PASSWORD')
DEVICE_NAME = config('DEVICE_NAME')

if sys.platform == 'win32':
    dllpath = os.environ['PKCS11_MODULE']
else:
    dllpath = '/usr/lib/WatchData/ProxKey/lib/libwdpkcs_SignatureP11.so'

database_helper = DatabaseHelper()
token_detector = TokenDetector(database_helper)

class Signer(hsm.HSM):
    token = None

    def __init__(self, dllpath, token):
        self.token = token
        super().__init__(dllpath)

    def certificate(self):
        self.login(self.token["device"], self.token["password"])
        try:
            pk11objects = self.session.findObjects(
                [(PK11.CKA_CLASS, PK11.CKO_CERTIFICATE)])
            all_attributes = [
                # PK11.CKA_SUBJECT,
                PK11.CKA_VALUE,
                # PK11.CKA_ISSUER,
                # PK11.CKA_CERTIFICATE_CATEGORY,
                # PK11.CKA_END_DATE,
                PK11.CKA_ID,
            ]

            for pk11object in pk11objects:
                try:
                    attributes = self.session.getAttributeValue(
                        pk11object, all_attributes)
                except PK11.PyKCS11Error as e:
                    print(e)
                    continue

                attrdict = dict(list(zip(all_attributes, attributes)))
                cert = bytes(attrdict[PK11.CKA_VALUE])
                return bytes(attrdict[PK11.CKA_ID]), cert
        except Exception:
            print("Session is not initialized")
        finally:
            self.logout()
        return None, None

    def sign(self, keyid, data, mech):
        self.login(self.token["device"], self.token["password"])
        try:
            priv_key = self.session.findObjects(
                [(PK11.CKA_CLASS, PK11.CKO_PRIVATE_KEY)])[0]
            mech = getattr(PK11, 'CKM_%s_RSA_PKCS' % mech.upper())
            sig = self.session.sign(priv_key, data, PK11.Mechanism(mech, None))
            return bytes(sig)
        except Exception:
            print("Session is not initialized")
        finally:
            self.logout()


def sign_pdf(file_input, file_output):    
    token = token_detector.find_token()
    print(token)
    if token is None:
        print("Error al firmar el PDF, no se ha encontrado \
el token o el token es inválido")
        return

    date = datetime.datetime.utcnow()
    date = date.strftime('%Y%m%d%H%M%S+00\'00\'')
    sign_params = {
        "sigflags": 3,
        "sigpage": 0,
        "sigbutton": True,
        "contact": token["contact"],
        "location": 'Puerto Varas - Chile',
        "signingdate": date.encode(),
        "reason": 'Conservador de Bienes Raices de Puerto Varas',
        "signature": token["signature"],
        "signaturebox": (50, 0, 500, 50),
    }
    clshsm = Signer(dllpath, token)
    fname = file_input

    if not os.path.exists(fname):
        raise FileNotFoundError("File wasn't found in the file system")

    try:
        data_pdf = open(fname, 'rb').read()
    except (IOError, OSError) as e:
        raise e

    data_sign = pdf.cms.sign(
        data_pdf,
        sign_params,
        None, None,
        [],
        'sha256',
        clshsm,
    )
    # fname = fname.replace('.pdf', '-signed.pdf')
    with open(file_output, 'wb') as fp:
        fp.write(data_pdf)
        fp.write(data_sign)
