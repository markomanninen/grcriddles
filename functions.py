#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re
import shutil, errno
from bs4 import BeautifulSoup
from xml.dom import minidom
from collections import Counter
from abnum import Abnum, greek
from pandas import DataFrame
from os import path, listdir, remove, makedirs
from greek_accentuation.syllabify import syllabify
from romanize3 import grc
from pathlib import Path # python 3.4+ version
from IPython.display import display_html, HTML
from zipfile import ZipFile
from tqdm import tqdm
from requests import get as rget

# SET PU VARIABLES

# home dir
home = path.expanduser("~")

# greek abnum object for isopsephical value getter
g = Abnum(greek)

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

roman_letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
roman_letters += "ABCDEFGHIJKLMNOPQRSTUVWXYZ".lower()

# DEFINE FUNCTIONS

# download file with output progress bar indicator
# nice utility for big files that takes time to transfer
def download_with_indicator(fs, fd, rl = False):
    if rl or (not rl and not path.isfile(fd)):
        try:
            req = rget(fs, stream = True)
            total_size = int(req.headers.get('content-length', 0))
            block_size = 1024
            print("Downloading: %s" % fs)
            with open(fd, 'wb') as f:
                params = {'total': total_size / (32.0 * block_size), 'unit': 'B', 'unit_scale': True, 'unit_divisor': block_size}
                for data in tqdm(req.iter_content(32 * block_size), **params):
                    f.write(data)
                #with tqdm(**params) as g:
                #    for data in req.iter_content(32 * block_size):
                #        f.write(data)
                #        g.update(len(data))
        except Exception as e:
            print(e)

# unzip packed file to desctination dir
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
def append_to_file(file, string, mode = 'a'):
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

# remove all sub tags and their content. usually they are footnotes or other metadata
def soupit(txt, tag):
    soup = BeautifulSoup(txt, "lxml")
    root = getattr(soup, tag)
    return " ".join(filter(lambda x: len(x), list(c.strip() for c in root.children if "<" not in str(c))))

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
                print("Unindentified language tag found from the file.")
                print("Please check and possibly add to the ignore list: %s" % f)
            result.append({"corpus": corpus, "uwords": {}, "length": 0,
                           "file": f, "content": [], "simplified": ""})
    return result

def get_title_and_author(xmldoc, corpus):
    # parse title and author for storing temp files
    desc = xmldoc.getElementsByTagName('fileDesc')[0]
    title = desc.getElementsByTagName('title')[0].toxml().strip().replace("\n", " ")
    title = re.sub('<[^<]+?>', '', title)
    title = title.replace("Greek", "").replace("(", "").replace(")", "")
    title = title.replace("?", "").replace("[", "").replace("]", "")
    title = title.replace(".", "").replace(",", "")
    title = ''.join(filter(lambda x: x.strip() != "", map(lambda x: x.title(), title.split())))
    author = ""
    try:
        author = desc.getElementsByTagName('author')[0].toxml().strip().replace("\n", " ")
        author = re.sub('<[^<]+?>', '', author)
        author = author.replace("&gt;", "").replace(">", "")
        author = author.replace(".", "").replace(",", "")
        author = author.replace("(", "").replace(")", "")
        author = ''.join(filter(lambda x: x.strip() != "", map(lambda x: x.title(), author.split())))
    except Exception as e:
        pass
    if not author:
        author = "Unnamed"
    return author, title.replace("MachineReadableText", "")

def process_greek_corpora(greek_corpora):
    result = []
    for corpus in greek_corpora:

        corp = corpus["corpus"]
        f = corpus["file"]

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
            #append_to_file(f1, content, 'w')
            # store preprocessed/unaccented, unified, uppercased and simplified text
            append_to_file(f2, corpus['simplified'], 'w')
            # store original stripped text
            append_to_file(f3, content_search, 'w')
            # store original file path
            append_to_file(f4, f, 'w')

        # append to different text files for statistical purposes
        append_to_file(all_greek_text_file, corpus['simplified'] + "\n")
        if corp == "greek_text_perseus":
            append_to_file(perseus_greek_text_file, corpus['simplified'] + "\n")
        else:
            append_to_file(first1k_greek_text_file, corpus['simplified'] + "\n")

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
    print()
    return ccontent, chars, lwords

# display tables side by side
def display_side_by_side(**kwargs):
    html = ''
    for caption, df in kwargs.items():
        df.columns = ['Letter', 'Count', 'Percent']
        html += df.to_html(index=False)\
                  .replace("<thead>", "<caption style='text-align:center'>%s</caption><thead>" % caption)
    display_html(html.replace('table', 'table style="display:inline"'), raw=True)


def has_roman_letters(data):
    a = {}
    for x in roman_letters:
        if x in data:
            a[x] = data.count(x)
    return a

def nvowels(x, n):
    word, tot = x[0], 0
    for c in vowels:
        tot += word.count(c)
        if tot > n:
            return False
    return tot == n

# find the string (s) from the search source text (t) and match with the original source text (u)
# search and original source texts should have same character indices for keywords
# based on that assumption the location of the matches +- threshold (l)
# is calculated and substring is returned with the original start and end location of the matches
def find_original(s, t, u, l = 100):
    # length of the original text
    ll = len(t)
    # calculate the start and end points
    return list((u[m.start() - l if m.start() > l else 0 : \
                   m.end() + l if m.end() + l < ll else -1], \
                 m.start(), m.end())
                for m in re.finditer(s, t))

# search words from the source text
def search_words(source, words):
    result = {}
    for word in words:
        # partial match is fine here. data should be split to words for exact match
        # but it would take more processing time. for shorter words it might be more useful however
        if word in source:
            result[word] = source.count(word)
    return result

def print_if_match(f, words, maxwords = -1):
    content = get_content(f)
    result = search_words(content, words)
    if result:
        g = f.replace("Search_", "Path_")
        try:
            path = get_content(g)
            pathx = path.split('\\')[-1]
            pathx = " (%s)" % pathx[:100].strip()
        except Exception as e:
            pathx = ""
        xcontent = get_content(path)
        chunks = ""
        i = 1
        for k, v in result.items():
            chunks += '\r\n\r\n   ----- %s (%s) -----\r\n' % (k, v)
            chunks += '\r\n'.join(list("   " + ' '.join(filter(lambda x: len(x), grc.filter(match[0]).strip().split())) for match in find_original(k, content, xcontent)[:maxwords]))
            i += 1
        c = ', '.join(f.replace("Search_", "").replace(".txt", "").split('\\')[1:])
        print(" + %s%s =>    %s\r\n" % (c, pathx, chunks))

def search_words_from_corpora(words, corpora, mx = 1):
    # iterate all corpora and see if selected words occur in the text
    for corp in corpora:
        for b in filter(path.isdir, map(lambda x: path.join(corp, x), listdir(corp))):
            for c in filter(lambda x: path.isfile(x) and x.find("Search_") > 0, map(lambda x: path.join(b, x), listdir(b))):
                print_if_match(c, words, mx)
