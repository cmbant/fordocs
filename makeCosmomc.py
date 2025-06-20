# Example of programmatic usage (for http://cosmologist.info/cosmomc code)

import fordocs

fordocs.generate_docs(
    [r"c://work/dist/git/cosmomc/source"],
    r"./doc_out_cosmomc",
    "*.f90",
    "CosmoMC Documentation",
    defines=["MPI"],
    excludes=[
        "sigma8.f90",
        "test*",
        "*_test*",
        "*Union2*",
        "*SNLS*",
        "lrg*",
        "cmbdata.*",
        "CMBlowL*",
    ],
    class_tree_splits=[
        "TSaveLoadStateObject",
        "TConfigClass",
        "TParameterization",
        "TDataLikelihood",
        "TLikelihoodUser",
        "TObjectList",
    ],
    github_root="https://github.com/cmbant/cosmomc",
)
