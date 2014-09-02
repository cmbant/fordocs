Fortran Document Generator Readme
=================================

GitHub Page: https://github.com/cmbant/fordocs


1- Install the requirements from the included requirements.txt:

	pip install -r requirements.txt

2- Using the program:

	This generator will extract the classes, function, subroutine and dependencies from every file (*.f90) of the project.
	In order to use the generator, run the following:
	
	    python fordocs.py <SourceDirectory/ies> <OutputDirectory>
	
	ex:
	    python fordocs.py cosmomc/source/ fordocs/output
			
	The script will automatically find every file matching the pattern recursively under the SourceDirectory root.
	

Run forfocs.py -h to see list of optional parameters, for example exclusion list:

	usage: fordocs.py [-h] [--file_pattern FILE_PATTERN] [--title TITLE]
                  [--define DEFINE [DEFINE ...]]
                  [--excludes EXCLUDES [EXCLUDES ...]]
                  [--excludes_file EXCLUDES_FILE]
                  source_folders [source_folders ...] output_folder

Fortran Documentation generator

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
  --excludes EXCLUDES [EXCLUDES ...]
                        list of file name patterns to exclude
  --excludes_file EXCLUDES_FILE
                        file containing list of file names to exclude
	
