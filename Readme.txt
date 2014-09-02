Usage
=====

1- Install the requirements from the included requirements.txt:
  pip install -r requirements.txt

2- Use main.py like:

  main.py -s <source_folder> -d <destination_folder> [-t <documentation_title>] [--define <one or more compiler flags>]

  Only the first time these arguments are required. If these arguments are omitted afterwards, they
  are re-read from last_args.txt (created automatically)