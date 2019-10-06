echo "Download pycparser"
git clone https://github.com/eliben/pycparser.git

echo "Create Python ENV"
python -m venv venv

call activate.bat

echo "Install requirements - run it manually"
pip install -r requirements.txt
