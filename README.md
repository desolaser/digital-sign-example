# Automated digital sign system

This is an example for digital sign automation, to sign pdfs with Safenet
eToken made in Python. It was made specifically to sign and mark with a qrcode
pdf files with property inscriptions that will be uploaded to [fojas](https://www.fojas.cl/index2.php) 
page. 

But you could remove **insert_qrcode** function call in **file_observer.py** to
sign the files in **files** folder without marking them. 

# Requisites

- Download [Safenet Authentication Client Tools](https://knowledge.digicert.com/generalinformation/INFO1982.html).
- You should have an eToken. 
- SafeNet eToken 5110 FIPS is recommended, is not tested on other tokens, so
i don't know if the program will work correctly with other models.
- You should have [Python](https://www.python.org/downloads/) installed.
- You also need virtualenv, once you have python you can install it with ```pip install virtualenv```.

# Configure

First, you should copy .env.example and name the new file as .env. Then
configure the variables, the description of each variable should be available
in [Environment Variables](#environment-variables) section.

```bash
# Clone the repository
git clone https://github.com/desolaser/digital-sign-example.git
# Enter to the root folder
cd digital-sign-example
# Create virtualenv
py -m venv venv
# On windows
.\venv\Scripts\Activate
# On linux
source venv/bin/activate
# Install dependencies
pip install -r requirements.txt
```

# Description

The program runs with pyodbc, that is used to query the token information from
a database. This is used to automatically detect the authorized tokens when
connected in the computer, so you don't need to insert the password every
time you run the program.

You can use add-token.py to add a new token to database and use it later.

## main.py

This program has a watchdog, aka. an observer that listens for changes on
files folder. If a pdf is inserted on **files** folder the program will
automatically sign that file and add the qr code with fojas link in
the left border of all pdf pages.

## info.py

It's an utility to get the info of SafeNet eToken Slots and the eTokens inside
the slots.

Credits: Ludovic Rousseau (ludovic.rousseau@free.fr).

## sign-test.py

You can use this to sign only one pdf. This is used for integration testing
purposes.

# Environment Variables

## General variables

* **INPUT_FOLDER:** Folder that will be observed by file_observer. You should
drop the files there to sign the files.

## Database variables

* **DB_DRIVER:** Database driver.
* **DB_SERVER:** Server IP or MS SQL Instance name.
* **DB_DATABASE_NAME:** Database name.
* **DB_USER:** Database user.
* **DB_PASS:** Database password.