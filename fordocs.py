"""
Fortran source code documentation generator; https://github.com/cmbant/fordocs

@author: Mohammed Hamdy
@author: Antony Lewis

"""

import time

from lib.dbmaker import ModelFiller
from lib.docmaker import HTMLDocMaker

NOISY = True


def generate_docs(
    sourceDirectories,
    destinationDirectory,
    match_pattern="*.*90",
    title="Fortran Documentation",
    defines=[],
    excludes=[],
    excludes_file=None,
    class_tree_splits=[],
    github_root=None,
    github_subdir=None,
):
    mf = ModelFiller(defines)
    if NOISY:
        print("Phase #1: Parsing source files into database")
        t = time.time()
    if excludes_file:
        excludes.append(open(excludes_file).readlines())
    mf.fillModel(sourceFolders=sourceDirectories, match=match_pattern, excludes=excludes)
    if NOISY:
        print(f"Phase #1: Finished <parsed {mf.fileCount():d} files in {(time.time() - t) / 60:.2f} minutes>")
        print()
        print("Phase #2: Generating documentation")

    dm = HTMLDocMaker(destinationDirectory, title, class_tree_splits, github_root, sourceDirectories, github_subdir)
    dm.makeDocs()
    if NOISY:
        print("Phase #2: Finished")
        print("Done")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Fortran Documentation generator")
    parser.add_argument(
        "source_folders",
        nargs="+",
        help="The directory in which to search for Fortran files, recursively",
    )
    parser.add_argument("output_folder", help="The directory in which documentation will be generated")
    parser.add_argument("--file_pattern", default="*.*90")
    parser.add_argument(
        "--title",
        default="Fortran Documentation",
        help="The title used in the documentation tab and index link",
    )
    parser.add_argument("--define", nargs="+", help="list of preprocessor definitions")
    parser.add_argument(
        "--class_tree_splits",
        nargs="+",
        help="list of class names to show separately in class tree index (rather than as part of larger big tree)",
    )

    parser.add_argument("--excludes", nargs="+", help="list of file name patterns to exclude")
    parser.add_argument("--excludes_file", help="file containing list of file names to exclude")
    parser.add_argument(
        "--github_root",
        help="GitHub repository root URL for hyperlinking to source files (e.g., https://github.com/cmbant/camb)",
    )
    parser.add_argument(
        "--github_subdir",
        help="Subdirectory within GitHub repository where source files are located (e.g., 'fortran' for CAMB)",
    )

    args = parser.parse_args()
    generate_docs(
        args.source_folders,
        args.output_folder,
        match_pattern=args.file_pattern,
        title=args.title,
        defines=args.define,
        excludes=args.excludes,
        excludes_file=args.excludes_file,
        class_tree_splits=args.class_tree_splits,
        github_root=args.github_root,
        github_subdir=args.github_subdir,
    )
