# GRCRiddles

Study of alpha-numeric riddles of ancient Greeks

´´´bash
pip install grcriddles
´´´

´´´python
  # import database getter
  from grcriddles.functions import get_database
  a = get_database()
  # filter words
  a = a[a[0].str.contains("ΑΜΦΕΚΑΛΥ")]
  # sort and print word info
  words = a.sort_values(0)
  words = words[[0, 1, 3, 4, 5, 7, 8]]
  words.columns = ['Word', 'Count', 'Chars', 'Isopsephy', 'Syllables', 'Vowels', 'Mutes']
  words.set_index('Word', inplace=True)
  words
´´´

´´´txt
              Count  Chars  Isopsephy               Syllables  Vowels  Mutes
Word
ΑΜΦΕΚΑΛΥΠΤΕ       3     11       1382   [ΑΜ, ΦΕ, ΚΑ, ΛΥ, ΠΤΕ]       5      6
ΑΜΦΕΚΑΛΥΠΤΟΝ      2     12       1497  [ΑΜ, ΦΕ, ΚΑ, ΛΥ, ΠΤΟΝ]       5      7
ΑΜΦΕΚΑΛΥΦΘΗ       2     11       1514   [ΑΜ, ΦΕ, ΚΑ, ΛΥ, ΦΘΗ]       5      6
ΑΜΦΕΚΑΛΥΨ         1      9       1697       [ΑΜ, ΦΕ, ΚΑ, ΛΥΨ]       4      5
ΑΜΦΕΚΑΛΥΨΑΝ       2     11       1748   [ΑΜ, ΦΕ, ΚΑ, ΛΥ, ΨΑΝ]       5      6
ΑΜΦΕΚΑΛΥΨΕ       18     10       1702    [ΑΜ, ΦΕ, ΚΑ, ΛΥ, ΨΕ]       5      5
ΑΜΦΕΚΑΛΥΨΕΝ      20     11       1752   [ΑΜ, ΦΕ, ΚΑ, ΛΥ, ΨΕΝ]       5      6
´´´

Developer documentation: http://grcriddles.readthedocs.io/en/latest/

Greek Alpha-Numeric Riddle Solver EBook: https://www.gitbook.com/book/markomanninen/isopsephical-riddles-pseudo-sibylline-oracles/details
