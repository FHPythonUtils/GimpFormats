[![GitHub top language](https://img.shields.io/github/languages/top/FHPythonUtils/GimpFormats.svg?style=for-the-badge&cacheSeconds=28800)](../../)
[![Issues](https://img.shields.io/github/issues/FHPythonUtils/GimpFormats.svg?style=for-the-badge&cacheSeconds=28800)](../../issues)
[![License](https://img.shields.io/github/license/FHPythonUtils/GimpFormats.svg?style=for-the-badge&cacheSeconds=28800)](/LICENSE.md)
[![Commit activity](https://img.shields.io/github/commit-activity/m/FHPythonUtils/GimpFormats.svg?style=for-the-badge&cacheSeconds=28800)](../../commits/master)
[![Last commit](https://img.shields.io/github/last-commit/FHPythonUtils/GimpFormats.svg?style=for-the-badge&cacheSeconds=28800)](../../commits/master)
[![PyPI Downloads](https://img.shields.io/pypi/dm/gimpformats.svg?style=for-the-badge&cacheSeconds=28800)](https://pypistats.org/packages/gimpformats)
[![PyPI Total Downloads](https://img.shields.io/pepy/dt/gimpformats?style=for-the-badge&label=Total%20Downloads&cacheSeconds=28800)](https://pepy.tech/project/attestationcheck)
[![PyPI Version](https://img.shields.io/pypi/v/gimpformats.svg?style=for-the-badge&cacheSeconds=28800)](https://pypi.org/project/gimpformats)

<!-- omit in toc -->
# GimpFormats

<img src="readme-assets/icons/name.png" alt="Project Icon" width="750">

Forked from https://github.com/TheHeadlessSourceMan/gimpFormats

A pure python implementation of the GIMP XCF image format. Use this to interact
with GIMP image formats

Issues and contributions very much wanted/ needed 😀

- [Getting started](#getting-started)
- [Next tasks (see below)](#next-tasks-see-below)
- [Currently supports](#currently-supports)
- [In progress but results in crashes and tests failing](#in-progress-but-results-in-crashes-and-tests-failing)
- [Not implemented](#not-implemented)
- [Documentation](#documentation)
- [Install With PIP](#install-with-pip)
- [Language information](#language-information)
	- [Built for](#built-for)
- [Install Python on Windows](#install-python-on-windows)
	- [Chocolatey](#chocolatey)
	- [Windows - Python.org](#windows---pythonorg)
- [Install Python on Linux](#install-python-on-linux)
	- [Apt](#apt)
	- [Dnf](#dnf)
- [Install Python on MacOS](#install-python-on-macos)
	- [Homebrew](#homebrew)
	- [MacOS - Python.org](#macos---pythonorg)
- [How to run](#how-to-run)
	- [Windows](#windows)
	- [Linux/ MacOS](#linux-macos)
- [Building](#building)
- [Testing](#testing)
- [Download Project](#download-project)
	- [Clone](#clone)
		- [Using The Command Line](#using-the-command-line)
		- [Using GitHub Desktop](#using-github-desktop)
	- [Download Zip File](#download-zip-file)
- [Community Files](#community-files)
	- [Licence](#licence)
	- [Changelog](#changelog)
	- [Code of Conduct](#code-of-conduct)
	- [Contributing](#contributing)
	- [Security](#security)
	- [Support](#support)
	- [Rationale](#rationale)

## Getting started

Read an image

```python
from gimpformats.gimpXcfDocument import GimpDocument
project = GimpDocument("image.xcf")
```

Iterate the image and report the contents of each group followed by the first
level children of the image

```python
"""Output Gimp Layers and Groups."""

from __future__ import annotations

from gimpformats.gimpXcfDocument import GimpDocument, GimpGroup

# ruff: noqa: T201


def cat_group(group: GimpGroup, i: int = 0) -> None:
	"""Output layers in group."""
	for idx, child in enumerate(group.children):
		if isinstance(child, GimpGroup):
			print("\t" * i, idx, child.layer_options)
			cat_group(child, i + 1)
		else:
			print("\t" * i, idx, child)


def catXCF(file: str) -> None:
	"""Open an .xcf file into a layered image."""
	project = GimpDocument(file)
	root_goup = project.walkTree()
	print()
	print("=" * 60)
	print("=", project.fileName)
	print("=" * 60)
	cat_group(root_goup)


catXCF("test_files/test.xcf")
catXCF("test_files/base24.xcf")
```

Example output:

```none

============================================================
= test.xcf
============================================================
 0 <GimpLayer name=Layer Group uniqueId='00000003', itemPath=None, visible=True, opacity=1.00, blendMode=GimpBlendMode.NORMAL, xOffset=0, yOffset=0, positionLocked=False, isGroup=True, groupItemFlags=1, locked=False, lockAlpha=False, editingMask=False>
         0 <GimpLayer name=Background uniqueId='00000002', itemPath=[0, 0], visible=True, opacity=1.00, blendMode=GimpBlendMode.NORMAL, xOffset=0, yOffset=0, positionLocked=False, isGroup=None, groupItemFlags=0, locked=False, lockAlpha=False, editingMask=False>

============================================================
= base24.xcf
============================================================
 0 <GimpLayer name=bg #1 uniqueId='00000006', itemPath=None, visible=True, opacity=1.00, blendMode=GimpBlendMode.NORMAL, xOffset=115, yOffset=115, positionLocked=False, isGroup=None, groupItemFlags=0, locked=False, lockAlpha=False, editingMask=False>
 1 <GimpLayer name=bg uniqueId='00000005', itemPath=None, visible=True, opacity=1.00, blendMode=GimpBlendMode.NORMAL, xOffset=64, yOffset=64, positionLocked=False, isGroup=None, groupItemFlags=0, locked=False, lockAlpha=False, editingMask=False>
 2 <GimpLayer name=bg #2 uniqueId='00000007', itemPath=None, visible=False, opacity=1.00, blendMode=GimpBlendMode.NORMAL, xOffset=0, yOffset=0, positionLocked=False, isGroup=None, groupItemFlags=0, locked=False, lockAlpha=False, editingMask=False>
 3 <GimpLayer name=Transformation uniqueId='0000001e', itemPath=None, visible=True, opacity=1.00, blendMode=GimpBlendMode.NORMAL, xOffset=295, yOffset=292, positionLocked=False, isGroup=None,
groupItemFlags=0, locked=False, lockAlpha=False, editingMask=False>
 4 <GimpLayer name=Layer Group uniqueId='00000021', itemPath=None, visible=True, opacity=1.00, blendMode=GimpBlendMode.NORMAL, xOffset=0, yOffset=0, positionLocked=False, isGroup=True, groupItemFlags=1, locked=False, lockAlpha=False, editingMask=False>
         0 <GimpLayer name=Layer uniqueId='0000001f', itemPath=[4, 0], visible=True, opacity=1.00, blendMode=GimpBlendMode.NORMAL, xOffset=0, yOffset=0, positionLocked=False, isGroup=None, groupItemFlags=0, locked=False, lockAlpha=False, editingMask=False>
         1 <GimpLayer name=Layer2 uniqueId='00000020', itemPath=[4, 1], visible=True, opacity=1.00, blendMode=GimpBlendMode.NORMAL, xOffset=0, yOffset=0, positionLocked=False, isGroup=None, groupItemFlags=0, locked=False, lockAlpha=False, editingMask=False>
 5 <GimpLayer name=Background uniqueId='00000002', itemPath=None, visible=True, opacity=1.00, blendMode=GimpBlendMode.NORMAL, xOffset=0, yOffset=0, positionLocked=False, isGroup=None, groupItemFlags=0, locked=False, lockAlpha=False, editingMask=False>
```

## Next tasks (see below)

- Saving

## Currently supports

- Loading xcf files (up to current GIMP version 2.10)
- Getting image hierarchy and info
- Getting image for each layer (PIL image)
- .gbr brushes
- .vbr brushes
- .gpl palette files
- .pat pattern files
- .gtp tool presets
- Generate a flattened image
- Add new layers

## In progress but results in crashes and tests failing

- Saving
- .ggr gradients - reads/saves fine, but I need to come up with a way to get the
actual colours
- .gih brush sets - BUG: seems to have more image data per brush than what's
expected
- .gpb brush - should work, but I need some test files

## Not implemented

- Exported paths in .svg format. - Reading should be easy enough, but I need to
ensure I don't get a full-blown svg in the mix
- Standard "parasites"

## Documentation

A high-level overview of how the documentation is organized organized will help you know
where to look for certain things:

<!--
- [Tutorials](/documentation/tutorials) take you by the hand through a series of steps to get
  started using the software. Start here if you’re new.
-->
- The [Technical Reference](/documentation/reference) documents APIs and other aspects of the
  machinery. This documentation describes how to use the classes and functions at a lower level
  and assume that you have a good high-level understanding of the software.
<!--
- The [Help](/documentation/help) guide provides a starting point and outlines common issues that you
  may have.
-->

## Install With PIP

```python
pip install gimpformats
```

Head to https://pypi.org/project/gimpformats/ for more info

## Language information

### Built for

This program has been written for Python versions 3.8 - 3.11 and has been tested with both 3.8 and
3.11

## Install Python on Windows

### Chocolatey

```powershell
choco install python
```

### Windows - Python.org

To install Python, go to https://www.python.org/downloads/windows/ and download the latest
version.

## Install Python on Linux

### Apt

```bash
sudo apt install python3.x
```

### Dnf

```bash
sudo dnf install python3.x
```

## Install Python on MacOS

### Homebrew

```bash
brew install python@3.x
```

### MacOS - Python.org

To install Python, go to https://www.python.org/downloads/macos/ and download the latest
version.

## How to run

### Windows

- Module
	`py -3.x -m [module]` or `[module]` (if module installs a script)

- File
	`py -3.x [file]` or `./[file]`

### Linux/ MacOS

- Module
	`python3.x -m [module]` or `[module]` (if module installs a script)

- File
	`python3.x [file]` or `./[file]`

## Building

This project uses https://github.com/FHPythonUtils/FHMake to automate most of the building. This
command generates the documentation, updates the requirements.txt and builds the library artefacts

Note the functionality provided by fhmake can be approximated by the following

```sh
handsdown  --cleanup -o documentation/reference
poetry export -f requirements.txt --output requirements.txt
poetry export -f requirements.txt --with dev --output requirements_optional.txt
poetry build
```

`fhmake audit` can be run to perform additional checks

## Testing

For testing with the version of python used by poetry use

```sh
poetry run pytest
```

Alternatively use `tox` to run tests over python 3.8 - 3.11

```sh
tox
```

## Download Project

### Clone

#### Using The Command Line

1. Press the Clone or download button in the top right
2. Copy the URL (link)
3. Open the command line and change directory to where you wish to
clone to
4. Type 'git clone' followed by URL in step 2
	```bash
	git clone https://github.com/FHPythonUtils/GimpFormats
	```

More information can be found at
https://help.github.com/en/articles/cloning-a-repository

#### Using GitHub Desktop

1. Press the Clone or download button in the top right
2. Click open in desktop
3. Choose the path for where you want and click Clone

More information can be found at
https://help.github.com/en/desktop/contributing-to-projects/cloning-a-repository-from-github-to-github-desktop

### Download Zip File

1. Download this GitHub repository
2. Extract the zip archive
3. Copy/ move to the desired location

## Community Files

### Licence

LGPLv3 License
(See the [LICENSE](/LICENSE.txt) for more information.)

### Changelog

See the [Changelog](/CHANGELOG.md) for more information.

### Code of Conduct

Online communities include people from many backgrounds. The *Project*
contributors are committed to providing a friendly, safe and welcoming
environment for all. Please see the
[Code of Conduct](https://github.com/FHPythonUtils/.github/blob/master/CODE_OF_CONDUCT.md)
 for more information.

### Contributing

Contributions are welcome, please see the
[Contributing Guidelines](https://github.com/FHPythonUtils/.github/blob/master/CONTRIBUTING.md)
for more information.

### Security

Thank you for improving the security of the project, please see the
[Security Policy](https://github.com/FHPythonUtils/.github/blob/master/SECURITY.md)
for more information.

### Support

Thank you for using this project, I hope it is of use to you. Please be aware that
those involved with the project often do so for fun along with other commitments
(such as work, family, etc). Please see the
[Support Policy](https://github.com/FHPythonUtils/.github/blob/master/SUPPORT.md)
for more information.

### Rationale

The rationale acts as a guide to various processes regarding projects such as
the versioning scheme and the programming styles used. Please see the
[Rationale](https://github.com/FHPythonUtils/.github/blob/master/RATIONALE.md)
for more information.
