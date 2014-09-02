# #Example of programmatic usage (for http://cosmologist.info/cosmomc code)

import fordocs

fordocs.generate_docs([r'c://work/dist/git/cosmomc/source'],
                      r'z:\testoutfull', '*.f90', 'CosmoMC Documentation', 
                      defines=['MPI'],
                      excludes=['sigma8.f90','test*','*Union2*','*SNLS*','lrg*','cmbdata.*','CMBlowL*'])
