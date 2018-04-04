# GRCRiddles

Study of alpha-numeric riddles of ancient Greeks

´´´bash
pip install grcriddles
´´´

´´´python
  # import database getter
  from grcriddles.functions import get_database
  a = get_database()
  # filter words with 1697 isopsephy value
  a = a[a[4] == 1697]
  # sort and print word info
  words = a.sort_values(0)
  words = words[[0, 1, 3, 4, 5, 7, 8]]
  words.columns = ['Word', 'Count', 'Letters', 'Isopsephy', 'Syllables', 'Vowels', 'Consonants']
  words.set_index('Word', inplace=True)
  words
´´´

´´´txt

´´´

Developer documentation: http://grcriddles.readthedocs.io/en/latest/

Greek Alpha-Numeric Riddle Solver EBook: https://www.gitbook.com/book/markomanninen/isopsephical-riddles-pseudo-sibylline-oracles/details
