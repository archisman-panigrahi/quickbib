# QuickBib

This is a python package that allows you to get the bibtex entry from a DOI number. It uses [doi2bib3](https://github.com/archisman-panigrahi/doi2bib3) as its backend. It is licensed under GPLv3.
 
![screenshot](assets/screenshots/quickbib_arxiv.png)

## How to install?

### GNU/Linux
<a href="https://repology.org/project/quickbib/versions">
    <img src="https://repology.org/badge/vertical-allrepos/quickbib.svg" alt="Packaging status" align="right">
</a>

 - On Arch Linux, you can get it from the AUR

```
yay -S quickbib
```

- On Ubuntu (24.04+), you can use our [official PPA](https://code.launchpad.net/~apandada1/+archive/ubuntu/quickbib)
```
sudo add-apt-repository ppa:apandada1/quickbib
sudo apt update
sudo apt install quickbib
```

- Other distros: Install from source
Install the required dependencies, pyqt6 and [doi2bib3](https://github.com/archisman-panigrahi/doi2bib3). Afterwards, you can use meson to install quickbib.
```
meson setup builddir --prefix="$HOME/.local"
meson install -C builddir
```

To uninstall, 
```
meson uninstall -C builddir
```
### Windows and MacOS
Prebuilt installers are available to download in the [Releases](https://github.com/archisman-panigrahi/quickbib/releases) section.

## How to run from source?

First, clone this repo.

```
git clone https://github.com/archisman-panigrahi/quickbib.git
cd quickbib
```

Then, run it with

```
python3 -m quickbib
```
