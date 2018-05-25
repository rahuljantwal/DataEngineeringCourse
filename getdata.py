import requests
from bs4 import BeautifulSoup
import time
from imdb import IMDb
import pandas as pd


urls = ['https://en.wikipedia.org/wiki/List_of_fiction_works_made_into_feature_films_(0%E2%80%939,_A%E2%80%93C)',
    'https://en.wikipedia.org/wiki/List_of_fiction_works_made_into_feature_films_(D%E2%80%93J)',
    'https://en.wikipedia.org/wiki/List_of_fiction_works_made_into_feature_films_(K%E2%80%93R)',
    'https://en.wikipedia.org/wiki/List_of_fiction_works_made_into_feature_films_(S%E2%80%93Z)']

#soup = BeautifulSoup(website_url,'lxml')

def create_book_film_table(links):
    ls_book = list()
    ls_films = list()
    for url in links:
        #website_url = requests.get(url).text
        soup = BeautifulSoup(requests.get(url).text,'lxml')
        tbl = soup.find_all('table',{'class':'wikitable'})   
        for i in range(len(tbl)):
            contents = [item.get_text() for item in tbl[i].find_all('td')]
            contents = list(filter(lambda a: a != 'Bicho de Sete Cabeças (The Great Brain Storm) (2001)', contents))
            for j in range(0,len(contents),2):
                ls_book.append(contents[j])
                ls_films.append(contents[j+1])
    return ls_book, ls_films


ls_book, ls_films = create_book_film_table(urls)
#book_film_df = pd.concat([pd.DataFrame(ls_book, columns=["Books"]),pd.DataFrame(ls_films, columns=["Films"])],axis=1)

book_film_df = pd.DataFrame([film.split("\n") for film in ls_films])[0]


# create an instance of the IMDb class
ia = IMDb()

def create_mappings(info,mat,mov,category):
    ls = list()
    if category == 'person':
        for i in range(len(mov[info])):
            ls.append((mat.movieID,
                   [person.personID for person in mov[info]][i],
                   [person["name"] for person in mov[info]][i]))
        return ls
    if category == 'entity':
        for i in range(len(mov[info])):
            ls.append((mat.movieID,mov[info][i]))
        return ls

def create_people_list(info):
    movie_people_list = list()
    for movie in list(pd.DataFrame([film.split("\n") for film in ls_films])[0])[0:10]:
        try:
            mat = ia.search_movie(movie)[0]
            mov = ia.get_movie(mat.movieID)
            movie_people_list.append(create_mappings(info,mat,mov,'person'))
        except IndexError:
            print(movie)
        except KeyError:
            print(movie)
        except OSError:
            print(movie)
        except gaierror:
            print(movie)
    movie_people_list = [item for sublist in movie_people_list for item in sublist]
    return movie_people_list

def create_entity_list(info):
    movie_entity_list = list()
    for movie in list(pd.DataFrame([film.split("\n") for film in ls_films])[0]):
        try:
            mat = ia.search_movie(movie)[0]
            mov = ia.get_movie(mat.movieID)
            movie_entity_list.append(create_mappings(info,mat,mov,'entity'))
        except IndexError:
            print(movie)
        except KeyError:
            print(movie)
        except OSError:
            print(movie)
        except gaierror:
            print(movie)
    movie_entity_list = [item for sublist in movie_entity_list for item in sublist]
    return movie_entity_list

movie_directors_list = create_people_list('directors')

#movie_producers_list = create_people_list('producers')

#movie_genres_list = create_entity_list('genres')

#movie_rating_list = create_entity_list('rating')

#movie_runtimes_list = create_entity_list('runtimes')

#movie_date_list = create_entity_list('original air date')

directors_df = pd.DataFrame(movie_directors_list, columns=["movieID","personID","Name"])
directors_df.to_csv("directors.csv")