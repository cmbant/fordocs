import fordocs

# usage example for camb as script

fordocs.generate_docs(
    [r"c://work/dist/git/camb/fortran"],
    r"./doc_out_camb",
    "*.f90",
    "Fortran CAMB Documentation",
    excludes=[
        "sigma8.f90",
        "second_PT*",
        "tester*",
        "Inspector*",
        "forutils*",
        "cosmorec*",
        "hyrec*",
        "writefits*",
    ],
    class_tree_splits=["TCambComponent"],
)
