virtualenv -p python3 virtual
export FLASK_APP=twidder
sudo apt install libpq-dev python3.10-dev
source virtual/bin/activate
pip install --upgrade pip
pip install selenium
pip install -e .
gunicorn -w 1 -b 127.0.0.1:5000 --threads 100 twidder:app