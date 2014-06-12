import sys
import doc_generator
import zipfile,os.path

"""Program to make automated documentation from Fortran 2003 code"""

def generate_docs(source_path, match_pattern, output_path, title=None, conditional_defines=[]):
    
    if not os.path.exists(output_path): os.makedirs(output_path)

    dg = doc_generator.doc_generator()
    
    print 'Generating documentation files...'
    dg.generate_docs(source_path, match_pattern, output_path, title, conditional_defines)

    print 'Generating index file...'
    dg.generate_index(output_path)
    
    print 'Copying assets...'
    zipfile.ZipFile( os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets.zip')).extractall(output_path)
    #unzip( os.path.dirname(os.path.abspath(__file__)) + os.sep + 'assets.zip', output_path)
    
    print 'Done.'

if __name__ == '__main__':
    try: import argparse
    except:
        print 'this code requires Python 2.7+'
        sys.exit()
        
    parser = argparse.ArgumentParser(description="Fortan Documentation generator")
    parser.add_argument('source_folder')    
    parser.add_argument('output_folder')
    parser.add_argument('--file_pattern', default='*.*90' )
    parser.add_argument('--title', default=None)
    parser.add_argument('--define', nargs='+', default=[])
    
    args =  parser.parse_args()

    generate_docs(args.source_folder, args.file_pattern, args.output_folder, args.title, args.define)