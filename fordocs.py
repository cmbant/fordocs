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
):
    mf = ModelFiller(defines)
    if NOISY:
        print("Phase #1: Parsing source files into database")
        t = time.time()
    if excludes_file:
        excludes.append(open(excludes_file).readlines())
    mf.fillModel(
        sourceFolders=sourceDirectories, match=match_pattern, excludes=excludes
    )
    if NOISY:
        print(
            f"Phase #1: Finished <parsed {mf.fileCount():d} files in {(time.time() - t) / 60:.2f} minutes>"
        )
        print()
        print("Phase #2: Generating documentation")

    dm = HTMLDocMaker(destinationDirectory, title, class_tree_splits)
    dm.makeDocs()
    if NOISY:
        print("Phase #2: Finished")
        print("Done")


# if __name__ == "__main__":
#     generate_docs(
#         [r"c://work/dist/git/camb"],
#         r"z:\testoutfull",
#         "*.f90",
#         "Fortran CAMB Documentation",
#         excludes=[
#             "sigma8.f90",
#             "second_PT*",
#             "tester*",
#             "Inspector*",
#             "forutils*",
#             "cosmorec*",
#             "hyrec*",
#             "writefits*",
#         ],
#         class_tree_splits=["TCambComponent"],
#     )

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Fortran Documentation generator")
    parser.add_argument(
        "source_folders",
        nargs="+",
        help="The directory in which to search for Fortran files, recursively",
    )
    parser.add_argument(
        "output_folder", help="The directory in which documentation will be generated"
    )
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

    parser.add_argument(
        "--excludes", nargs="+", help="list of file name patterns to exclude"
    )
    parser.add_argument(
        "--excludes_file", help="file containing list of file names to exclude"
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
    )
