
from __future__ import print_function, division
from lib.dbmaker import ModelFiller
from lib.docmaker import HTMLDocMaker
import time, sys
NOISY = True

def generate_docs(sourceDirectory, destinationDirectory, docTitle, defines):

    mf = ModelFiller(sourceDirectory, defines)
    if NOISY:
        print("Phase #1: Parsing source files into database")
        t = time.time()
    mf.fillModel()
    if NOISY:
        print("Phase #1: Finished <parsed {:d} files in {:.2f} minutes>".format(mf.fileCount(), (time.time()-t) / 60))
        print()
        print("Phase #2: Generating documentation")
      
    dm = HTMLDocMaker(destinationDirectory, docTitle)
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
    parser.add_argument('source_folder', help="The directory in which to search for Fortran files, recursively")    
    parser.add_argument('output_folder', help="The directory in which documentation will be generated")
#    parser.add_argument('--file_pattern', default='*.*90' )
    parser.add_argument('--title', default="Fortran Documentation", help="The title used in the documentation tab and index link")
    parser.add_argument('--define', nargs='+', default=[])
    
    args =  parser.parse_args()
    generate_docs(args.source_folder, args.output_folder, args.title, args.define)
