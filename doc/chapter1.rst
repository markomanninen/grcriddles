Processing Greek corpora for the isopsehical riddle solver
==========================================================

.. figure:: delphic_sibyl.png
   :scale: 50 %
   :alt: Delphic Sibyl

   Michelangelo's Delphic Sibyl, Sistine Chapel

This is an interactive Jupyter notebook document used to preprocess ancient Greek corpora for solving some enigmatic alpha numerical riddles in the [Pseudo Sibylline](https://en.wikipedia.org/wiki/Sibylline_Oracles) oracles.

Oracles were composed in 150BC - 400AD and contain hexametric poems written in Ancient Greek. These _oracula_ were circulating and quite famous among the Jewish-Christian community at that time. From the fourteen known individual books twelve has passed to our age. Some of the material in the books contain cryptic riddles, often refering to persons, cities, countries, and Gods names for example. Most of these secretive references are very general, pointing only to the first letter of the subject and its numerical value. Solving them requires a proper knowledge of the context, not only inner textual but historical context.

Most of the riddles have been solved by historians already. Some of the riddles are still problematic and open for better proposals. Some of these open riddles are specific enough so that one may try to solve them programmically.

Programmical approach to solve the riddles requires a Greek text corpora which is what this document is made for. I will download and preprocess available open source Greek corpora, which is a quite dauntful task for many reasons. At the end I'll have a word database containing hundreds of thousands of Greek words that can be further used in the riddle solver.

See the separate notebooks for:

-  the `riddle solver <chapter2.rst>`__ itself in action
-  the analytical `word study <chapter3.rst`>__ of the results

Note that rather than just reading, these chapters can also be run interactively in your local Jupyter notebook installation if you prefer. That means that you may verify the procedure or alter parameters and try solving the riddles with your own parameters.

Collecting Greek Corpora
------------------------

The first things is to get a big raw Ancient Greek text to operate with. [CLTK](https://github.com/cltk/cltk) library provides an importer to the [Perseus](http://www.perseus.tufts.edu/hopper/opensource/download) and the [First1KGreek](http://opengreekandlatin.github.io/First1KGreek/) open source data sources.

I'm using [Abnum](https://github.com/markomanninen/abnum3) library to strip diacritics of the Greek words, remove non-alphabetical characters, as well as calculating the isopsephical value of the words. [Greek_accentuation](https://github.com/jtauber/greek-accentuation) library is used to split words into syllables. This is required because few of the riddles contain specific information about syllables. [Pandas](http://pandas.pydata.org/) library is used as an API to the collected database and [Plotly](https://plot.ly/) library is used for the visual presentation of the statistics.

You can install these libraries by uncommenting the next lines:


.. code-block:: python

	import sys

	#!{sys.executable} -m pip install cltk
	#!{sys.executable} -m pip install abnum
	#!{sys.executable} -m pip install pandas
	#!{sys.executable} -m pip install plotly
	#!{sys.executable} -m pip install greek_accentuation


For your convenience, my environment is the following:


.. code-block:: python

	print("Python %s" % sys.version)


|Output:|

.. code-block:: text

    Python 3.6.1 |Anaconda 4.4.0 (64-bit)| (default, May 11 2017, 13:25:24) [MSC v.1900 64 bit (AMD64)]


Note, that `Python 3.4+` is required for all libraries to work properly.

Listing CLTK corpora
~~~~~~~~~~~~~~~~~~~~

Let's see what corporas are available for download:


.. code-block:: python

	from cltk.corpus.utils.importer import CorpusImporter
	corpus_importer = CorpusImporter('greek')
	', '.join(corpus_importer.list_corpora)


Output:

    'greek_software_tlgu, greek_text_perseus, phi7, tlg, greek_proper_names_cltk, greek_models_cltk, greek_treebank_perseus, greek_lexica_perseus, greek_training_set_sentence_cltk, greek_word2vec_cltk, greek_text_lacus_curtius, greek_text_first1kgreek'


I'm going to use `greek_text_perseus` and `greek_text_first1kgreek` corpora for the study, combine them to a single raw text file and unique words database.

Download corporas
~~~~~~~~~~~~~~~~~

I have collected large part of the used procedures to the [functions](functions.py) script to maintain this notebook document more concise.

The next code snippet will download hundreds of megabytes of Greek text to your local computer for quicker access:


.. code-block:: python

	# import corpora
	for corpus in ["greek_text_perseus", "greek_text_first1kgreek"]:
	    try:
	        corpus_importer.import_corpus(corpus)
	    except Exception as e:
	        print(e)


Next I will copy only suitable greek text files from `greek_text_first1kgreek` to the working directory `greek_text_tlg`. Perseus corpora is pretty good as it is.

Note that one can download and extract `greek_text_first1kgreek` directly from  https://github.com/OpenGreekAndLatin/First1KGreek/zipball/master. It may have the most recent and complete set of files. If you wish to use it, extract package directly to `~\cltk_data\greek\text\greek_text_tlg`.



.. code-block:: python

	from functions import path, joinpaths, copy, dirt

	# copy all suitable greek text files from the source dir to the destination work dir
	if not path.isdir(path.join(dirt, "greek_text_tlg")):
	    src = joinpaths(dirt, ["greek_text_first1kgreek", "data"])
	    dst = joinpaths(dirt, ["greek_text_tlg"])
	    print("Copying %s -> %s" % (src, dst))
	    try:
	        copy(src, dst)
	    except Exception as e:
	        print(e)
	else:
	    print(path.join(dirt, "greek_text_tlg"), "already exists, lets roll on!")


|Output:|

.. code-block:: text

    C:\Users\phtep\cltk_data\greek\text\greek_text_tlg already exists, lets roll on!


Perseus Greek source text is written as a betacode, so I will need a converter script for it. I found a suitable one from: https://github.com/epilanthanomai/hexameter but had to make a small fix to it, so I'm using my own version of the  [betacode](betacode.py) script.

### Process files

Next step is to find out Greek text nodes from the provided XML source files. I have to specify a tag table to find main text lines from the source files so that only Greek texts are processed. XML files have a lot of English and Latin phrases that needs to be stripped out.

Extracted content is saved to the author/work based directories. Simplified uncial conversion is also made at the same time so that the final output file contains only plain words separated by spaces. Pretty much in a format written by the ancient Greeks btw.

Collect text files
~~~~~~~~~~~~~~~~~~

.. code-block:: python

	from functions import init_corpora

	# init corpora list
	corporas = ["greek_text_perseus", "greek_text_tlg"]

	greek_corpora_x = init_corpora(corporas)
	print("%s files found" % len(greek_corpora_x))


|Output:|

.. code-block:: text

    1272 files found


Process text files
~~~~~~~~~~~~~~~~~~

This will take several minutes depending on if you have already run it once and have temporary directories available:


.. code-block:: python

	from functions import remove, all_greek_text_file, perseus_greek_text_file, first1k_greek_text_file, process_greek_corpora

	# remove old temp files
	try:
	    remove(all_greek_text_file)
	    remove(perseus_greek_text_file)
	    remove(first1k_greek_text_file)
	except OSError:
	    pass

	# collect greek corpora data
	greek_corpora = process_greek_corpora(greek_corpora_x)


File statistics
---------------

When files are downloaded and preprocessed, I can get the size of the text files:


.. code-block:: python

	from functions import get_file_size

	print("Size of the all raw text: %s MB" % get_file_size(all_greek_text_file))
	print("Size of the perseus raw text: %s MB" % get_file_size(perseus_greek_text_file))
	print("Size of the first1k raw text: %s MB" % get_file_size(first1k_greek_text_file))


|Output:|

.. code-block:: text

    Size of the all raw text: 604.88 MB
    Size of the perseus raw text: 79.74 MB
    Size of the first1k raw text: 525.13 MB


I will calculate other statistics of the saved text files for cross checking their content:


.. code-block:: python

	from functions import get_stats

	ccontent1, chars1, lwords1 = get_stats(perseus_greek_text_file)
	ccontent2, chars2, lwords2 = get_stats(first1k_greek_text_file)
	ccontent3, chars3, lwords3 = get_stats(all_greek_text_file)


|Output:|

.. code-block:: text

    Corpora: perseus_greek_text_files.txt
    Letters: 38146511
    Words in total: 7322673
    Unique words: 355348

    Corpora: first1k_greek_text_files.txt
    Letters: 249255721
    Words in total: 52130741
    Unique words: 648873

    Corpora: all_greek_text_files.txt
    Letters: 287402232
    Words in total: 59453414
    Unique words: 826516



Letter statistics
~~~~~~~~~~~~~~~~~

I'm using Pandas library to handle tabular data and show basic letter statistics.



.. code-block:: python

	from functions import Counter, DataFrame


Calculate statistics
~~~~~~~~~~~~~~~~~~~~

This will take some time too:



.. code-block:: python

	# perseus dataframe
	df = DataFrame([[k, v] for k, v in Counter(ccontent1).items()])
	df[2] = df[1].apply(lambda x: round(x*100/chars1, 2))
	a = df.sort_values(1, ascending=False)
	# first1k dataframe
	df = DataFrame([[k, v] for k, v in Counter(ccontent2).items()])
	df[2] = df[1].apply(lambda x: round(x*100/chars2, 2))
	b = df.sort_values(1, ascending=False)
	# perseus + first1k dataframe
	df = DataFrame([[k, v] for k, v in Counter(ccontent3).items()])
	df[2] = df[1].apply(lambda x: round(x*100/chars3, 2))
	c = df.sort_values(1, ascending=False)


Show letter statistics
~~~~~~~~~~~~~~~~~~~~~~

The first column is the letter, the second column is the count of the letter, and the third column is the percentage of the letter contra all letters.

Show tables side by side to save some vertical space:


.. code-block:: python

	from functions import display_side_by_side

	display_side_by_side(Perseus=a, First1K=b, Perseus_First1K=c)


_Perseus_

| Letter | Count | Percent |
| --- | --- | --- |
| 