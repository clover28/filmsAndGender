import sqlite3 as sqlite
import csv
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

# with open("meta_data7.csv", "rb") as csv_imdb:
#     reader_imdb = csv.reader(csv_imdb, delimiter=",")
#     for l_imdb in reader_imdb:
#         script_imdb.append((l_imdb[0], l_imdb[1]))
#     script_imdb = script_imdb[1:]

count_gender_dict = {}
for tup in script_gender:
    if tup[0] not in count_gender_dict:
        count_gender_dict[tup[0]] = [tup[1]]
    else:
        count_gender_dict[tup[0]].append(tup[1])

def deter_gender(l):
    char_num = len(l)
    female_num = l.count("f")
    if float(female_num) / char_num >= 0.6:
        return "f"
    else:
        return "m"

for script_id in count_gender_dict:
    count_gender_dict[script_id] = deter_gender(count_gender_dict[script_id])

script_movie_gender = []
for k in count_gender_dict:
    script_movie_gender.append((k, count_gender_dict[k]))


with sqlite.connect(r'movie.db') as con:
    con.text_factory = str
    cur = con.cursor()
    # cur.execute("CREATE TABLE script_gender(script_id text, gender text)")
    # cur.executemany("INSERT INTO script_gender VALUES(?, ?)", script_movie_gender)
    #
    # cur.execute("CREATE TABLE script_imdb(script_id text, imdb_id text)")
    # cur.executemany("INSERT INTO script_imdb VALUES (?, ?)", script_imdb)

    cur.execute("SELECT script_gender.gender, script_imdb.imdb_id FROM script_imdb JOIN script_gender ON (script_imdb.script_id = script_gender.script_id)")
    con.commit()

    rows = cur.fetchall()

class movie:
    def __init__(self, joined_data):
        self.gender = joined_data[0]
        self.imdb_id = joined_data[1]

    def fetch_content(self):
        response = urllib2.urlopen('http://www.imdb.com/title/'+ self.imdb_id)
        soup = BeautifulSoup(response.read())
        try:
            title = soup.h1.contents[0]
        except:
            title = None
        try:
            year_span = soup.h1.contents[1]
            year = year_span.find("a").string
        except:
            year = None
        try:
            rating = float(soup.find('span', itemprop='ratingValue').string)
        except:
            rating = None
        try:
            keywords_div = soup.find("div", itemprop = "keywords")
            keywords_spans = keywords_div.find_all("span")
            keywords = []
            for keyword in keywords_spans:
                keywords.append(keyword.string)
            keywords = [x for x in keywords if x != u"|"]
        except:
            keywords = None
        try:
            country = soup.find("h4", string = "Country:").next_sibling.next_sibling.string
        except:
            country = None
        return self.imdb_id, self.gender, title, year, country, rating, keywords


# movie_full_data = []
# for row in rows:
#     try:
#         movie_full_data.append(movie(row).fetch_content())
#         with open("data.json", "a") as datafile:
#             datafile.write(json.dumps(movie(row).fetch_content())+'\n')
#         time.sleep(5)
#     except:
#         pass

movies = []
for line in open('data.json', 'r'):
    movies.append(json.loads(line))

movies_women = [m for m in movies if m[1] == u"f"]
movies_men = [mo for mo in movies if mo[1] == u"m"]

def get_keywords(lst):
    mov_words = []
    for ele in lst:
        if ele[6]:
            mov_words += ele[6]
    return mov_words

women_keywords = get_keywords(movies_women)
men_keywords = get_keywords(movies_men)

def count_frequency(lst):
    dict = {}
    for word in lst:
        if word not in dict:
            dict[word] = 1
        else:
            dict[word] += 1
    return_lst = []
    for k in dict:
        return_lst.append((k, dict[k]))
    return_lst = sorted(return_lst, key=lambda x: x[1], reverse=True)
    return return_lst

women_top_ten = count_frequency(women_keywords)[:5]
men_top_ten = count_frequency(men_keywords)[:5]
print women_top_ten
print men_top_ten
w_top_ten = sorted([z[0] for z in women_top_ten])
m_top_ten = sorted([i[0] for i in men_top_ten])


def count_by_year(w_top_ten, movies_women):
    w_year_frequency = {}
    for w_movie in movies_women:
        if w_movie[3] not in w_year_frequency:
            w_year_frequency[w_movie[3]] = {}
        for w_word in w_top_ten:
            if w_movie[6]:
                if w_word in w_movie[6]:
                    if w_word not in w_year_frequency[w_movie[3]]:
                        w_year_frequency[w_movie[3]][w_word] = 1
                    else:
                        w_year_frequency[w_movie[3]][w_word] += 1
    for k in w_year_frequency:
        for w_wo in w_top_ten:
            if w_wo not in w_year_frequency[k]:
                w_year_frequency[k][w_wo] = 0
    return w_year_frequency

# for w_word in w_top_ten:
#     w_year_frequency[w_word] = {}
#     for w_movie in movies_women:
#         if w_movie[6]:
#             if w_word in w_movie[6]:
#                 if w_movie[3] not in w_year_frequency[w_word]:
#                     w_year_frequency[w_word][w_movie[3]] = 1
#                 else:
#                     w_year_frequency[w_word][w_movie[3]] += 1
# print count_by_year(w_top_ten, movies_women)
# print count_by_year(m_top_ten, movies_men)

w_year_dict = count_by_year(w_top_ten, movies_women)
m_year_dict = count_by_year(m_top_ten, movies_men)

print w_year_dict
print m_year_dict

w_header = ["year"] + w_top_ten
m_header = ["year"] + m_top_ten
print m_header

def out_year(w_year_dict, w_top_ten):
    w_out_year_lst = []
    for year in w_year_dict:
        y = year
        x0 = w_year_dict[year][w_top_ten[0]]
        x1 = w_year_dict[year][w_top_ten[1]]
        x2 = w_year_dict[year][w_top_ten[2]]
        x3 = w_year_dict[year][w_top_ten[3]]
        x4 = w_year_dict[year][w_top_ten[4]]
        w_out_year_lst.append([y, x0, x1, x2, x3, x4])
    w_out_year_lst = sorted(w_out_year_lst, key=lambda j:j[0])
    return w_out_year_lst

with open("w_year_lst.txt", "w") as w_out_year:
    w_out_year.write(str(w_header) + ",\n")
    for w_year in out_year(w_year_dict, w_top_ten):
        w_out_year.write(str(w_year)+",\n")

with open("m_year_lst.txt", "w") as m_out_year:
    m_out_year.write(str(m_header) + ",\n")
    for m_year in out_year(m_year_dict, m_top_ten):
        m_out_year.write(str(m_year)+",\n")

