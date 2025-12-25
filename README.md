# How to Play the Game
## Setting Up the Environment
Make sure you have downloaded [Python 3.13.9](https://www.python.org/downloads/) onto your computer. You can also use `winget` to download Python.
```
winget search Python.Python.3.13.9
winget install --id Python.Python.3.13.9
```
Navigate to your desired directory. Make sure it is empty.
```
cd path/to/your/desired/directory
```
Run the `git clone` command.
```
git clone https://github.com/ethnjs/columns.git
```
Make the virtual environment.
```
python -3.13.9 -m venv venv
```
Activate the virtual environment.
```
cd venv/Scripts
activate
```
Install required dependencies.
```
pip install -r requirements.txt
```
## Playing the Game
Either:
1. Open the source code in VS Code and press play on the `main.py` file.
2. Run the following command in `./venv/Scripts`.
```
python ../../src/main.py
```