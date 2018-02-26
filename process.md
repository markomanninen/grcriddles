
# Processing Greek corpora for the isopsehical riddle solver

<img src="https://github.com/markomanninen/grcriddles/blob/master/sibylline.png?raw=true" style="width: 65%; border: 1px solid #ddd; padding: 5px" />

This is an interactive Jupyter notebook document used to preprocess ancient Greek corpora for solving some enigmatic alpha numerical riddles in the [Pseudo Sibylline](https://en.wikipedia.org/wiki/Sibylline_Oracles) oracles.

Oracles were composed in 150BC - 400AD and contain hexametric poems written in Ancient Greek. These _oracula_ were circulating and quite famous among the Jewish-Christian community at that time. From the fourteen known individual books twelve has passed to our age. Some of the material in the books contain cryptic riddles, often refering to persons, cities, countries, and Gods names for example. Most of these secretive references are very general, pointing only to the first letter of the subject and its numerical value. Solving them requires a proper knowledge of the context, not only inner textual but historical context.

Most of the riddles have been solved by historians already. Some of the riddles are still problematic and open for better proposals. Some of these open riddles are specific enough so that one may try to solve them programmically.

Programmical approach to solve the riddles requires a Greek text corpora which is what this document is made for. I will download and preprocess available open source Greek corpora, which is a quite dauntful task for many reasons. At the end I'll have a word database containing hundreds of thousands of Greek words that can be further used in the riddle solver.

See the separate notebooks for:

- the [riddle solver](Isopsephical riddles in the Greek Pseudo Sibylline hexameter poetry.ipynb) itself in action 
- the analytical [word study](Study of the results of the isopsephical riddle solver.ipynb) of the results

Note that rather than just reading, these documents can also be run interactively in your local Jupyter notebook installation if you prefer. That means that you may verify the procedure or alter parameters and try solving the riddles with your own parameters.

## Collecting Greek Corpora

The first things is to get a big raw Ancient Greek text to operate with. [CLTK](https://github.com/cltk/cltk) library provides an importer to the [Perseus](http://www.perseus.tufts.edu/hopper/opensource/download) and the [First1KGreek](http://opengreekandlatin.github.io/First1KGreek/) open source data sources.

I'm using [Abnum](https://github.com/markomanninen/abnum3) library to strip diacritics of the Greek words, remove non-alphabetical characters, as well as calculating the isopsephical value of the words. [Greek_accentuation](https://github.com/jtauber/greek-accentuation) library is used to split words into syllables. This is required because few of the riddles contain specific information about syllables. [Pandas](http://pandas.pydata.org/) library is used as an API to the collected database and [Plotly](https://plot.ly/) library is used for the visual presentation of the statistics.

You can install these libraries by uncommenting the next lines:


```python
import sys

#!{sys.executable} -m pip install cltk
#!{sys.executable} -m pip install abnum
#!{sys.executable} -m pip install pandas
#!{sys.executable} -m pip install plotly
#!{sys.executable} -m pip install greek_accentuation
```

For your convenience, my environment is the following:


```python
print("Python %s" % sys.version)
```

    Python 3.6.1 |Anaconda 4.4.0 (64-bit)| (default, May 11 2017, 13:25:24) [MSC v.1900 64 bit (AMD64)]
    

Note, that `Python 3.4+` is required for all libraries to work properly.

#### List CLTK corpora

Let's see what corporas are available for download:


```python
from cltk.corpus.utils.importer import CorpusImporter
corpus_importer = CorpusImporter('greek')
', '.join(corpus_importer.list_corpora)
```




    'greek_software_tlgu, greek_text_perseus, phi7, tlg, greek_proper_names_cltk, greek_models_cltk, greek_treebank_perseus, greek_lexica_perseus, greek_training_set_sentence_cltk, greek_word2vec_cltk, greek_text_lacus_curtius, greek_text_first1kgreek'



I'm going to use `greek_text_perseus` and `greek_text_first1kgreek` corpora for the study, combine them to a single raw text file and unique words database.

### Download corporas

I have collected large part of the used procedures to the [functions](functions.py) script to maintain this notebook document more concise.

The next code snippet will download hundreds of megabytes of Greek text to your local computer for quicker access:


```python
# import corpora
for corpus in ["greek_text_perseus", "greek_text_first1kgreek"]:
    try:
        corpus_importer.import_corpus(corpus)
    except Exception as e:
        print(e)
```

Next I will copy only suitable greek text files from `greek_text_first1kgreek` to the working directory `greek_text_tlg`. Perseus corpora is pretty good as it is.

Note that one can download and extract `greek_text_first1kgreek` directly from  https://github.com/OpenGreekAndLatin/First1KGreek/zipball/master. It may have the most recent and complete set of files. If you wish to use it, extract package directly to `~\cltk_data\greek\text\greek_text_tlg`.


```python
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
```

    C:\Users\phtep\cltk_data\greek\text\greek_text_tlg already exists, lets roll on!
    

Perseus Greek source text is written as a betacode, so I will need a converter script for it. I found a suitable one from: https://github.com/epilanthanomai/hexameter but had to make a small fix to it, so I'm using my own version of the  [betacode](betacode.py) script.

### Process files

Next step is to find out Greek text nodes from the provided XML source files. I have to specify a tag table to find main text lines from the source files so that only Greek texts are processed. XML files have a lot of English and Latin phrases that needs to be stripped out.

Extracted content is saved to the author/work based directories. Simplified uncial conversion is also made at the same time so that the final output file contains only plain words separated by spaces. Pretty much in a format written by the ancient Greeks btw.

#### Collect text files


```python
from functions import init_corpora

# init corpora list
corporas = ["greek_text_perseus", "greek_text_tlg"]

greek_corpora_x = init_corpora(corporas)
print("%s files found" % len(greek_corpora_x))
```

    1272 files found
    

#### Process text files

This will take several minutes depending on if you have already run it once and have temporary directories available:


```python
from functions import remove, all_greek_text_file, perseus_greek_text_file, first1k_greek_text_file, process_greek_corpora

# remove old temp files
try:
    remove(all_greek_text_file)
    remove(perseus_greek_text_file)
    remove(first1k_greek_text_file)
except OSError:
    pass

# collect greek corpora data
# one could use filter to process only selected files here...
#greek_corpora = process_greek_corpora(list(filter(lambda x: "aristot.nic.eth_gk.xml" in x['file'], greek_corpora_x)))
greek_corpora = process_greek_corpora(greek_corpora_x)
```

## Statistics

When files are downloaded and preprocessed, I can get the size of the text files:


```python
from functions import get_file_size

print("Size of the all raw text: %s MB" % get_file_size(all_greek_text_file))
print("Size of the perseus raw text: %s MB" % get_file_size(perseus_greek_text_file))
print("Size of the first1k raw text: %s MB" % get_file_size(first1k_greek_text_file))
#Size of the all raw text: 604.88 MB
#Size of the perseus raw text: 79.74 MB
#Size of the first1k raw text: 525.13 MB
```

    Size of the all raw text: 604.88 MB
    Size of the perseus raw text: 79.74 MB
    Size of the first1k raw text: 525.13 MB
    

I will calculate other statistics of the saved text files for cross checking their content:


```python
from functions import get_stats

ccontent1, chars1, lwords1 = get_stats(perseus_greek_text_file)
ccontent2, chars2, lwords2 = get_stats(first1k_greek_text_file)
ccontent3, chars3, lwords3 = get_stats(all_greek_text_file)
```

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
    
    

## Letter statistics

I'm using Pandas library to handle tabular data and show basic letter statistics.


```python
from functions import Counter, DataFrame
```

#### Calculate statistics

This will take some time too:


```python
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
```

#### Show letter statistics

The first column is the letter, the second column is the count of the letter, and the third column is the percentage of the letter contra all letters.

Show tables side by side to save some vertical space:


```python
from functions import display_side_by_side

display_side_by_side(Perseus=a, First1K=b, Perseus_First1K=c)
```


<table style="display:inline" border="1" class="dataframe">
  <caption style='text-align:center'>Perseus</caption><thead>
    <tr style="text-align: right;">
      <th>Letter</th>
      <th>Count</th>
      <th>Percent</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>Α</td>
      <td>4182002</td>
      <td>10.96</td>
    </tr>
    <tr>
      <td>Ε</td>
      <td>3678672</td>
      <td>9.64</td>
    </tr>
    <tr>
      <td>Ο</td>
      <td>3664034</td>
      <td>9.61</td>
    </tr>
    <tr>
      <td>Ι</td>
      <td>3613662</td>
      <td>9.47</td>
    </tr>
    <tr>
      <td>Ν</td>
      <td>3410850</td>
      <td>8.94</td>
    </tr>
    <tr>
      <td>Τ</td>
      <td>2903418</td>
      <td>7.61</td>
    </tr>
    <tr>
      <td>Σ</td>
      <td>2830967</td>
      <td>7.42</td>
    </tr>
    <tr>
      <td>Υ</td>
      <td>1776871</td>
      <td>4.66</td>
    </tr>
    <tr>
      <td>Ρ</td>
      <td>1440852</td>
      <td>3.78</td>
    </tr>
    <tr>
      <td>Η</td>
      <td>1392909</td>
      <td>3.65</td>
    </tr>
    <tr>
      <td>Π</td>
      <td>1326596</td>
      <td>3.48</td>
    </tr>
    <tr>
      <td>Κ</td>
      <td>1261673</td>
      <td>3.31</td>
    </tr>
    <tr>
      <td>Ω</td>
      <td>1179566</td>
      <td>3.09</td>
    </tr>
    <tr>
      <td>Λ</td>
      <td>1147548</td>
      <td>3.01</td>
    </tr>
    <tr>
      <td>Μ</td>
      <td>1139510</td>
      <td>2.99</td>
    </tr>
    <tr>
      <td>Δ</td>
      <td>932823</td>
      <td>2.45</td>
    </tr>
    <tr>
      <td>Γ</td>
      <td>584668</td>
      <td>1.53</td>
    </tr>
    <tr>
      <td>Θ</td>
      <td>501512</td>
      <td>1.31</td>
    </tr>
    <tr>
      <td>Χ</td>
      <td>352579</td>
      <td>0.92</td>
    </tr>
    <tr>
      <td>Φ</td>
      <td>325210</td>
      <td>0.85</td>
    </tr>
    <tr>
      <td>Β</td>
      <td>220267</td>
      <td>0.58</td>
    </tr>
    <tr>
      <td>Ξ</td>
      <td>152971</td>
      <td>0.40</td>
    </tr>
    <tr>
      <td>Ζ</td>
      <td>75946</td>
      <td>0.20</td>
    </tr>
    <tr>
      <td>Ψ</td>
      <td>51405</td>
      <td>0.13</td>
    </tr>
  </tbody>
</table style="display:inline"><table style="display:inline" border="1" class="dataframe">
  <caption style='text-align:center'>First1K</caption><thead>
    <tr style="text-align: right;">
      <th>Letter</th>
      <th>Count</th>
      <th>Percent</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>Α</td>
      <td>26817705</td>
      <td>10.76</td>
    </tr>
    <tr>
      <td>Ο</td>
      <td>23687669</td>
      <td>9.50</td>
    </tr>
    <tr>
      <td>Ι</td>
      <td>22665483</td>
      <td>9.09</td>
    </tr>
    <tr>
      <td>Ν</td>
      <td>22498413</td>
      <td>9.03</td>
    </tr>
    <tr>
      <td>Ε</td>
      <td>22121458</td>
      <td>8.88</td>
    </tr>
    <tr>
      <td>Τ</td>
      <td>21698265</td>
      <td>8.71</td>
    </tr>
    <tr>
      <td>Σ</td>
      <td>18738234</td>
      <td>7.52</td>
    </tr>
    <tr>
      <td>Υ</td>
      <td>11384921</td>
      <td>4.57</td>
    </tr>
    <tr>
      <td>Ρ</td>
      <td>9776411</td>
      <td>3.92</td>
    </tr>
    <tr>
      <td>Η</td>
      <td>9268111</td>
      <td>3.72</td>
    </tr>
    <tr>
      <td>Κ</td>
      <td>8982955</td>
      <td>3.60</td>
    </tr>
    <tr>
      <td>Π</td>
      <td>8290364</td>
      <td>3.33</td>
    </tr>
    <tr>
      <td>Ω</td>
      <td>7874161</td>
      <td>3.16</td>
    </tr>
    <tr>
      <td>Μ</td>
      <td>7498489</td>
      <td>3.01</td>
    </tr>
    <tr>
      <td>Λ</td>
      <td>6929170</td>
      <td>2.78</td>
    </tr>
    <tr>
      <td>Δ</td>
      <td>5757782</td>
      <td>2.31</td>
    </tr>
    <tr>
      <td>Γ</td>
      <td>4197053</td>
      <td>1.68</td>
    </tr>
    <tr>
      <td>Θ</td>
      <td>3440599</td>
      <td>1.38</td>
    </tr>
    <tr>
      <td>Χ</td>
      <td>2294905</td>
      <td>0.92</td>
    </tr>
    <tr>
      <td>Φ</td>
      <td>2115768</td>
      <td>0.85</td>
    </tr>
    <tr>
      <td>Β</td>
      <td>1322737</td>
      <td>0.53</td>
    </tr>
    <tr>
      <td>Ξ</td>
      <td>951076</td>
      <td>0.38</td>
    </tr>
    <tr>
      <td>Ζ</td>
      <td>559728</td>
      <td>0.22</td>
    </tr>
    <tr>
      <td>Ψ</td>
      <td>375266</td>
      <td>0.15</td>
    </tr>
    <tr>
      <td>Ϛ</td>
      <td>8430</td>
      <td>0.00</td>
    </tr>
    <tr>
      <td>Ϡ</td>
      <td>364</td>
      <td>0.00</td>
    </tr>
    <tr>
      <td>Ϟ</td>
      <td>204</td>
      <td>0.00</td>
    </tr>
  </tbody>
</table style="display:inline"><table style="display:inline" border="1" class="dataframe">
  <caption style='text-align:center'>Perseus_First1K</caption><thead>
    <tr style="text-align: right;">
      <th>Letter</th>
      <th>Count</th>
      <th>Percent</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>Α</td>
      <td>30999707</td>
      <td>10.79</td>
    </tr>
    <tr>
      <td>Ο</td>
      <td>27351703</td>
      <td>9.52</td>
    </tr>
    <tr>
      <td>Ι</td>
      <td>26279145</td>
      <td>9.14</td>
    </tr>
    <tr>
      <td>Ν</td>
      <td>25909263</td>
      <td>9.01</td>
    </tr>
    <tr>
      <td>Ε</td>
      <td>25800130</td>
      <td>8.98</td>
    </tr>
    <tr>
      <td>Τ</td>
      <td>24601683</td>
      <td>8.56</td>
    </tr>
    <tr>
      <td>Σ</td>
      <td>21569201</td>
      <td>7.50</td>
    </tr>
    <tr>
      <td>Υ</td>
      <td>13161792</td>
      <td>4.58</td>
    </tr>
    <tr>
      <td>Ρ</td>
      <td>11217263</td>
      <td>3.90</td>
    </tr>
    <tr>
      <td>Η</td>
      <td>10661020</td>
      <td>3.71</td>
    </tr>
    <tr>
      <td>Κ</td>
      <td>10244628</td>
      <td>3.56</td>
    </tr>
    <tr>
      <td>Π</td>
      <td>9616960</td>
      <td>3.35</td>
    </tr>
    <tr>
      <td>Ω</td>
      <td>9053727</td>
      <td>3.15</td>
    </tr>
    <tr>
      <td>Μ</td>
      <td>8637999</td>
      <td>3.01</td>
    </tr>
    <tr>
      <td>Λ</td>
      <td>8076718</td>
      <td>2.81</td>
    </tr>
    <tr>
      <td>Δ</td>
      <td>6690605</td>
      <td>2.33</td>
    </tr>
    <tr>
      <td>Γ</td>
      <td>4781721</td>
      <td>1.66</td>
    </tr>
    <tr>
      <td>Θ</td>
      <td>3942111</td>
      <td>1.37</td>
    </tr>
    <tr>
      <td>Χ</td>
      <td>2647484</td>
      <td>0.92</td>
    </tr>
    <tr>
      <td>Φ</td>
      <td>2440978</td>
      <td>0.85</td>
    </tr>
    <tr>
      <td>Β</td>
      <td>1543004</td>
      <td>0.54</td>
    </tr>
    <tr>
      <td>Ξ</td>
      <td>1104047</td>
      <td>0.38</td>
    </tr>
    <tr>
      <td>Ζ</td>
      <td>635674</td>
      <td>0.22</td>
    </tr>
    <tr>
      <td>Ψ</td>
      <td>426671</td>
      <td>0.15</td>
    </tr>
    <tr>
      <td>Ϛ</td>
      <td>8430</td>
      <td>0.00</td>
    </tr>
    <tr>
      <td>Ϡ</td>
      <td>364</td>
      <td>0.00</td>
    </tr>
    <tr>
      <td>Ϟ</td>
      <td>204</td>
      <td>0.00</td>
    </tr>
  </tbody>
</table style="display:inline">


`First1K` corpora contains mathematical texts in Greek, which explains why the rarely used digamma (Ϛ = 6), qoppa (Ϟ/Ϙ = 90), and sampi(Ϡ = 900) letters are included on the table. You can find other interesting differences too, like the occurrence of E/T, K/Π, and M/Λ, which are probably explained by the difference of the included text genres in the corporas.

#### Plotly bar chart for letter stats

The next chart will show visually which are the most used letters and the least used letters in the available Ancient Greek corpora.

<img src="https://github.com/markomanninen/grcriddles/blob/master/stats.png?raw=true" />

Vowels with `N`, `S`, and `T` consonants pops up as the most used letters. The least used letters are `Z`, `Chi`, and `Psi`.

Uncomment next part to output a new fresh graph from Plotly:

```python
#from plotly.offline import init_notebook_mode
#init_notebook_mode(connected=False)

# for the fist time set plotly service credentials, then you can comment the next line
#import plotly
#plotly.tools.set_credentials_file(username='MarkoManninen', api_key='xyz')

# use tables and graphs...
#import plotly.tools as tls
# embed plotly graphs
#tls.embed("https://plot.ly/~MarkoManninen/8/")
```

Then it is time to store unique Greek words to the database and show some specialties of the word statistics. This will take a minute or two:


```python
from functions import syllabify, Abnum, greek

# greek abnum object for calculating isopsephical value
g = Abnum(greek)

# lets count unique words statistic from the parsed greek corpora rather than the plain text file
# it would be pretty dauntful to find out occurence of the all 800000+ unique words from the text 
# file that is over 600 MB big!
unique_word_stats = {}
for item in greek_corpora:
    for word, cnt in item['uwords'].items():
        if word not in unique_word_stats:
            unique_word_stats[word] = 0
        unique_word_stats[word] += cnt

# init dataframe
df = DataFrame([[k, v] for k, v in unique_word_stats.items()])
# add column for the occurrence percentage of the word
df[2] = df[1].apply(lambda x: round(x*100/lwords1, 2))
# add column for the length of the word
df[3] = df[0].apply(lambda x: len(x))
# add isopsephy column
df[4] = df[0].apply(lambda x: g.value(x))
# add syllabified column
df[5] = df[0].apply(lambda x: syllabify(x))
# add length of the syllables column
df[6] = df[5].apply(lambda x: len(x))
```

### Save unique words database

This is the single most important part of the document. I'm saving all simplified unique words as a csv file that can be used as a database for the riddle solver. After this you may proceed to the [riddle solver](Isopsephical riddles in the Greek Pseudo Sibylline hexameter poetry.ipynb) Jupyter notebook document in interactive mode if you prefer.


```python
from functions import csv_file_name, syllabify, Abnum, greek
df.to_csv(csv_file_name, header=False, index=False, encoding='utf-8')
```

For confirmation, I will show twenty of the most repeated words in the database:


```python
from functions import display_html
# use to_html and index=False to hide index column
display_html(df.sort_values(1, ascending=False).head(n=20).to_html(index=False), raw=True)
```


<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th>0</th>
      <th>1</th>
      <th>2</th>
      <th>3</th>
      <th>4</th>
      <th>5</th>
      <th>6</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>ΚΑΙ</td>
      <td>3332509</td>
      <td>45.51</td>
      <td>3</td>
      <td>31</td>
      <td>[ΚΑΙ]</td>
      <td>1</td>
    </tr>
    <tr>
      <td>ΔΕ</td>
      <td>1355091</td>
      <td>18.51</td>
      <td>2</td>
      <td>9</td>
      <td>[ΔΕ]</td>
      <td>1</td>
    </tr>
    <tr>
      <td>ΤΟ</td>
      <td>1297764</td>
      <td>17.72</td>
      <td>2</td>
      <td>370</td>
      <td>[ΤΟ]</td>
      <td>1</td>
    </tr>
    <tr>
      <td>ΤΟΥ</td>
      <td>933432</td>
      <td>12.75</td>
      <td>3</td>
      <td>770</td>
      <td>[ΤΟΥ]</td>
      <td>1</td>
    </tr>
    <tr>
      <td>ΤΩΝ</td>
      <td>918946</td>
      <td>12.55</td>
      <td>3</td>
      <td>1150</td>
      <td>[ΤΩΝ]</td>
      <td>1</td>
    </tr>
    <tr>
      <td>Η</td>
      <td>886577</td>
      <td>12.11</td>
      <td>1</td>
      <td>8</td>
      <td>[Η]</td>
      <td>1</td>
    </tr>
    <tr>
      <td>ΤΗΝ</td>
      <td>806695</td>
      <td>11.02</td>
      <td>3</td>
      <td>358</td>
      <td>[ΤΗΝ]</td>
      <td>1</td>
    </tr>
    <tr>
      <td>ΕΝ</td>
      <td>715117</td>
      <td>9.77</td>
      <td>2</td>
      <td>55</td>
      <td>[ΕΝ]</td>
      <td>1</td>
    </tr>
    <tr>
      <td>ΤΗΣ</td>
      <td>692091</td>
      <td>9.45</td>
      <td>3</td>
      <td>508</td>
      <td>[ΤΗΣ]</td>
      <td>1</td>
    </tr>
    <tr>
      <td>Ο</td>
      <td>678340</td>
      <td>9.26</td>
      <td>1</td>
      <td>70</td>
      <td>[Ο]</td>
      <td>1</td>
    </tr>
    <tr>
      <td>ΓΑΡ</td>
      <td>634722</td>
      <td>8.67</td>
      <td>3</td>
      <td>104</td>
      <td>[ΓΑΡ]</td>
      <td>1</td>
    </tr>
    <tr>
      <td>ΜΕΝ</td>
      <td>593622</td>
      <td>8.11</td>
      <td>3</td>
      <td>95</td>
      <td>[ΜΕΝ]</td>
      <td>1</td>
    </tr>
    <tr>
      <td>ΤΑ</td>
      <td>552785</td>
      <td>7.55</td>
      <td>2</td>
      <td>301</td>
      <td>[ΤΑ]</td>
      <td>1</td>
    </tr>
    <tr>
      <td>ΤΟΝ</td>
      <td>524407</td>
      <td>7.16</td>
      <td>3</td>
      <td>420</td>
      <td>[ΤΟΝ]</td>
      <td>1</td>
    </tr>
    <tr>
      <td>ΤΩ</td>
      <td>466797</td>
      <td>6.37</td>
      <td>2</td>
      <td>1100</td>
      <td>[ΤΩ]</td>
      <td>1</td>
    </tr>
    <tr>
      <td>ΩΣ</td>
      <td>412402</td>
      <td>5.63</td>
      <td>2</td>
      <td>1000</td>
      <td>[ΩΣ]</td>
      <td>1</td>
    </tr>
    <tr>
      <td>ΕΙΣ</td>
      <td>371682</td>
      <td>5.08</td>
      <td>3</td>
      <td>215</td>
      <td>[ΕΙΣ]</td>
      <td>1</td>
    </tr>
    <tr>
      <td>ΤΕ</td>
      <td>339484</td>
      <td>4.64</td>
      <td>2</td>
      <td>305</td>
      <td>[ΤΕ]</td>
      <td>1</td>
    </tr>
    <tr>
      <td>Δ</td>
      <td>339061</td>
      <td>4.63</td>
      <td>1</td>
      <td>4</td>
      <td>[Δ]</td>
      <td>1</td>
    </tr>
    <tr>
      <td>ΟΥ</td>
      <td>338187</td>
      <td>4.62</td>
      <td>2</td>
      <td>470</td>
      <td>[ΟΥ]</td>
      <td>1</td>
    </tr>
  </tbody>
</table>


For curiosity, let's also see the longest words in the database:


```python
from functions import HTML
l = df.sort_values(3, ascending=False).head(n=20)
HTML(l.to_html(index=False))
```




<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th>0</th>
      <th>1</th>
      <th>2</th>
      <th>3</th>
      <th>4</th>
      <th>5</th>
      <th>6</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>ΑΛΛΗΣΤΗΣΑΝΩΘΕΝΘΕΡΜΤΗΤΟΣΑΤΜΙΔΟΜΕΝΟΝΦΡΕΤΑΙ</td>
      <td>3</td>
      <td>0.0</td>
      <td>40</td>
      <td>4280</td>
      <td>[ΑΛ, ΛΗ, ΣΤΗ, ΣΑ, ΝΩ, ΘΕΝ, ΘΕΡΜ, ΤΗ, ΤΟ, ΣΑΤ, ...</td>
      <td>16</td>
    </tr>
    <tr>
      <td>ΔΥΝΑΤΟΝΔΕΤΟΑΙΤΑΙΗΣΓΕΝΣΕΩΣΚΑΙΤΗΣΦΘΟΡΑΣ</td>
      <td>3</td>
      <td>0.0</td>
      <td>37</td>
      <td>4466</td>
      <td>[ΔΥ, ΝΑ, ΤΟΝ, ΔΕ, ΤΟ, ΑΙ, ΤΑΙ, ΗΣ, ΓΕΝ, ΣΕ, Ω,...</td>
      <td>15</td>
    </tr>
    <tr>
      <td>ΕΝΝΕΑΚΑΙΔΕΚΑΕΤΗΡΙΕΝΝΕΑΚΑΙΔΕΚΑΕΤΗΡΔΟΣ</td>
      <td>2</td>
      <td>0.0</td>
      <td>36</td>
      <td>1454</td>
      <td>[ΕΝ, ΝΕ, Α, ΚΑΙ, ΔΕ, ΚΑ, Ε, ΤΗ, ΡΙ, ΕΝ, ΝΕ, Α,...</td>
      <td>18</td>
    </tr>
    <tr>
      <td>ΣΙΑΛΟΙΟΡΑΧΙΝΤΕΘΑΛΥΙΑΝΑΛΟΙΦΗΕΥΤΡΑΦΟΥΣ</td>
      <td>4</td>
      <td>0.0</td>
      <td>36</td>
      <td>4553</td>
      <td>[ΣΙ, Α, ΛΟΙ, Ο, ΡΑ, ΧΙΝ, ΤΕ, ΘΑ, ΛΥΙ, Α, ΝΑ, Λ...</td>
      <td>16</td>
    </tr>
    <tr>
      <td>ΕΜΟΥΙΑΠΦΕΥΓΑΧΕΙΡΑΣΛΥΠΣΑΣΜΕΝΟΥΔΝΑΟΥΔΝ</td>
      <td>3</td>
      <td>0.0</td>
      <td>36</td>
      <td>4486</td>
      <td>[Ε, ΜΟΥΙ, ΑΠ, ΦΕΥ, ΓΑ, ΧΕΙ, ΡΑΣ, ΛΥΠ, ΣΑ, ΣΜΕ,...</td>
      <td>13</td>
    </tr>
    <tr>
      <td>ΚΑΙΟΣΑΑΛΛΑΤΩΝΤΟΙΟΥΤΩΝΠΡΟΣΔΙΟΡΙΖΜΕΘΑ</td>
      <td>2</td>
      <td>0.0</td>
      <td>35</td>
      <td>4220</td>
      <td>[ΚΑΙ, Ο, ΣΑ, ΑΛ, ΛΑ, ΤΩΝ, ΤΟΙ, ΟΥ, ΤΩΝ, ΠΡΟΣ, ...</td>
      <td>15</td>
    </tr>
    <tr>
      <td>ΕΝΝΕΑΚΑΙΕΙΚΟΣΙΚΑΙΕΠΤΑΚΟΣΙΟΠΛΑΣΙΑΚΙΣ</td>
      <td>1</td>
      <td>0.0</td>
      <td>35</td>
      <td>1796</td>
      <td>[ΕΝ, ΝΕ, Α, ΚΑΙ, ΕΙ, ΚΟ, ΣΙ, ΚΑΙ, Ε, ΠΤΑ, ΚΟ, ...</td>
      <td>17</td>
    </tr>
    <tr>
      <td>ΟΡΘΡΟΦΟΙΤΟΣΥΚΟΦΑΝΤΟΔΙΚΟΤΑΛΑΙΠΩΡΩΝ</td>
      <td>1</td>
      <td>0.0</td>
      <td>33</td>
      <td>5186</td>
      <td>[ΟΡ, ΘΡΟ, ΦΟΙ, ΤΟ, ΣΥ, ΚΟ, ΦΑΝ, ΤΟ, ΔΙ, ΚΟ, ΤΑ...</td>
      <td>14</td>
    </tr>
    <tr>
      <td>ΤΕΤΤΑΡΑΚΟΝΤΑΚΑΙΠΕΝΤΑΚΙΣΧΙΛΙΟΣΤΟΝ</td>
      <td>1</td>
      <td>0.0</td>
      <td>32</td>
      <td>3485</td>
      <td>[ΤΕΤ, ΤΑ, ΡΑ, ΚΟΝ, ΤΑ, ΚΑΙ, ΠΕΝ, ΤΑ, ΚΙ, ΣΧΙ, ...</td>
      <td>13</td>
    </tr>
    <tr>
      <td>ΚΑΙΙΚΛΗΧΡΥΣΗΑΦΡΟΔΤΗΚΑΙΟΙΣΕΚΣΜΗΣΕ</td>
      <td>3</td>
      <td>0.0</td>
      <td>32</td>
      <td>3179</td>
      <td>[ΚΑΙ, Ι, ΚΛΗ, ΧΡΥ, ΣΗ, Α, ΦΡΟΔ, ΤΗ, ΚΑΙ, ΟΙ, Σ...</td>
      <td>13</td>
    </tr>
    <tr>
      <td>ΟΤΙΤΟΥΜΗΔΙΑΠΡΟΤΡΩΝΟΡΖΕΣΘΑΙΤΡΕΙΣ</td>
      <td>2</td>
      <td>0.0</td>
      <td>31</td>
      <td>3730</td>
      <td>[Ο, ΤΙ, ΤΟΥ, ΜΗ, ΔΙ, Α, ΠΡΟ, ΤΡΩ, ΝΟΡ, ΖΕ, ΣΘΑ...</td>
      <td>12</td>
    </tr>
    <tr>
      <td>ΑΥΤΟΜΑΤΟΙΔΕΟΙΘΕΟΙΑΠΑΛΛΑΣΣΟΜΕΝΟΙ</td>
      <td>3</td>
      <td>0.0</td>
      <td>31</td>
      <td>2163</td>
      <td>[ΑΥ, ΤΟ, ΜΑ, ΤΟΙ, ΔΕ, ΟΙ, ΘΕ, ΟΙ, Α, ΠΑΛ, ΛΑΣ,...</td>
      <td>14</td>
    </tr>
    <tr>
      <td>ΣΠΕΡΜΑΓΟΡΑΙΟΛΕΚΙΘΟΛΑΧΑΝΟΠΩΛΙΔΕΣ</td>
      <td>1</td>
      <td>0.0</td>
      <td>31</td>
      <td>2705</td>
      <td>[ΣΠΕΡ, ΜΑ, ΓΟ, ΡΑΙ, Ο, ΛΕ, ΚΙ, ΘΟ, ΛΑ, ΧΑ, ΝΟ,...</td>
      <td>14</td>
    </tr>
    <tr>
      <td>ΗΔΙΚΗΜΝΟΝΔΕΑΠΕΡΡΙΜΜΝΟΝΠΕΡΙΟΡΑΣ</td>
      <td>2</td>
      <td>0.0</td>
      <td>30</td>
      <td>1381</td>
      <td>[Η, ΔΙ, ΚΗ, ΜΝΟΝ, ΔΕ, Α, ΠΕΡ, ΡΙΜ, ΜΝΟΝ, ΠΕ, Ρ...</td>
      <td>13</td>
    </tr>
    <tr>
      <td>ΠΑΡΥΦΙΣΤΑΜΕΝΟΥΠΡΑΓΜΑΤΟΣΚΟΙΝΩΣ</td>
      <td>3</td>
      <td>0.0</td>
      <td>29</td>
      <td>4102</td>
      <td>[ΠΑ, ΡΥ, ΦΙ, ΣΤΑ, ΜΕ, ΝΟΥ, ΠΡΑΓ, ΜΑ, ΤΟ, ΣΚΟΙ,...</td>
      <td>11</td>
    </tr>
    <tr>
      <td>ΧΙΛΙΟΚΤΑΚΟΣΙΟΥΔΟΗΚΟΝΤΑΠΛΑΣΟΝΑ</td>
      <td>2</td>
      <td>0.0</td>
      <td>29</td>
      <td>2766</td>
      <td>[ΧΙ, ΛΙ, Ο, ΚΤΑ, ΚΟ, ΣΙ, ΟΥ, ΔΟ, Η, ΚΟΝ, ΤΑ, Π...</td>
      <td>14</td>
    </tr>
    <tr>
      <td>ΕΝΝΕΑΚΑΙΔΕΕΝΝΕΑΚΑΙΔΕΚΑΕΤΗΡΔΩΝ</td>
      <td>2</td>
      <td>0.0</td>
      <td>29</td>
      <td>1590</td>
      <td>[ΕΝ, ΝΕ, Α, ΚΑΙ, ΔΕ, ΕΝ, ΝΕ, Α, ΚΑΙ, ΔΕ, ΚΑ, Ε...</td>
      <td>14</td>
    </tr>
    <tr>
      <td>ΕΚΑΤΟΝΤΑΚΑΙΕΒΔΟΜΗΚΟΝΤΑΠΛΑΣΙΟΝ</td>
      <td>3</td>
      <td>0.0</td>
      <td>29</td>
      <td>1789</td>
      <td>[Ε, ΚΑ, ΤΟΝ, ΤΑ, ΚΑΙ, Ε, ΒΔΟ, ΜΗ, ΚΟΝ, ΤΑ, ΠΛΑ...</td>
      <td>13</td>
    </tr>
    <tr>
      <td>ΣΚΟΡΟΔΟΠΑΝΔΟΚΕΥΤΡΙΑΡΤΟΠΩΛΙΔΕΣ</td>
      <td>1</td>
      <td>0.0</td>
      <td>29</td>
      <td>3174</td>
      <td>[ΣΚΟ, ΡΟ, ΔΟ, ΠΑΝ, ΔΟ, ΚΕΥ, ΤΡΙ, ΑΡ, ΤΟ, ΠΩ, Λ...</td>
      <td>12</td>
    </tr>
    <tr>
      <td>ΣΙΛΦΙΟΤΥΡΟΜΕΛΙΤΟΚΑΤΑΚΕΧΥΜΕΝΟ</td>
      <td>1</td>
      <td>0.0</td>
      <td>28</td>
      <td>3657</td>
      <td>[ΣΙΛ, ΦΙ, Ο, ΤΥ, ΡΟ, ΜΕ, ΛΙ, ΤΟ, ΚΑ, ΤΑ, ΚΕ, Χ...</td>
      <td>14</td>
    </tr>
  </tbody>
</table>



How about finding out, which words has the biggest isopsephical values?


```python
HTML(df.sort_values(4, ascending=False).head(n=20).to_html(index=False))
```




<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th>0</th>
      <th>1</th>
      <th>2</th>
      <th>3</th>
      <th>4</th>
      <th>5</th>
      <th>6</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>ΟΡΘΡΟΦΟΙΤΟΣΥΚΟΦΑΝΤΟΔΙΚΟΤΑΛΑΙΠΩΡΩΝ</td>
      <td>1</td>
      <td>0.0</td>
      <td>33</td>
      <td>5186</td>
      <td>[ΟΡ, ΘΡΟ, ΦΟΙ, ΤΟ, ΣΥ, ΚΟ, ΦΑΝ, ΤΟ, ΔΙ, ΚΟ, ΤΑ...</td>
      <td>14</td>
    </tr>
    <tr>
      <td>ΓΛΩΣΣΟΤΟΜΗΘΕΝΤΩΝΧΡΙΣΤΙΑΝΩΝ</td>
      <td>3</td>
      <td>0.0</td>
      <td>26</td>
      <td>5056</td>
      <td>[ΓΛΩΣ, ΣΟ, ΤΟ, ΜΗ, ΘΕΝ, ΤΩΝ, ΧΡΙ, ΣΤΙ, Α, ΝΩΝ]</td>
      <td>10</td>
    </tr>
    <tr>
      <td>ΣΙΑΛΟΙΟΡΑΧΙΝΤΕΘΑΛΥΙΑΝΑΛΟΙΦΗΕΥΤΡΑΦΟΥΣ</td>
      <td>4</td>
      <td>0.0</td>
      <td>36</td>
      <td>4553</td>
      <td>[ΣΙ, Α, ΛΟΙ, Ο, ΡΑ, ΧΙΝ, ΤΕ, ΘΑ, ΛΥΙ, Α, ΝΑ, Λ...</td>
      <td>16</td>
    </tr>
    <tr>
      <td>ΤΟΙΧΩΡΥΧΟΥΝΤΩΝ</td>
      <td>1</td>
      <td>0.0</td>
      <td>14</td>
      <td>4550</td>
      <td>[ΤΟΙ, ΧΩ, ΡΥ, ΧΟΥΝ, ΤΩΝ]</td>
      <td>5</td>
    </tr>
    <tr>
      <td>ΕΜΟΥΙΑΠΦΕΥΓΑΧΕΙΡΑΣΛΥΠΣΑΣΜΕΝΟΥΔΝΑΟΥΔΝ</td>
      <td>3</td>
      <td>0.0</td>
      <td>36</td>
      <td>4486</td>
      <td>[Ε, ΜΟΥΙ, ΑΠ, ΦΕΥ, ΓΑ, ΧΕΙ, ΡΑΣ, ΛΥΠ, ΣΑ, ΣΜΕ,...</td>
      <td>13</td>
    </tr>
    <tr>
      <td>ΔΥΝΑΤΟΝΔΕΤΟΑΙΤΑΙΗΣΓΕΝΣΕΩΣΚΑΙΤΗΣΦΘΟΡΑΣ</td>
      <td>3</td>
      <td>0.0</td>
      <td>37</td>
      <td>4466</td>
      <td>[ΔΥ, ΝΑ, ΤΟΝ, ΔΕ, ΤΟ, ΑΙ, ΤΑΙ, ΗΣ, ΓΕΝ, ΣΕ, Ω,...</td>
      <td>15</td>
    </tr>
    <tr>
      <td>ΣΥΝΥΠΟΧΩΡΟΥΝΤΩΝ</td>
      <td>1</td>
      <td>0.0</td>
      <td>15</td>
      <td>4370</td>
      <td>[ΣΥ, ΝΥ, ΠΟ, ΧΩ, ΡΟΥΝ, ΤΩΝ]</td>
      <td>6</td>
    </tr>
    <tr>
      <td>ΤΩΟΡΘΩΕΚΑΣΤΑΘΕΩΡΩΝ</td>
      <td>4</td>
      <td>0.0</td>
      <td>18</td>
      <td>4370</td>
      <td>[ΤΩ, ΟΡ, ΘΩ, Ε, ΚΑ, ΣΤΑ, ΘΕ, Ω, ΡΩΝ]</td>
      <td>9</td>
    </tr>
    <tr>
      <td>ΑΛΛΗΣΤΗΣΑΝΩΘΕΝΘΕΡΜΤΗΤΟΣΑΤΜΙΔΟΜΕΝΟΝΦΡΕΤΑΙ</td>
      <td>3</td>
      <td>0.0</td>
      <td>40</td>
      <td>4280</td>
      <td>[ΑΛ, ΛΗ, ΣΤΗ, ΣΑ, ΝΩ, ΘΕΝ, ΘΕΡΜ, ΤΗ, ΤΟ, ΣΑΤ, ...</td>
      <td>16</td>
    </tr>
    <tr>
      <td>ΩΡΙΣΜΕΝΩΝΠΡΟΣΩΠΩΝ</td>
      <td>2</td>
      <td>0.0</td>
      <td>17</td>
      <td>4235</td>
      <td>[Ω, ΡΙ, ΣΜΕ, ΝΩΝ, ΠΡΟ, ΣΩ, ΠΩΝ]</td>
      <td>7</td>
    </tr>
    <tr>
      <td>ΚΑΙΟΣΑΑΛΛΑΤΩΝΤΟΙΟΥΤΩΝΠΡΟΣΔΙΟΡΙΖΜΕΘΑ</td>
      <td>2</td>
      <td>0.0</td>
      <td>35</td>
      <td>4220</td>
      <td>[ΚΑΙ, Ο, ΣΑ, ΑΛ, ΛΑ, ΤΩΝ, ΤΟΙ, ΟΥ, ΤΩΝ, ΠΡΟΣ, ...</td>
      <td>15</td>
    </tr>
    <tr>
      <td>ΤΟΥΤΟΥΣΛΕΓΟΝΤΕΣΩΣΠΡΟΣΤΗΝ</td>
      <td>2</td>
      <td>0.0</td>
      <td>24</td>
      <td>4211</td>
      <td>[ΤΟΥ, ΤΟΥΣ, ΛΕ, ΓΟΝ, ΤΕ, ΣΩ, ΣΠΡΟ, ΣΤΗΝ]</td>
      <td>8</td>
    </tr>
    <tr>
      <td>ΨΥΧΟΓΟΝΙΜΩΤΤΩΝ</td>
      <td>3</td>
      <td>0.0</td>
      <td>14</td>
      <td>4193</td>
      <td>[ΨΥ, ΧΟ, ΓΟ, ΝΙ, ΜΩΤ, ΤΩΝ]</td>
      <td>6</td>
    </tr>
    <tr>
      <td>ΚΙΧΛΕΠΙΚΟΣΣΥΦΟΦΑΤΤΟΠΕΡΙΣΤΕΡΑ</td>
      <td>1</td>
      <td>0.0</td>
      <td>28</td>
      <td>4187</td>
      <td>[ΚΙ, ΧΛΕ, ΠΙ, ΚΟΣ, ΣΥ, ΦΟ, ΦΑΤ, ΤΟ, ΠΕ, ΡΙ, ΣΤ...</td>
      <td>12</td>
    </tr>
    <tr>
      <td>ΨΥΧΑΓΩΓΟΥΝΤΩΝ</td>
      <td>1</td>
      <td>0.0</td>
      <td>13</td>
      <td>4177</td>
      <td>[ΨΥ, ΧΑ, ΓΩ, ΓΟΥΝ, ΤΩΝ]</td>
      <td>5</td>
    </tr>
    <tr>
      <td>ΦΙΛΟΞΕΝΩΤΑΤΟΣΟΥΤΩΣ</td>
      <td>4</td>
      <td>0.0</td>
      <td>18</td>
      <td>4166</td>
      <td>[ΦΙ, ΛΟ, ΞΕ, ΝΩ, ΤΑ, ΤΟ, ΣΟΥ, ΤΩΣ]</td>
      <td>8</td>
    </tr>
    <tr>
      <td>ΥΠΟΧΩΡΗΤΙΚΩΤΤΟΙΣΙΝ</td>
      <td>3</td>
      <td>0.0</td>
      <td>18</td>
      <td>4128</td>
      <td>[Υ, ΠΟ, ΧΩ, ΡΗ, ΤΙ, ΚΩΤ, ΤΟΙ, ΣΙΝ]</td>
      <td>8</td>
    </tr>
    <tr>
      <td>ΚΩΝΣΤΑΝΤΙΝΟΥΤΕΛΕΥΤΗΣΑΝΤΟΣ</td>
      <td>3</td>
      <td>0.0</td>
      <td>25</td>
      <td>4120</td>
      <td>[ΚΩΝ, ΣΤΑΝ, ΤΙ, ΝΟΥ, ΤΕ, ΛΕΥ, ΤΗ, ΣΑΝ, ΤΟΣ]</td>
      <td>9</td>
    </tr>
    <tr>
      <td>ΠΑΡΥΦΙΣΤΑΜΕΝΟΥΠΡΑΓΜΑΤΟΣΚΟΙΝΩΣ</td>
      <td>3</td>
      <td>0.0</td>
      <td>29</td>
      <td>4102</td>
      <td>[ΠΑ, ΡΥ, ΦΙ, ΣΤΑ, ΜΕ, ΝΟΥ, ΠΡΑΓ, ΜΑ, ΤΟ, ΣΚΟΙ,...</td>
      <td>11</td>
    </tr>
    <tr>
      <td>ΕΜΨΥΧΟΝΑΝΘΡΩΠΟΣΖΩΟΝ</td>
      <td>8</td>
      <td>0.0</td>
      <td>19</td>
      <td>4102</td>
      <td>[ΕΜ, ΨΥ, ΧΟ, ΝΑΝ, ΘΡΩ, ΠΟΣ, ΖΩ, ΟΝ]</td>
      <td>8</td>
    </tr>
  </tbody>
</table>



How many percent of the whole word base, the least repeated words take:


```python
le = len(df)
for x, y in df.groupby([1, 2]).count()[:10].T.items():
    print("words repeating %s time(s): " % x[0], round(100*y[0]/le, 2), "%")
```

    words repeating 1 time(s):  14.81 %
    words repeating 2 time(s):  14.61 %
    words repeating 3 time(s):  16.49 %
    words repeating 4 time(s):  10.5 %
    words repeating 5 time(s):  3.66 %
    words repeating 6 time(s):  4.95 %
    words repeating 7 time(s):  2.53 %
    words repeating 8 time(s):  3.3 %
    words repeating 9 time(s):  2.17 %
    words repeating 10 time(s):  1.7 %
    

Words that repeat 1-4 times fills the 60% of the whole text. Words repeating three times takes 16.5% of the words being the greatest repeatance factor.

Finally, for cross checking the data processing algorithm, I want to know in which texts the longest words occur:


```python
from functions import listdir, get_content
# using already instantiated l variable I'm collecting the plain text words
words = list(y[0] for x, y in l.T.items())

def has_words(data):
    a = {}
    for x in words:
        # partial match is fine here. data should be split to words for exact match
        # but it will take more processing time. for shorter words it might be more useful however
        if x in data:
            a[x] = data.count(x)
    return a

def has_content(f):
    content = get_content(f)
    a = has_words(content)
    if a:
        print(f, a)

# iterate all corporas and see if selected words occur in the text
for corp in corporas:
    for a in listdir(corp):
        b = path.join(corp, a)
        if path.isdir(b):
            for c in listdir(b):
                d = path.join(b, c)
                if path.isfile(d):
                    has_content(d)
```

    greek_text_perseus\Aristophanes\Simplified_Ecclesiazusae.txt {'ΣΙΛΦΙΟΤΥΡΟΜΕΛΙΤΟΚΑΤΑΚΕΧΥΜΕΝΟ': 1}
    greek_text_perseus\Aristophanes\Simplified_Lysistrata.txt {'ΣΠΕΡΜΑΓΟΡΑΙΟΛΕΚΙΘΟΛΑΧΑΝΟΠΩΛΙΔΕΣ': 1, 'ΣΚΟΡΟΔΟΠΑΝΔΟΚΕΥΤΡΙΑΡΤΟΠΩΛΙΔΕΣ': 1}
    greek_text_perseus\Aristophanes\Simplified_Wasps.txt {'ΟΡΘΡΟΦΟΙΤΟΣΥΚΟΦΑΝΤΟΔΙΚΟΤΑΛΑΙΠΩΡΩΝ': 1}
    greek_text_perseus\Plato\Simplified_LawsMachineReadableText.txt {'ΤΕΤΤΑΡΑΚΟΝΤΑΚΑΙΠΕΝΤΑΚΙΣΧΙΛΙΟΣΤΟΝ': 1}
    greek_text_perseus\Plato\Simplified_RepublicMachineReadableText.txt {'ΕΝΝΕΑΚΑΙΕΙΚΟΣΙΚΑΙΕΠΤΑΚΟΣΙΟΠΛΑΣΙΑΚΙΣ': 1}
    greek_text_tlg\AlexanderOfAphrodisias\Simplified_InAristotelisTopicorumLibrosOctoCommentaria.txt {'ΟΤΙΤΟΥΜΗΔΙΑΠΡΟΤΡΩΝΟΡΖΕΣΘΑΙΤΡΕΙΣ': 2}
    greek_text_tlg\Ammonius\Simplified_InAristotelisLibrumDeInterpretationeCommentarius.txt {'ΚΑΙΟΣΑΑΛΛΑΤΩΝΤΟΙΟΥΤΩΝΠΡΟΣΔΙΟΡΙΖΜΕΘΑ': 2}
    greek_text_tlg\ApolloniusDyscolus\Simplified_DeConstructione.txt {'ΠΑΡΥΦΙΣΤΑΜΕΝΟΥΠΡΑΓΜΑΤΟΣΚΟΙΝΩΣ': 3}
    greek_text_tlg\Artemidorus\Simplified_Onirocriticon.txt {'ΑΥΤΟΜΑΤΟΙΔΕΟΙΘΕΟΙΑΠΑΛΛΑΣΣΟΜΕΝΟΙ': 3}
    greek_text_tlg\ChroniconPaschale\Simplified_ChroniconPaschale.txt {'ΕΝΝΕΑΚΑΙΔΕΚΑΕΤΗΡΙΕΝΝΕΑΚΑΙΔΕΚΑΕΤΗΡΔΟΣ': 2, 'ΕΝΝΕΑΚΑΙΔΕΕΝΝΕΑΚΑΙΔΕΚΑΕΤΗΡΔΩΝ': 2}
    greek_text_tlg\ClaudiusPtolemaeus\Simplified_SyntaxisMathematica.txt {'ΕΚΑΤΟΝΤΑΚΑΙΕΒΔΟΜΗΚΟΝΤΑΠΛΑΣΙΟΝ': 3}
    greek_text_tlg\JoannesPhiloponus\Simplified_InAristotetelisMeteorologicorumLibrumPrimumCommentarium.txt {'ΑΛΛΗΣΤΗΣΑΝΩΘΕΝΘΕΡΜΤΗΤΟΣΑΤΜΙΔΟΜΕΝΟΝΦΡΕΤΑΙ': 3, 'ΔΥΝΑΤΟΝΔΕΤΟΑΙΤΑΙΗΣΓΕΝΣΕΩΣΚΑΙΤΗΣΦΘΟΡΑΣ': 3}
    greek_text_tlg\Libanius\Simplified_Epistulae1-839.txt {'ΕΜΟΥΙΑΠΦΕΥΓΑΧΕΙΡΑΣΛΥΠΣΑΣΜΕΝΟΥΔΝΑΟΥΔΝ': 3, 'ΚΑΙΙΚΛΗΧΡΥΣΗΑΦΡΟΔΤΗΚΑΙΟΙΣΕΚΣΜΗΣΕ': 3}
    greek_text_tlg\Libanius\Simplified_OratioI.txt {'ΗΔΙΚΗΜΝΟΝΔΕΑΠΕΡΡΙΜΜΝΟΝΠΕΡΙΟΡΑΣ': 2}
    greek_text_tlg\ScholiaInHomerum\Simplified_ScholiaInIliadum.txt {'ΣΙΑΛΟΙΟΡΑΧΙΝΤΕΘΑΛΥΙΑΝΑΛΟΙΦΗΕΥΤΡΑΦΟΥΣ': 4}
    greek_text_tlg\TheonSmyrnaeus\Simplified_DeUtilitateMathematicae.txt {'ΧΙΛΙΟΚΤΑΚΟΣΙΟΥΔΟΗΚΟΝΤΑΠΛΑΣΟΝΑ': 2}
    

For a small explanation: [Aristophanes](https://en.wikipedia.org/wiki/Aristophanes) was a Greek comic playwright and a word expert of a kind. Mathematical texts are also filled with long compoud words for fractions for example.

So thats all for the Greek corpora processing and basic statistics. One could further investigate the basic stats, categorize and compare individual texts as well.

## The [MIT](http://choosealicense.com/licenses/mit/) License

Copyright &copy; 2018 Marko Manninen
