# Appendix 2 - Riddle solver
============================

Minimum code to solve isopsephical riddles in the Pseudo-Sibylline oracles. This
requires `functions.py` script and `greek_words_corpora.csv` file reside in the
same directory.

.. code-block:: python

  # read csv file to dataframe
  from functions import csv_file_name, read_csv
  df = read_csv(csv_file_name, header = None)
  df[1] = df[1].apply(lambda x: int(x))
  df[2] = df[2].apply(lambda x: float(x))
  df[3] = df[3].apply(lambda x: int(x))
  df[4] = df[4].apply(lambda x: int(x))
  df[5] = df[5].apply(lambda x: str(x).replace("'", "").replace("[", "").replace("]", "").split(", "))
  df[6] = df[6].apply(lambda x: int(x))
  df[7] = df[7].apply(lambda x: int(x))
  df[8] = df[8].apply(lambda x: int(x))

  # get words with length 9, isopsephy 1697, syllable count 4, consonants 5,
  # and the first three syllables having 2 letters each
  a = df.copy()
  a = a[a[4] == 1697]
  a = a[a[3] == 9]
  a = a[a[6] == 4]
  a = a[a[8] == 5]
  a = a[a.apply(lambda x: len(x[5][0]) == 2 and len(x[5][1]) == 2 and len(x[5][2]) == 2, axis=1)]

  # output words ordered alphabetically
  words = a.sort_values(0)
  words = words[[0, 1, 3, 4, 5, 7, 8]]
  words.columns = ['Word', 'Count', 'Letters', 'Isopsephy', 'Syllables', 'Vowels', 'Consonants']
  words.set_index('Word', inplace=True)
  words

  # search exact match(es) for the word
  from functions import search_words_from_corpora, perseus_dir, first1k_dir
  search_words_from_corpora(["ΑΜΦΕΚΑΛΥΨ"], [perseus_dir, first1k_dir], None, True)

  # search partial match(es) for the word
  search_words_from_corpora(["ΑΜΦΕΚΑΛΥΨ"], [perseus_dir, first1k_dir], None, False)
