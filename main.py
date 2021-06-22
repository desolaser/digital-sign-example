import time
from decouple import config
from src.file_observer import create_file_observer

INPUT_FOLDER = config('INPUT_FOLDER')

if __name__ == "__main__":
    file_observer = create_file_observer(INPUT_FOLDER)
    file_observer.start()
    try:
        while True:
            time.sleep(5)
    except KeyboardInterrupt:
        file_observer.stop()
        file_observer.join()


'''
sign_pdf()
image_path, text = create_qrcode(document_code)
insert_qrcode(image_path, text)
'''
