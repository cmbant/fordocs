import fordocs

fordocs.generate_docs(
    [r"c://work/dist/git/forutils"],
    r"z:\forutils",
    "*.f90",
    "ForUtils Documentation",
    excludes=[],
    class_tree_splits=[],
)
