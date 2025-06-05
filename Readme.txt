Fortran Document Generator Readme
=================================

GitHub Page: https://github.com/cmbant/fordocs

## Features

✨ **Interactive Tree Diagrams**: Zoom, pan, and explore class hierarchies with modern visualization
🎨 **Dark/Light Theme**: Toggle between themes for comfortable viewing
📱 **Responsive Design**: Works perfectly on desktop, tablet, and mobile devices
🔍 **Zoom Controls**: Built-in zoom in/out and fit-to-view functionality
🚀 **Modern UI**: Bootstrap 5 with cards, icons, and smooth animations

## Installation

### Option 1: Modern Python (Recommended)
Install using the modern pyproject.toml configuration:

	pip install -e .

## Usage

This generator extracts classes, functions, subroutines, and dependencies from Fortran files (*.f90) and creates modern, interactive documentation.

### Basic Usage
	python fordocs.py <SourceDirectory/ies> <OutputDirectory>

### Example
	python fordocs.py cosmomc/source/ fordocs/output

The script automatically finds every file matching the pattern recursively under the SourceDirectory root.

### Tree Diagram Features
Once generated, open the documentation in a web browser to enjoy:
- **Interactive Navigation**: Click tree nodes to jump to class documentation
- **Zoom & Pan**: Use mouse wheel to zoom, drag to pan around large trees
- **Theme Toggle**: Click the theme button in the navbar to switch between light/dark modes
- **Mobile Friendly**: Tree diagrams automatically adapt to smaller screens
- **Export**: Download tree diagrams as PNG images using the download button
	

## Advanced Options

Run `python fordocs.py -h` to see the full list of optional parameters:

	usage: fordocs.py [-h] [--file_pattern FILE_PATTERN] [--title TITLE]
                  [--define DEFINE [DEFINE ...]]
                  [--excludes EXCLUDES [EXCLUDES ...]]
                  [--excludes_file EXCLUDES_FILE]
                  source_folders [source_folders ...] output_folder

positional arguments:
  source_folders        The directory in which to search for Fortran files,
                        recursively
  output_folder         The directory in which documentation will be generated

optional arguments:
  -h, --help            show this help message and exit
  --file_pattern FILE_PATTERN
  --title TITLE         The title used in the documentation tab and index link
  --define DEFINE [DEFINE ...]
                        list of preprocessor definitions
  --class_tree_splits CLASS_TREE_SPLITS [CLASS_TREE_SPLITS ...]
                        list of class names to show separately in class tree
                        index (rather than as part of larger big tree)
  --excludes EXCLUDES [EXCLUDES ...]
                        list of file name patterns to exclude
  --excludes_file EXCLUDES_FILE
                        file containing list of file names to exclude

