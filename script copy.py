import sqlite3 as sqlite
import csv
import re
from bs4 import BeautifulSoup
import json
import urllib2
import time


script_gender = []
script_imdb = []
imdb_metadata = []

with open("character_list5.csv", "rb") as csv_gender:
    reader_gender = csv.reader(csv_gender, delimiter=',')
    for l_gender in reader_gender:
        script_gender.append((l_gender[0], l_gender[3]))
    script_gender = script_gender[1:]

with open("meta_data7.csv", "rb") as csv_imdb:
    reader_imdb = csv.reader(csv_imdb, delimiter=",")
    for l_imdb in reader_imdb:
        script_imdb.append((l_imdb[0], l_imdb[1]))
    script_imdb = script_imdb[1:]

count_gender_dict = {}
for tup in script_gender:
    if tup[0] not in count_gender_dict:
        count_gender_dict[tup[0]] = [tup[1]]
    else:
        count_gender_dict[tup[0]].append(tup[1])

# def deter_gender(l):
#     char_num = len(l)
#     female_num = l.count("f")
#     if float(female_num) / char_num >= 0.6:
#         return "f"
#     else:
#         return "m"

def deter_gender(l):
    char_num = len(l)
    female_num = l.count("f")
    male_num = l.count("m")
    if float(female_num) / char_num > 0.5:
        return "f"
    elif float(male_num) / char_num > 0.5:
        return "m"
    else:
        return "n"

for script_id in count_gender_dict:
    count_gender_dict[script_id] = deter_gender(count_gender_dict[script_id])

script_movie_gender = []
for k in count_gender_dict:
    script_movie_gender.append((k, count_gender_dict[k]))


with sqlite.connect(r'movie2.db') as con:
    con.text_factory = str
    cur = con.cursor()
    cur.execute("CREATE TABLE script_gender(script_id text, gender text)")
    cur.executemany("INSERT INTO script_gender VALUES(?, ?)", script_movie_gender)

    cur.execute("CREATE TABLE script_imdb(script_id text, imdb_id text)")
    cur.executemany("INSERT INTO script_imdb VALUES (?, ?)", script_imdb)

    cur.execute("SELECT script_gender.gender, script_imdb.imdb_id FROM script_imdb JOIN script_gender ON (script_imdb.script_id = script_gender.script_id)")
    con.commit()
    rows = cur.fetchall()


movies = []
for line in open('data.json', 'r'):
    movies.append(json.loads(line))

n_movies = zip(rows, movies)
n_mov_lst = []
for movie in n_movies:
    n_mov_lst.append([movie[0][1], movie[0][0]] + movie[1][2:])

print n_mov_lst[:5]
movies_women = [m for m in movies if m[1] == u"f"]
movies_men = [mo for mo in movies if mo[1] == u"m"]
movies_neu = [mov for mov in movies if mov[1] == u"n"]

def get_keywords(lst):
    mov_words = []
    for ele in lst:
        if ele[6]:
            mov_words += ele[6]
    return mov_words

women_keywords = get_keywords(movies_women)
men_keywords = get_keywords(movies_men)
with open("women_keywords_3.txt", "w") as foutfile, open("men_keywords_3.txt", "w") as moutfile:
    foutfile.write("\n".join(women_keywords))
    moutfile.write("\n".join(men_keywords))

print len(movies_men)
print len(movies_neu)