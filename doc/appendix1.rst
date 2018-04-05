Appendix 1 - Store database
===========================

Minimum code to create a unique word database for the riddle solver. Download,
preprocess, and store Greek corpora, then save and retrieve word database as
a `DataFrame` object.

.. code-block:: bash

  pip install grcriddles

.. code-block:: python

  # import download and preprocess function
  from grcriddles import download_and_preprocess_corpora, save_database
  # call function to create Greek file directories and retrieve corpora data
  greek_corpora = download_and_preprocess_corpora()
  # save and retrieve word database
  df = save_database(greek_corpora)
  # how many records there are in the database?
  print("Total records: %s" % len(df))

Output:

.. code-block:: text

  Total records: 1708
