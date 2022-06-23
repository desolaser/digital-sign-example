from src.signer import sign_pdf
from src.qrcode import create_qrcode, insert_qrcode

if __name__ == "__main__":
    insert_qrcode('./example.pdf', './files/example.pdf', 123456888621)
    sign_pdf('./files/example.pdf', './files/example-sign.pdf')
