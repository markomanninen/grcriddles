#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: functions.py
# License: MIT
# Copyright: (c) 2018 Marko Manninen
# Module requirements: greek_accentuation, abnum, requests, pathlib, pandas, tqdm, IPython
import re
import shutil, errno, pkg_resources
from xml.dom import minidom
from collections import Counter
from abnum import Abnum, greek
from romanize3 import grc
from pandas import DataFrame, read_csv
from os import path, listdir, makedirs
from os import remove as rm
from pathlib import Path # python 3.4+ version
from greek_accentuation.syllabify import syllabify
from IPython.display import display_html, HTML
from requests import get as rget
from zipfile import ZipFile
from tqdm import tqdm

###################
# DEFINE VARIABLES
##################

# file to collect all stripped greek text
all_greek_text_file = "all_greek_text_files.txt"
# file to collect all perseus greek text
perseus_greek_text_file = "perseus_greek_text_files.txt"
# file to collect all first 1k greek text
first1k_greek_text_file = "first1k_greek_text_files.txt"
# unique greek words database
csv_file_name = "greek_words_corpora.csv"
# zip download files
perseus_zip_file = "perseus.zip"
perseus_zip_dir = 'greek_text_perseus_zip'
perseus_tmp_dir = 'greek_text_perseus_tmp'
perseus_dir = 'greek_text_perseus'

first1k_zip_file = "first1k.zip"
first1k_zip_dir = 'greek_text_first1k_zip'
first1k_tmp_dir = 'greek_text_first1k_tmp'
first1k_dir = 'greek_text_first1k'

# ϒ not needed?
vowels = "ΩΗΥΕΙΟΑ"

# main database entry point
database = None

###################
# DEFINE FUNCTIONS
###################

# silently bypass exception if file does not exist
def remove(f):
    try:
        rm(f)
    except:
        pass

# download file with output progress bar indicator
# nice utility for big files that takes time to transfer
def download_with_indicator(fs, fd, rl = False):
    if rl or (not rl and not path.isfile(fd)):
        try:
            req = rget(fs, stream = True)
            total_size, block_size = int(req.headers.get('content-length', 0)), 1024
            print("Downloading: %s" % fs)
            with open(fd, 'wb') as f:
                params = {'total': total_size / (32.0 * block_size), 'unit': 'B', 'unit_scale': True, 'unit_divisor': block_size}
                # way 1 of doing indicator
                #for data in tqdm(req.iter_content(32 * block_size), **params):
                #    f.write(data)
                # way 2 of doing indicator
                with tqdm(**params) as g:
                    for data in req.iter_content(32 * block_size):
                        f.write(data)
                        g.update(len(data))
        except Exception as e:
            print(e)

# extract packed file to desctination dir
def unzip(fs, fd):
    if not path.isdir(fd) and path.isfile(fs):
        zip_ref = ZipFile(fs, 'r')
        zip_ref.extractall(fd)
        zip_ref.close()

# get only greek letters from the source text
def extract_greek(s):
    # words are separated by spaces but all other whitespace is removed
    s = grc.filter(s)
    t = ' '.join(filter(lambda x: len(x), s.split()))
    return t, grc.deaccent(s).upper().replace("ϒ", "Υ").replace("Ϲ", "Σ")

# file path utility for win/mac/lin
def joinpaths(d, paths):
    for p in paths:
        d = path.join(d, p)
    return d

# append (a) or rewrite (w) a file
def to_file(file, string, mode = 'a'):
    with open(file, mode, encoding="utf-8", newline='\n') as f:
        f.write(string)

# helper function to get file size
def get_file_size(f):
    file = Path() / f
    size = file.stat().st_size
    return round(size/1024/1024, 2)

# copy files utility
def copy(src, dst):
    try:
        # ignore files containing these patterns
        ignore = shutil.ignore_patterns('*.csv*',  '*lat*.xml', '*cop*.xml', '*ara*.xml', '*mul*.xml', \
                                        '*eng*.xml', '__cts__.xml', '*.json', '*fre*.xml', '*ger*.xml', \
                                        '*english.xml', '*higg.xml', '.directory')
        shutil.copytree(src, dst, ignore=ignore)
    except OSError as e:
        # error was caused because the source wasn't a directory
        if e.errno == errno.ENOTDIR:
            # copy the file
            shutil.copy(src, dst)
        else:
            print('Directory not copied. Error: %s' % e)

# copy files to new location
def copy_corpora(src, dst):
    # copy all suitable greek text files from the source dir to the destination work dir
    if not path.isdir(dst):
        print("Copying %s -> %s" % (src, dst))
        try:
            copy(src, dst)
        except Exception as e:
            print(e)
    else:
        print(dst, "already exists. Either remove it and run again, or just use the old one.")

# read file and return content
def get_content(fl):
    with open(fl, 'r', encoding="utf-8") as f:
        return f.read().replace("\n", " ")

# return list of available greek files
def init_corpora(corpora):
    result = []
    for d, corpus in corpora:
        files = []
        # get only sub directories
        for a in filter(lambda x: path.isdir(path.join(d, x)), listdir(d)):
            aa = path.join(d, a)
            # get only sub directories
            for b in filter(lambda x: path.isdir(joinpaths(d, [a, x])), listdir(aa)):
                bb = path.join(aa, b)
                # get only files and construct paths to them
                files.extend(map(lambda x: path.join(bb, x),
                                 filter(lambda x: path.isfile(path.join(bb, x)), listdir(bb))))
        # prepare corpora data by adding keys for corpus, unique words,
        # length, file, content and simplified data
        for f in files:
            if 'grc' not in f:
                print("Unidentified language tag found from the file.")
                print("Please check and possibly add to the ignore list: %s" % f)
            result.append({"corpus": corpus, "uwords": {}, "length": 0,
                           "file": f, "content": [], "simplified": ""})
    return result

def get_title_and_author(xmldoc, corpus):
    # parse title and author for storing temp files
    desc = xmldoc.getElementsByTagName('fileDesc')[0]
    title = desc.getElementsByTagName('title')[0].toxml().strip().replace("\n", " ")
    # remove tags
    title = re.sub('<[^<]+?>', '', title)
    title = title.replace("Greek", "").replace("(", "").replace(")", "")
    title = title.replace("?", "").replace("[", "").replace("]", "")
    title = title.replace(".", "").replace(",", "")
    title = ''.join(filter(lambda x: x.strip() != "", map(lambda x: x.title(), title.split())))
    author = ""
    try:
        author = desc.getElementsByTagName('author')[0].toxml().strip().replace("\n", " ")
        # remove tags
        author = re.sub('<[^<]+?>', '', author)
        author = author.replace("&gt;", "").replace(">", "")
        author = author.replace(".", "").replace(",", "")
        author = author.replace("(", "").replace(")", "")
        author = ''.join(filter(lambda x: x.strip() != "", map(lambda x: x.title(), author.split())))
    except Exception as e:
        pass
    # default author name in case it could not have been parsed
    if not author:
        author = "Unnamed"
    return author, title.replace("MachineReadableText", "")

def process_greek_corpora(greek_corpora):
    # remove old temp files
    remove(all_greek_text_file)
    remove(perseus_greek_text_file)
    remove(first1k_greek_text_file)
    # collect corpora data to result
    result = []
    # show indicator of the process
    for corpus in tqdm(greek_corpora):
        corp, f = corpus["corpus"], corpus["file"]
        try:
            s = get_content(f)
            xmldoc = minidom.parseString(s)
        except Exception as e:
            #print("Could not parse document.", e, corp, f)
            continue
        # get author and title
        author, title = get_title_and_author(xmldoc, corp)
        direct = path.join(corp, author)
        # create author based directory
        if not path.exists(direct):
            makedirs(direct)
        # init author and work based file paths
        f1 = title + ".txt"
        #f1 = path.join(direct, f0)
        f2 = path.join(direct, "Simplified_" + f1)
        f3 = path.join(direct, "Search_" + f1)
        f4 = path.join(direct, "Path_" + f1)

        try:
            # is file already processed?
            with open(f2, 'r', encoding="utf-8") as _:
                corpus['simplified'] = _.read()
        except:
            # for greek text tlg this is pretty simple because all the text we are interested is in greek letters
            # so we can dismiss all other characters and just keep the greek one
            content, content_search = extract_greek(s)
            # transform all diacritics to simple uppercase Greek letters
            corpus['simplified'] = grc.deaccent(content).upper()

            if not corpus['simplified']:
                #print("no data", corp, corpus['file'])
                continue
            # unify two different camelcase upsilons
            # unify also medial, final and lunate sigmas
            corpus['simplified'] = corpus['simplified'].replace("ϒ", "Υ").replace("Ϲ", "Σ")
            # store original stripped text
            #to_file(f1, content, 'w')
            # store preprocessed/unaccented, unified, uppercased and simplified text
            to_file(f2, corpus['simplified'], 'w')
            # store original stripped text
            to_file(f3, content_search, 'w')
            # store original file path
            to_file(f4, f, 'w')

        # append to different text files for statistical purposes
        to_file(all_greek_text_file, corpus['simplified'] + "\n")
        if corp == "greek_text_perseus":
            to_file(perseus_greek_text_file, corpus['simplified'] + "\n")
        else:
            to_file(first1k_greek_text_file, corpus['simplified'] + "\n")

        corpus['uwords'] = Counter(corpus['simplified'].split())
        corpus['length'] = len(corpus['simplified'].replace(" ", ""))

        if corpus['length'] < 100:
            #print("Minimum length not meet on the document", f, corpus['length'])
            continue
        else:
            corpus['lperw'] = corpus['length'] / len(corpus['uwords'])

        if 'content' in corpus:
            del corpus['content']
        result.append(corpus)
    return result

# calculate, print and return words stats
def get_stats(fl):
    content = get_content(fl)
    # remove space chars to get pure raw greek character string of the file
    ccontent = content.replace(" ", "")
    chars = len(ccontent)
    # split by space char to get words
    words = content.split()
    lwords = len(words)
    # unique words
    uwords = set(words)
    luwords = len(uwords)
    # output info
    print("Corpora: %s" % fl)
    print("Letters: %s" % str(chars))
    print("Words in total: %s" % str(lwords))
    print("Unique words: %s" % str(luwords))
    print() # newline
    return ccontent, chars, lwords

def download_and_preprocess_corpora():
    # download greek corpora
    print("Downloading Greek corpora...")
    fs = "https://github.com/PerseusDL/canonical-greekLit/archive/master.zip"
    download_with_indicator(fs, perseus_zip_file)
    fs = "https://github.com/OpenGreekAndLatin/First1KGreek/archive/master.zip"
    download_with_indicator(fs, first1k_zip_file)
    # extract zip files
    print("Extracting zip files...")
    unzip(perseus_zip_file, perseus_zip_dir)
    unzip(first1k_zip_file, first1k_zip_dir)
    # copy greek text files from repository
    print("Copying Greek text files from repository...")
    for item in [[joinpaths(perseus_zip_dir, ["canonical-greekLit-master", "data"]), perseus_tmp_dir],
                 [joinpaths(first1k_zip_dir, ["First1KGreek-master", "data"]), first1k_tmp_dir]]:
        copy_corpora(*item)
    # init files
    print("Initializing corpora...")
    greek_corpora_x = init_corpora([[perseus_tmp_dir, perseus_dir], [first1k_tmp_dir, first1k_dir]])
    # process files
    print("Processing files...")
    return process_greek_corpora(greek_corpora_x)

# save words database
def save_database(greek_corpora):
    # get statistics
    lwords = len(get_content(all_greek_text_file).split())
    # greek abnum object for calculating isopsephical value of the words
    gvalue = Abnum(greek).value
    # count unique words statistic from the parsed greek corpora
    # rather than the plain text file. it would be pretty hefty work to find
    # out occurence of the all over 800000 unique words from the text file that
    # is over 300 MB big!
    unique_word_stats = {}
    for item in greek_corpora:
        for word, cnt in item['uwords'].items():
            if word not in unique_word_stats:
                unique_word_stats[word] = 0
            unique_word_stats[word] += cnt
    # init dataframe
    df = DataFrame([[k, v] for k, v in unique_word_stats.items()])
    # add column for the occurrence percentage of the word
    # lwords3 variable is the length of the all words list
    df[2] = df[1].apply(lambda x: round(x*100/lwords, 2))
    # add column for the length of the individual word
    df[3] = df[0].apply(lambda x: len(x))
    # add isopsephical value column
    df[4] = df[0].apply(lambda x: gvalue(x))
    # add syllabified word column
    df[5] = df[0].apply(lambda x: syllabify(x))
    # add length of the syllables in word column
    df[6] = df[5].apply(lambda x: len(x))
    # count vowels in the word as a column
    df[7] = df[0].apply(lambda x: sum(list(x.count(c) for c in vowels)))
    # count consonants in the word as a column
    df[8] = df[0].apply(lambda x: len(x)-sum(list(x.count(c) for c in vowels)))
    # save dataframe to CSV file
    df.to_csv(csv_file_name, header=False, index=False, encoding='utf-8')
    # set global database variable
    database = df
    return get_database()

# get word database
def get_database(cols = None):
    global database
    if  database == None:
        # try to read from the current directory
        if path.exists(csv_file_name):
        	df = read_csv(csv_file_name, header = None)
        else:
            # fallback to package root directory
            df = read_csv(pkg_resources.resource_filename('grcriddles', csv_file_name), header = None)
        df[1] = df[1].apply(lambda x: int(x))
        df[2] = df[2].apply(lambda x: float(x))
        df[3] = df[3].apply(lambda x: int(x))
        df[4] = df[4].apply(lambda x: int(x))
        df[5] = df[5].apply(lambda x: str(x).replace("'", "").replace("[", "").replace("]", "").split(", "))
        df[6] = df[6].apply(lambda x: int(x))
        df[7] = df[7].apply(lambda x: int(x))
        df[8] = df[8].apply(lambda x: int(x))
        database = df
    # rename columns and set index
    if cols:
        words = database.copy()
        words = words[list(cols.keys())]
        words.columns = list(cols.values())
        if 0 in cols:
            words.set_index(cols[0], inplace=True)
            return words.sort_index()
        return words
    else:
        return database.copy()

# display tables side by side, jupyter notebook helper
def display_side_by_side(**kwargs):
    html = ''
    for caption, df in kwargs.items():
        df.columns = ['Letter', 'Count', 'Percent']
        html += df.to_html(index=False)\
                  .replace("<thead>", "<caption style='text-align:center'>%s</caption><thead>" % caption)
    display_html(html.replace('table', 'table style="display:inline"'), raw=True)

# find the string (s) from the search source text (t) and match with the original source text (u)
# search and original source texts should have same character indices for keywords
# based on that assumption the location of the matches +- threshold (l)
# is calculated and substring is returned with the original start and end location of the matches
def find_original(s, t, u, l = 100, e = False):
    # length of the original text
    ll = len(t)
    # get exact match or partial match points
    rc = re.compile(" %s |^%s | %s$|^%s$" % (s, s, s, s)) if e else re.compile(s)
    fi = re.finditer(rc, t)
    # calculate the start and end points
    return list((u[m.start() - l if m.start() > l else 0 : \
                   m.end() + l if m.end() + l < ll else -1], \
                 m.start(), m.end()) for m in fi)

# search words from the source text
def search_words(source, words, exact = False):
    result = {}
    # partial match or exact match
    source = source.split() if exact else source
    for word in words:
        if word in source:
            result[word] = source.count(word)
    return result

# helper function for search_words_from_corpora
def print_if_match(f, words, maxwords = None, exact = False, extract = 100):
    content = get_content(f)
    result = search_words(content, words, exact)
    if result:
        g = f.replace("Search_", "Path_")
        try:
            path = get_content(g)
            pathx = path.split('\\')[-1]
            pathx = " (%s)" % pathx[:100].strip()
        except Exception as e:
            pathx = ""
        xcontent, chunks = get_content(path), ""
        for k, v in result.items():
            # author.text (hits)
            chunks += '\r\n\r\n   ----- %s (%s) -----\r\n' % (k, v)
            chunks += '\r\n'.join(list("   " + ' '.join(filter(lambda x: len(x), grc.filter(match[0]).strip().split())) \
                                       for match in find_original(k, content, xcontent, extract, exact)[:maxwords]))
        c = ', '.join(f.replace("Search_", "").replace(".txt", "").split('\\')[1:])
        print(" + %s%s =>    %s\r\n" % (c, pathx, chunks))

# search words in a given list from the original corpora
# optional: define maximum results (default is one, 'None' if all should be returned)
# optional: define exact match of the word or partial match. the latter is default
# optional: define how many characters extract before and after the match. default is 100
def search_words_from_corpora(words, corpora, maximum = 1, exact = False, extract = 100):
    # iterate all corpora and see if selected words occur in the text
    for corp in corpora:
        # author directories in corpora
        for b in filter(path.isdir, map(lambda x: path.join(corp, x), listdir(corp))):
            # author text files
            for c in filter(lambda x: path.isfile(x) and x.find("Search_") > 0, map(lambda x: path.join(b, x), listdir(b))):
                print_if_match(c, words, maximum, exact, extract)
