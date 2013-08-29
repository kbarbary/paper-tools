paper-tools
===========

Scripts for preparing manuscripts for astronomical journals.

* `shorten.py`: Shorten author list in `.bbl` file and save modified file
  to `{filename}.short`. Usage:

      shorten.py [-n NUMBER] FILENAME

  where `NUMBER` is the maximum number of authors to allow before the author
  list is shortened to First Author, et al. Default is 8.

* `submission_prep.py`: Prepare files for submission to ApJ or arXiv. Usage:

      submission_prep.py [-a] FILENAME OUTDIR

  See script for more details. `-a` prepares for submission to arXiv rather
  than ApJ.
