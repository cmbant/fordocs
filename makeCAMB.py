import fordocs

fordocs.generate_docs(
    [r"c://work/dist/git/camb/fortran"],
    r"z:\testoutfull",
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
