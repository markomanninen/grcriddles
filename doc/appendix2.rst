# Appendix 2 - Riddle solver
============================

Minimum code to solve riddles.

.. code-block:: python

  # read csv file to dataframe
  from functions import csv_file_name
  from pandas import read_csv
  df = read_csv(csv_file_name, header = None)
  df[1] = df[1].apply(lambda x: int(x))
  df[2] = df[2].apply(lambda x: float(x))
  df[3] = df[3].apply(lambda x: int(x))
  df[4] = df[4].apply(lambda x: int(x))
  df[5] = df[5].apply(lambda x: str(x).replace("'", "").replace("[", "").replace("]", "").split(", "))
  df[6] = df[6].apply(lambda x: int(x))
  df[7] = df[7].apply(lambda x: int(x))
  df[8] = df[8].apply(lambda x: int(x))

  # get words with isopsephy of 1697 and length 9
  a = df.copy()
  a = a[a[4] == 1697]
  a = a[a[3] == 9]

  # how many results?
  print("Total records: %s" % len(a))

  # output words ordered alphabetically
  words = a.sort_values(0)
  words = words[[0, 1, 3, 4, 5, 7, 8]]
  words.columns = ['Word', 'Count', 'Letters', 'Isopsephy', 'Syllables', 'Vowels', 'Consonants']
  words.set_index('Word', inplace=True)
  words
