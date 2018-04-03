Appendix 1
==========

.. code-block:: python

	from functions import download_with_indicator, perseus_zip_file, first1k_zip_file
	fs = "https://github.com/PerseusDL/canonical-greekLit/archive/master.zip"
	download_with_indicator(fs, perseus_zip_file)
	fs = "https://github.com/OpenGreekAndLatin/First1KGreek/archive/master.zip"
	download_with_indicator(fs, first1k_zip_file)

	from functions import perseus_zip_dir, first1k_zip_dir, unzip
	unzip(perseus_zip_file, perseus_zip_dir)
	unzip(first1k_zip_file, first1k_zip_dir)

	from functions import copy_corpora, joinpaths, perseus_tmp_dir, first1k_tmp_dir
	for item in [[joinpaths(perseus_zip_dir, ["canonical-greekLit-master", "data"]), perseus_tmp_dir],
				 [joinpaths(first1k_zip_dir, ["First1KGreek-master", "data"]), first1k_tmp_dir]]:
	    copy_corpora(*item)

	from functions import init_corpora, process_greek_corpora
	from functions import perseus_tmp_dir, first1k_tmp_dir, perseus_dir, first1k_dir
	greek_corpora_x = init_corpora([[perseus_tmp_dir, perseus_dir], [first1k_tmp_dir, first1k_dir]])
	greek_corpora = process_greek_corpora(greek_corpora_x)

	from functions import syllabify, Abnum, greek, vowels
	g = Abnum(greek)
	unique_word_stats = {}
	for item in greek_corpora:
		for word, cnt in item['uwords'].items():
			if word not in unique_word_stats:
				unique_word_stats[word] = 0
			unique_word_stats[word] += cnt
	df = DataFrame([[k, v] for k, v in unique_word_stats.items()])
	df[2] = df[1].apply(lambda x: round(x*100/words, 2))
	df[3] = df[0].apply(lambda x: len(x))
	df[4] = df[0].apply(lambda x: g.value(x))
	df[5] = df[0].apply(lambda x: syllabify(x))
	df[6] = df[5].apply(lambda x: len(x))
	df[7] = df[0].apply(lambda x: sum(list(x.count(c) for c in vowels)))
	df[8] = df[0].apply(lambda x: len(x)-sum(list(x.count(c) for c in vowels)))

	print("Total records: %s" % len(df))

	from functions import csv_file_name
	df.to_csv(csv_file_name, header=False, index=False, encoding='utf-8')
