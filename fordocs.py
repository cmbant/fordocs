
'''
Fortran source code documentation generator; https://github.com/cmbant/fordocs

@author: Mohammed Hamdy
@author: Antony Lewis

'''

from __future__ import print_function, division
from lib.dbmaker import ModelFiller
from lib.docmaker import HTMLDocMaker
import time, sys
NOISY = True

def generate_docs(sourceDirectories, destinationDirectory, match_pattern='*.*90', title="Fortran Documentation",
                   defines=[], excludes=[], excludes_file=None, class_tree_splits=[]):

    mf = ModelFiller(defines)
    if NOISY:
        print("Phase #1: Parsing source files into database")
        t = time.time()
    if excludes_file:
        excludes.append(open(excludes_file, 'r').readlines())
    mf.fillModel(sourceFolders=sourceDirectories, match=match_pattern, excludes=excludes)
    if NOISY:
        print("Phase #1: Finished <parsed {:d} files in {:.2f} minutes>".format(mf.fileCount(), (time.time() - t) / 60))
        print()
        print("Phase #2: Generating documentation")
      
    dm = HTMLDocMaker(destinationDirectory, title, class_tree_splits)
    dm.makeDocs()
    if NOISY:
        print("Phase #2: Finished")
        print("Done")

if __name__ == "__main__":
    try: 
        import argparse
    except:
        print('this code requires Python 2.7+')
        sys.exit()
        
    parser = argparse.ArgumentParser(description="Fortran Documentation generator")
    parser.add_argument('source_folders', nargs='+', help="The directory in which to search for Fortran files, recursively")
    parser.add_argument('output_folder', help="The directory in which documentation will be generated")
    parser.add_argument('--file_pattern', default='*.*90')
    parser.add_argument('--title', default="Fortran Documentation", help="The title used in the documentation tab and index link")
    parser.add_argument('--define', nargs='+', help="list of preprocessor definitions")
    parser.add_argument('--class_tree_splits', nargs='+',
                        help="list of class names to show separately in class tree index (rather than as part of larger big tree)")
    
    parser.add_argument('--excludes', nargs='+', help="list of file name patterns to exclude")
    parser.add_argument('--excludes_file', help="file containing list of file names to exclude")
    
    args = parser.parse_args()
    generate_docs(args.source_folders, args.output_folder, match_pattern=args.file_pattern, title=args.title,
                  defines=args.define, excludes=args.excludes, excludes_file=args.excludes_file, class_tree_splits=args.class_tree_splits)
