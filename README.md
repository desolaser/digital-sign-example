# Automated digital sign system

This system made on python is used to sign deeds and certficates automatically
and upload them to fojas repository without effort.
# Usage

```bash
cd cbrpv-digital-sign
# Create virtualenv
py -m venv venv
# On windows
venv\Scripts\Activate
# On linux
source venv/bin/activate
# Install dependencies
pip install -r requirements.txt
# Run program
py main.py
```

# How it works?

The progrma has a watchdog, aka. an observer that listens for changes on
files folder. If a pdf is inserted on files folder the program will
automatically sign that file and add the qr code with fojas link in
the left border of all pdf pages.

