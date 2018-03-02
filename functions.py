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

# file path utility for win/mac/lin
def joinpaths(d, paths):
    for p in paths:
        d = path.join(d, p)
    return d

# append (a) or rewrite (w) a file
def append_to_file(file, string, mode = 'a'):
    with open(file, mode, encoding="utf-8", newline='\n') as f:
        f.write(string)

# home dir
home = path.expanduser("~")

# filter dirs and files to get all greek authors
# directory: by default corpora is downloaded to the user root under cltk_data
dirt = joinpaths(home, ["cltk_data", "greek", "text"])

# greek abnum object for preprocess and isopsephical value getter
g = Abnum(greek)

# download greek betacode decoder script
file_bc = 'betacode.py'
if not path.isfile(file_bc):
    from urllib.request import urlopen
    response = urlopen('https://raw.githubusercontent.com/markomanninen/grcriddles/master/betacode.py')
    append_to_file(file_bc, response.read().decode("utf-8"), 'w')

# import betacode to unicode function
from betacode import betacode_to_unicode

# file to collect all stripped greek text
all_greek_text_file = "all_greek_text_files.txt"
# file to collect all perseus greek text
perseus_greek_text_file = "perseus_greek_text_files.txt"
# file to collect all first 1k greek text
first1k_greek_text_file = "first1k_greek_text_files.txt"
# unique greek words database
csv_file_name = "greek_words_corpora.csv"

# copy files utility
def copy(src, dest):
    try:
        ignore = shutil.ignore_patterns('*.csv*', '*lat.xml', '*lat1.xml', '*cop1.xml', \
		                                '*eng1.xml', '__cts__.xml', '*.json', '*_eng*', \
										'*_lat*', '*_cop*', '*english.xml', '*higg.xml')
        shutil.copytree(src, dest, ignore=ignore)
    except OSError as e:
        # error was caused because the source wasn't a directory
        if e.errno == errno.ENOTDIR:
            shutil.copy(src, dest)
        else:
            print('Directory not copied. Error: %s' % e)

# read file and return content
def get_content(fl):
    with open(fl, 'r', encoding="utf-8") as f:
        return f.read().replace("\n", " ")

# remove tags from the content
def remove_tags(x, corpus):
    x = re.sub('<[^<]+?>', '', x)
    if corpus == "greek_text_prs":
        # with perseus data decode betacode to unicode
        x = betacode_to_unicode(x)
    return x

# remove all sub tags and their content. usually they are footnotes or other metadata
def soupit(txt, tag):
    soup = BeautifulSoup(txt, "lxml")
    root = getattr(soup, tag)
    return " ".join(filter(lambda x: len(x), list(c.strip() for c in root.children if "<" not in str(c))))

# parse greek text line for corpora
def line_for_corpora(node, tag, corpus):
    try:
        line = node.toxml().strip()
        if line:
            line = soupit(line, tag)
            if corpus == "greek_text_prs":
                line = betacode_to_unicode(line)
            line = " ".join(filter(lambda x: x.strip() != "", line.split()))
            if line:
                return line.strip()
    except Exception as e:
        #print(e)
        pass
    return ''

# tags used to retrieve lines from xml file
tags = {
    # perseus
    "Aeschines": ["div1", ["head", "p"]],
    "Aeschylus": ["div1", ["speaker", "l"]],
    "Andocides": ["div1", ["head", "p"]],
    "Anth": ["div1", ["label", "p"]],
    "Apollodorus": ["div1", ["p"]],
    "Apollonius": ["div1", ["l"]],
    "Appian": ["p", []],
    "Aratus": ["div1", ["p"]],
    "Aretaeus": ["p", ["foreign"]],
    "Aristides": ["body", ["head", "p"]],
    "Aristophanes": ["div1", ["speaker", "l"]],
    "Aristotle": ["p", []],
    "Arrian": ["body", ["p"]],
    "Athenaeus": ["body", ["p"]],
    "Bacchylides": ["div2", ["persName", "l"]],
    "Bible": ["div1", ["head", "p"]],
    "Callimachus": ["div1", ["head", "p"]],
    "Colluthus": ["body", ["p"]],
    "Demades": ["p", []],
    "Demosthenes": ["p", []],
    "Diodorus": ["p", []],
    "Diogenes": ["div1", ["head", "p"]],
    "Dionysius": ["div1", ["opener", "p"]],
    "Dinarchus": ["p", []],
    "DioChrys": ["p", []],
    "Epictetus": ["p", []],
    "Euclid": ["p", []],
    "Galen": ["p", []],
    "Herodotus": ["p", []],
    "Hippocrates": ["p", []],
	"Homer": ["body", ["l", "lemma"]],
    "Hyperides": ["p", []],
    "JebbOrators": ["p", ["lemma", "foreign", "l"]],
    "Josephus": ["p", []],
    "Lucian": ["p", []],
    "Lycophron": ["div1", ["p"]],
    "Lycurgus": ["div1", ["head", "p"]],
    "Lysias": ["div1", ["head", "p"]],
    "Oppian": ["div1", ["p"]],
    "Nonnos": ["div1", ["p"]],
    "Plato": ["p", []],
    "Plutarch": ["p", []],
    "Polybius": ["p", []],
    "Sibyl": ["div", ["head", "p"]],
    "Tryphiodorus": ["p", []],
    "Xenophon": ["p", []],
    "Theophrastus": ["p", []],
    # first1k
    "tlg0643\\tlg001": ["div", ["l"]],
    "tlg0068\\tlg001": ["div", ["head", "l"]],
    "tlg0085\\tlg007": ["div", ["head", "p", "l"]],
    "tlg0527\\tlg035": ["div", ["l"]],
    "tlg0084\\tlg001": ["div", ["head", "l"]],
    "tlg0643\\tlg002": ["div", ["l"]],
    "tlg0643\\tlg001": ["div", ["p"]],
    "tlg0011\\tlg003": ["div", ["l"]],
    "tlg0031\\tlg002": ["div", ["w"]],
    "tlg0527\\tlg029": ["div", ["l"]],
    "tlg0527\\tlg031": ["div", ["l"]],
    "tlg0527\\tlg032": ["div", ["l"]],
    "tlg0527\\tlg033": ["div", ["l"]],
    "tlg0527\\tlg034": ["div", ["l"]],
    "tlg0527\\tlg035": ["div", ["head", "l"]],
    "tlg0085\\tlg001": ["div", ["head", "speaker", "l"]],
    "tlg0011\\tlg003": ["div", ["speaker", "l"]],
    "tlg0643\\tlg001": ["div", ["l"]],
    "tlg0527\\tlg027": ["div", ["head", "l"]],
    "tlg0591\\1st1K001": ["div", ["head", "p"]],
    "tlg0591\\1st1K002": ["div", ["head", "p"]],
    "tlg0593\\1st1K001": ["div", ["head", "p"]],
    "tlg1766\\tlg001": ["div", ["head", "seq"]],
    "tlg1220\\tlg001": ["div", ["head", "l"]],
    "tlg0643\\tlg001": ["div", ["head", "l"]],
    "tlg0069\\tlg001": ["div", ["head", "l"]],
}

# filter only greek xml files
def is_greek_file(x):
    return ("greek_orators" in x or \
            "attic_orators" in x or \
            "grc1.xml" in x or \
            "grc2.xml" in x or \
            "grc3.xml" in x or \
            "_01.xml" in x or "_02.xml" in x or \
            "_03.xml" in x or "_gk.xml" in x) and ".json" not in x

def init_corpora(corporas):
    global dirt
    greek_corpora = []
    for corpus in corporas:
        d = path.join(dirt, corpus)
        files = []
        for a in listdir(d):
            # get only dirs
            if "." not in a:
                # again get only dirs containing xml files
                for b in filter(lambda x: "." not in x and "json" not in x, listdir(path.join(d, a))):
                    # build file paths to greek source files
                    e = joinpaths(d, [a, b])
                    files.extend(map(lambda x: path.join(e, x), filter(lambda x: is_greek_file(x), listdir(e))))
        # prepare corpora data
        for file in files:
            # defaul xml parse path
            if corpus == "greek_text_prs":
                tg = ["l", []]
            else:
                tg = ["div", ["head", "p"]]
            # overwrite with custom parse path if exists
            for key, tag in tags.items():
                if key in file:
                    tg = tag
                    break
            greek_corpora.append({"tag": tg, "corpus": corpus, "uwords": {}, "length": 0,
                                  "file": file, "content": [], "simplified": ""})
    return greek_corpora

# filter out non greek words. there are also some special chars
# in greek text that I will leave out from the processed simplified files
special_chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZÔÊṂḌẠ";

def filter_only_greek_words(x):
    return len(x) and not any(map(lambda y: y in special_chars, x))

def get_title_and_author(xmldoc, corpus):
    # parse title and author for storing temp files
    desc = xmldoc.getElementsByTagName('fileDesc')[0]
    title = desc.getElementsByTagName('title')[0].toxml().strip().replace("\n", " ")
    title = re.sub('<[^<]+?>', '', title)
    title = title.replace("Greek", "").replace("(", "").replace(")", "")
    title = title.replace("?", "").replace("[", "").replace("]", "")
    title = title.replace(".", "").replace(",", "")
    title = ''.join(filter(lambda x: x.strip() != "", map(lambda x: x.title(), title.split())))
    try:
        author = desc.getElementsByTagName('author')[0].toxml().strip().replace("\n", " ")
        author = re.sub('<[^<]+?>', '', author)
        author = author.replace("&gt;", "").replace(">", "")
        author = author.replace(".", "").replace(",", "")
        author = ''.join(filter(lambda x: x.strip() != "", map(lambda x: x.title(), author.split())))
    except Exception as e:
        author = "Unnamed"
    if author == "":
        author = "Unnamed"
    return author, title.replace("MachineReadableText", "")

def process_greek_corpora(greek_corpora):
    #print(greek_corpora)
    r = []
    for corpus in greek_corpora:

        corp = corpus["corpus"]
        f = corpus["file"]

        try:
            s = get_content(f)
            if corp == "greek_text_prs":
                # replace html entities with empty char and replace double empties with single ones
                s = re.sub("&(?:[a-z\d]+|#\d+|#x[a-f\d]+);", " ", s).replace("  ", " ")
            xmldoc = minidom.parseString(s)
        except Exception as e:
            print(e)
            continue
        # get author and title
        author, title = get_title_and_author(xmldoc, corp)
        direct = path.join(corp, author)
        # create author based directory
        if not path.exists(direct):
            makedirs(direct)
        # init author and work based file paths
        f1 = path.join(direct, title + ".txt")
        f2 = path.join(direct, "Simplified_" + title + ".txt")

        try:
            # is file already processed?
            with open(f2, 'r', encoding="utf-8") as _:
                corpus['simplified'] = _.read()
        except:
            #print("process file: " + f.replace(dirt, ""))
            if corpus['tag'][0] == "foreign":
                for item in xmldoc.getElementsByTagName("foreign"):
                    if item.hasAttribute("lang") and item.getAttribute("lang") == "greek":
                        corpus['content'].append(line_for_corpora(item, "foreign", corp))
                    elif item.hasAttribute("xml:lang") and item.getAttribute("xml:lang") == "greek":
                        corpus['content'].append(line_for_corpora(item, "foreign", corp))
            else:
                itemlist = xmldoc.getElementsByTagName(corpus['tag'][0])
                for item in itemlist:
                    if len(corpus['tag'][1]):
                        for tag in corpus['tag'][1]:
                            if tag == "foreign":
                                for item2 in item.getElementsByTagName("foreign"):
                                    if item2.hasAttribute("lang") and item2.getAttribute("lang") == "greek":
                                        corpus['content'].append(line_for_corpora(item2, "foreign", corp))
                                    elif item2.hasAttribute("xml:lang") and item2.getAttribute("xml:lang") == "greek":
                                        corpus['content'].append(line_for_corpora(item2, "foreign", corp))
                            elif tag == "lemma":
                                for item2 in item.getElementsByTagName("lemma"):
                                    if item2.hasAttribute("lang") and item2.getAttribute("lang") == "greek":
                                        corpus['content'].append(line_for_corpora(item2, "lemma", corp))
                                    elif item2.hasAttribute("xml:lang") and item2.getAttribute("xml:lang") == "greek":
                                        corpus['content'].append(line_for_corpora(item2, "lemma", corp))
                            else:
                                for item2 in item.getElementsByTagName(tag):
                                    corpus['content'].append(line_for_corpora(item2, tag, corp))
                    else:
                        corpus['content'].append(line_for_corpora(item, corpus['tag'][0], corp))
            content = ' '.join(corpus['content'])
            #print(content[:20000])
            # there is some comma separated words without spaces that needs to be separated and united again
            content = content.replace(",", ", ").replace(",  ", ", ").replace(".", " . ").replace("  ", " ")
            content = content.replace("·", " · ").replace("  ", " ")
            corpus['simplified'] = ' '.join(filter(filter_only_greek_words, g.preprocess(content).upper().split()))

            if not corpus['simplified']:
                #print("no data", corp, corpus['file'])
                continue
            # unify these two different camelcase upsilons
            # unify also medial, final and lunate sigmas
            corpus['simplified'] = corpus['simplified'].replace("ϒ", "Υ").replace("Ϲ", "Σ")
            # store original stripped text
            append_to_file(f1, content, 'w')
            # store preprocessed, unified, uppercased and simplified text
            append_to_file(f2, corpus['simplified'], 'w')

        # append to different text files for statistical purposes
        append_to_file(all_greek_text_file, corpus['simplified'] + "\n")
        if corp == "greek_text_prs":
            append_to_file(perseus_greek_text_file, corpus['simplified'] + "\n")
        else:
            append_to_file(first1k_greek_text_file, corpus['simplified'] + "\n")

        corpus['uwords'] = Counter(corpus['simplified'].split())
        corpus['length'] = len(corpus['simplified'].replace(" ", ""))

        # log processing
        #print(corpus['file'].replace(dirt, ""), ":", author, ":", title, corpus['length'])

        if corpus['length'] < 100:
            #print("min length", corp, corpus['file'], corpus['length'])
            continue
        else:
            corpus['lperw'] = corpus['length'] / len(corpus['uwords'])

        if 'content' in corpus:
            del corpus['content']
        r.append(corpus)
    return r

# to get file size, python 3.4+ version
from pathlib import Path

def get_file_size(f):
    file = Path() / f
    size = file.stat().st_size
    return round(size/1024/1024, 2)

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
from IPython.display import display_html, HTML

def display_side_by_side(**kwargs):
    html = ''
    for caption, df in kwargs.items():
        df.columns = ['Letter', 'Count', 'Percent']
        html += df.to_html(index=False)\
                  .replace("<thead>", "<caption style='text-align:center'>%s</caption><thead>" % caption)
    display_html(html.replace('table', 'table style="display:inline"'), raw=True)

# loop all extracted text files and find out these:
mixed_content = "" #"ϹḌϘ"
mixed_content += mixed_content.lower()

def has_mixed_content(data):
    a = {}
    for x in mixed_content:
        if x in data:
            a[x] = data.count(x)
    return a

roman_letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

def has_roman_letters(data):
    a = {}
    for x in roman_letters:
        if x in data:
            a[x] = data.count(x)
    return a

vowels = "ϒΩΗΥΕΙΟΑ"

def nvowels(x, n):
    word, tot = x[0], 0
    for c in vowels:
        tot += word.count(c)
        if tot > n:
            return False
    return tot == n
