Appendix 2 - Solve riddles
==========================

Minimum code to solve isopsephical riddles in the Pseudo-Sibylline oracles.

.. code-block:: bash

  pip install grcriddles

.. code-block:: python

  from grcriddles import get_database
  # get words with length 9, isopsephy 1697, consonants 5,
  # and the first three syllables having 2 letters each
  # syllable count is going to be 4 with above parameters
  words = get_database({0: 'Word', 1: 'Count', 3: 'Chars', 4: 'Isopsephy', 5: 'Syllables', 7: 'Vowels', 8: 'Mutes'})
  a = words[words['Isopsephy'] == 1697]
  a = a[a['Chars'] == 9]
  a = a[a['Mutes'] == 5]
  a = a[a.apply(lambda x: len(x['Syllables'][0]) == 2 and \
                          len(x['Syllables'][1]) == 2 and \
                          len(x['Syllables'][2]) == 2, axis=1)]
  # output words ordered alphabetically
  a.sort_index()

.. code-block:: text

             Count    Chars  Isopsephy          Syllables  Vowels       Mutes
  Word
  ΑΜΦΕΚΑΛΥΨ      1        9       1697  [ΑΜ, ΦΕ, ΚΑ, ΛΥΨ]       4           5
  ΛΗΛΥΘΟΤΩΝ      1        9       1697  [ΛΗ, ΛΥ, ΘΟ, ΤΩΝ]       4           5
  ΜΕΤΑΝΑΣΤΩ      1        9       1697  [ΜΕ, ΤΑ, ΝΑ, ΣΤΩ]       4           5
  ΣΥΝΩΚΙΣΘΗ     13        9       1697  [ΣΥ, ΝΩ, ΚΙ, ΣΘΗ]       4           5

.. code-block:: python

  # get words containing ΑΜΦΕΚΑΛΥ stem word
  b = words.filter(like="ΑΜΦΕΚΑΛΥ", axis=0)
  b.sort_index()

.. code-block:: text

                Count  Chars  Isopsephy               Syllables  Vowels  Mutes
  Word
  ΑΜΦΕΚΑΛΥΠΤΕ       3     11       1382   [ΑΜ, ΦΕ, ΚΑ, ΛΥ, ΠΤΕ]       5      6
  ΑΜΦΕΚΑΛΥΠΤΟΝ      2     12       1497  [ΑΜ, ΦΕ, ΚΑ, ΛΥ, ΠΤΟΝ]       5      7
  ΑΜΦΕΚΑΛΥΦΘΗ       2     11       1514   [ΑΜ, ΦΕ, ΚΑ, ΛΥ, ΦΘΗ]       5      6
  ΑΜΦΕΚΑΛΥΨ         1      9       1697       [ΑΜ, ΦΕ, ΚΑ, ΛΥΨ]       4      5
  ΑΜΦΕΚΑΛΥΨΑΝ       2     11       1748   [ΑΜ, ΦΕ, ΚΑ, ΛΥ, ΨΑΝ]       5      6
  ΑΜΦΕΚΑΛΥΨΕ       18     10       1702    [ΑΜ, ΦΕ, ΚΑ, ΛΥ, ΨΕ]       5      5
  ΑΜΦΕΚΑΛΥΨΕΝ      20     11       1752   [ΑΜ, ΦΕ, ΚΑ, ΛΥ, ΨΕΝ]       5      6
