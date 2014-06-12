Fortran Document Generator Readme
=================================

This generator will extract the classes, function, subroutine and dependencies from every file (*.f90) of the project.
In order to use the generator, Please prepare an output folder and run the following:

    python fordocs.py <SourceDirectory> <match_pattern> <OutputDirectory>

ex:
    python fordocs.py cosmomc/source/ '*.f90' fordocs/output
		
The script will automatically find every file matching the pattern recursively under the SourceDirectory root.



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

2. After the script completes, unpack the assets.zip file into the output folder, creating a structure like so:
    output/
    |_ assets/
    |___ css/
    |___ js/
    |___ fonts/
    |_ <Generated HTML Files>

    Be sure to keep this structure intact whenever changing/moving directories.
    If needed, Assets could be re-downloaded from the web.

3. The following prerequisites are met (pip - python package manager):
    - Install Jinja2 Template engine:
        pip install jinja2

    - Install treelib:
        pip install treelib


Please fill free to contact me via Freelancer.com website for any question/request.
Thanks!
