# SAT Project
## Requirements
-----
 * Tested on Python 3.5.2+
 * [pycosat](https://pypi.python.org/pypi/pycosat)
 * [Pillow(Only for generating the dataset)](https://pillow.readthedocs.io/en/latest/installation.html)
### Optional
 * [pytesseract(Only for generating the dataset)](https://github.com/madmaze/pytesseract)

## Usage
-----
To generate the dataset from scratch:
```
python3 kropki_generate.py -dpw
```

To solve a sudoku with the naive encoding:
```
python3 kropki_solve.py
```

To solve a sudoku with the improved encoding:
```
python3 enc_kropki.py
```
