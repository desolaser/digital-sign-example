import os
import sys
import datetime
from endesive import pdf, hsm
from decouple import config

TOKEN_PASSWORD = config('TOKEN_PASSWORD')
DEVICE_NAME = config('DEVICE_NAME')

if sys.platform == 'win32':
    dllpath = os.environ['PKCS11_MODULE']
else:
    dllpath = '/usr/lib/WatchData/ProxKey/lib/libwdpkcs_SignatureP11.so'

import PyKCS11 as PK11


class Signer(hsm.HSM):
    def certificate(self):
        self.login(DEVICE_NAME, TOKEN_PASSWORD)
        keyid = [0x02, 0xa1, 0xb7, 0x9d]
        keyid = bytes(keyid)
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
                    continue

                attrDict = dict(list(zip(all_attributes, attributes)))
                cert = bytes(attrDict[PK11.CKA_VALUE])
                # if keyid == bytes(attrDict[PK11.CKA_ID]):
                return bytes(attrDict[PK11.CKA_ID]), cert
        finally:
            self.logout()
        return None, None

    def sign(self, keyid, data, mech):
        self.login(DEVICE_NAME, TOKEN_PASSWORD)
        try:
            privKey = self.session.findObjects(
                [(PK11.CKA_CLASS, PK11.CKO_PRIVATE_KEY)])[0]
            mech = getattr(PK11, 'CKM_%s_RSA_PKCS' % mech.upper())
            sig = self.session.sign(privKey, data, PK11.Mechanism(mech, None))
            return bytes(sig)
        finally:
            self.logout()


def sign_pdf():
    date = datetime.datetime.utcnow() - datetime.timedelta(hours=12)
    date = date.strftime('%Y%m%d%H%M%S+00\'00\'')
    signParams = {
        "sigflags": 3,
        "sigpage": 0,
        "sigbutton": True,
        "contact": "MACARENA.MOLINA.CORTES322@GMAIL.COM",
        "location": 'Puerto Varas - Chile',
        "signingdate": date.encode(),
        "reason": 'Conservador de Bienes Raices de Puerto Varas',
        "signature": 'MACARENA CONSTANZA MOLINA CORTES',
        "signaturebox": (50, 0, 500, 50),
    }
    clshsm = Signer(dllpath)
    fname = './pdf/hello.pdf'
    dataPdf = open(fname, 'rb').read()
    dataSign = pdf.cms.sign(
        dataPdf, 
        signParams,
        None, None,
        [],
        'sha256',
        clshsm,
    )
    fname = fname.replace('.pdf', '-signed.pdf')
    with open(fname, 'wb') as fp:
        fp.write(dataPdf)
        fp.write(dataSign)
