# pyweek32-neverending

## Setup

Note that the arcade library requires OpenGL 3.3 and thus won't currently run on a Raspberry Pi.

Install Python 3.9.7. Older versions may work as well. I used pyenv on a Mac, but you can do whatever suits you:

```
brew update && brew upgrade pyenv
pyenv install 3.9.7
# Restarted my shell.
```

Setup a virtualenv using the right version of Python. I used pyenv, but that's optional:

```
pyenv global 3.9.7
python --version
python -m venv ~/.virtualenvs/pyweek32-neverending
pyenv global system
python --version
```

Check out the source code:

```
# Switch to some directory where you can checkout the code.
git clone https://github.com/jjinux/pyweek32-neverending.git
cd pyweek32-neverending
```

Install requirements:

```
# Make sure you're in the directory containing the source code.
. ~/.virtualenvs/pyweek32-neverending/bin/activate
pip install -r requirements.txt
```

## Running

```
. ~/.virtualenvs/pyweek32-neverending/bin/activate
./run_game.py
```

## Developing

```
. ~/.virtualenvs/pyweek32-neverending/bin/activate
make help
make test
```
