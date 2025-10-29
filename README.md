# quickbib

This is a GUI around [doi2bib3](https://github.com/archisman-panigrahi/doi2bib3) python package that allows you to get the bibtex entry from a DOI number.
 
![screenshot](assets/screenshots/quickbib_arxiv.png)

## How to run?

First, clone this repo.

```
git clone https://github.com/archisman-panigrahi/quickbib.git
cd quickbib
```

Then, run it with

```
python3 -m quickbib
```

## How to install?

First, install the required dependencies, pyqt6 and [doi2bib3](https://github.com/archisman-panigrahi/doi2bib3). Afterwards, you can use meson to install quickbib.

```
meson setup builddir --prefix="$HOME/.local"
meson install -C builddir
```

To uninstall,
```
meson uninstall -C builddir
```