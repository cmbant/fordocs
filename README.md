# Fortran Documentation Generator

A modern, interactive documentation generator for Fortran projects that creates beautiful HTML documentation with tree diagrams, GitHub integration, and responsive design.

## ✨ Features

- **📊 Interactive Tree Diagrams**: Zoom, pan, and explore class hierarchies with modern visualization
- **🎨 Dark/Light Theme**: Toggle between themes for comfortable viewing
- **📱 Responsive Design**: Works perfectly on desktop, tablet, and mobile devices
- **🔍 Zoom Controls**: Built-in zoom in/out and fit-to-view functionality
- **🚀 Modern UI**: Bootstrap 5 with cards, icons, and smooth animations
- **🔗 GitHub Integration**: Direct links to source files on GitHub for easy cross-reference
- **📁 Comprehensive Parsing**: Extracts classes, functions, subroutines, modules, and dependencies

## 🚀 Installation

### Option 1: Modern Python (Recommended)

Install using the modern pyproject.toml configuration:

```bash
pip install -e .
```

### Option 2: Direct Usage

Clone the repository and run directly:

```bash
git clone https://github.com/cmbant/fordocs.git
cd fordocs
python fordocs.py <source_directories> <output_directory>
```

## 📖 Usage

This generator extracts classes, functions, subroutines, and dependencies from Fortran files (\*.f90) and creates modern, interactive documentation.

### Basic Usage

```bash
python fordocs.py <SourceDirectory/ies> <OutputDirectory>
```

### 🌳 Class Hierachy Tree Diagrams

Once generated, open the documentation in a web browser to enjoy:

- **Interactive Navigation**: Click tree nodes to jump to class documentation
- **Zoom & Pan**: Use mouse wheel to zoom, drag to pan around large trees
- **Theme Toggle**: Click the theme button in the navbar to switch between light/dark modes
- **Mobile Friendly**: Tree diagrams automatically adapt to smaller screens
- **Export**: Download tree diagrams as PNG images using the download button

## ⚙️ Advanced Options

Run `python fordocs.py -h` to see the full list of optional parameters:

```
usage: fordocs.py [-h] [--file_pattern FILE_PATTERN] [--title TITLE]
                  [--define DEFINE [DEFINE ...]]
                  [--class_tree_splits CLASS_TREE_SPLITS [CLASS_TREE_SPLITS ...]]
                  [--excludes EXCLUDES [EXCLUDES ...]]
                  [--excludes_file EXCLUDES_FILE]
                  [--github_root GITHUB_ROOT]
                  source_folders [source_folders ...] output_folder

positional arguments:
  source_folders        The directory in which to search for Fortran files,
                        recursively
  output_folder         The directory in which documentation will be generated

optional arguments:
  -h, --help            show this help message and exit
  --file_pattern FILE_PATTERN
                        File pattern to match (default: *.*90)
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
  --github_root GITHUB_ROOT
                        GitHub repository root URL for hyperlinking to source
                        files (e.g., https://github.com/cmbant/camb)
  --github_subdir GITHUB_SUBDIR
                        Subdirectory within GitHub repository where source
                        files are located (e.g., 'fortran' for CAMB)
```

### 🔗 GitHub Integration

The `--github_root` option enables direct linking to source files on GitHub:

```bash
python fordocs.py source/ docs/ --github_root https://github.com/username/repository
```

For repositories where source files are in a subdirectory, use `--github_subdir`:

```bash
python fordocs.py camb/fortran/ docs/ --github_root https://github.com/cmbant/camb --github_subdir fortran
```

This adds "View Source" buttons to file, program, and module documentation pages that link directly to the corresponding files on GitHub, making it easy for users to browse the actual source code.

## 🛠️ Development

### Testing

The codebase includes a test file `makeCAMB.py` that should work for testing the documentation generation.

### Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 👥 Authors

- **Mohammed Hamdy** and **AI agent** - Original authors
- **Antony Lewis** - Maintainer and manager

## 🔗 Links

- [GitHub Repository](https://github.com/cmbant/fordocs)
- [Issues](https://github.com/cmbant/fordocs/issues)
- [Pull Requests](https://github.com/cmbant/fordocs/pulls)
