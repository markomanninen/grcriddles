Appendix 3 - Search results
===========================

.. code-block:: python

  # search exact match(es) for the word from both perseus and first1k corpora
  from functions import search_words_from_corpora, perseus_dir, first1k_dir
  search_words_from_corpora(["ΑΜΦΕΚΑΛΥΨ"], [perseus_dir, first1k_dir], None, True)

  # search partial match(es) for the word from both perseus and first1k corpora
  search_words_from_corpora(["ΑΜΦΕΚΑΛΥΨ"], [perseus_dir, first1k_dir], None, False)
