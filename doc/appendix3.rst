Appendix 3 - Search results
===========================

Minimum code to search words from the Greek corpora. `download_and_preprocess_corpora`
should be run at least once in the working directory to make search
functionality to work because it will create all necessary Greek text files and
directories from the original `Perseus` and `First1K` repositories.

.. code-block:: bash

  pip install grcriddles

.. code-block:: python

  # import download and preprocess function
  from grcriddles import download_and_preprocess_corpora
  # call function to create Greek file directories for search functionality
  greek_corpora = download_and_preprocess_corpora()

  # search exact match(es) for the word from both perseus and first1k corpora
  from grcriddles import search_words_from_corpora, perseus_dir, first1k_dir
  search_words_from_corpora(["ΑΜΦΕΚΑΛΥΨ"], [perseus_dir, first1k_dir], None, True)

Output:

.. code-block:: text

  ..

.. code-block:: python

  # search partial match(es) for the word from both perseus and first1k corpora
  search_words_from_corpora(["ΑΜΦΕΚΑΛΥΨ"], [perseus_dir, first1k_dir], None, False)

Output:

.. code-block:: text

  ..
