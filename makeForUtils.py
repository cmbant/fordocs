import fordocs

fordocs.generate_docs(
    [r"c://work/dist/git/CAMB/forutils"],
    r"./doc_out_forutils",
    "*.f90",
    "ForUtils Documentation",
    excludes=["*_tests.f90"],
    class_tree_splits=[],
    github_root="https://github.com/cmbant/forutils",
)
