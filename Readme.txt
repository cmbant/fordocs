Fortran Document Generator Readme
=================================

This generator will extract the classes, function, subroutine and dependencies from every file (*.f90) of the project.
In order to use the generator, Please prepare an output folder and run the following:

    python fordocs.py <SourceDirectory> <OutputDirectory>

ex:
    python fordocs.py cosmomc/source/ fordocs/output
		
The script will automatically find every file matching the pattern recursively under the SourceDirectory root.
Run forfocs.py without arguments to see list of optional parameters.



Important Info
==============

Please make sure that:
1. The following files are included inside the script's folder:
    - class_template.html
    - module_template.html
    - file_template.html		
	- index_template.html
    - fortran_parser.py
    - doc_generator.py
    - fordocs.py
    - assets.zip


2. The following prerequisites are met (pip - python package manager):
    - Install Jinja2 Template engine:
        pip install jinja2

    - Install treelib:
        pip install treelib

