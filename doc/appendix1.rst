Appendix 1 - Process corpora
============================

Minimum code to create a unique word database for the riddle solver. Download,
preprocess, and store Greek corpora.

.. code-block:: python

  # import download and preprocess function
  from grcriddles import download_and_preprocess_corpora, save_database, get_database
  # call function to create Greek file directories and retrieve corpora data
  greek_corpora = download_and_preprocess_corpora()
  # save word database
  save_database(greek_corpora)
  # retrieve word database
  df = get_database()
  # how many records there are in the database?
  print("Total records: %s" % len(df))
