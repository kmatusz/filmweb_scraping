# This script contains data preprocessing after running scraper.
# Created by Kamil Matuszelański

import pandas as pd

movies = pd.read_csv('data/movies.csv', dtype='object')


movies['user_rated_date'] = pd.to_datetime(movies.rename(columns={'user_rated_day':'Day', 'user_rated_month':'Month', 'user_rated_year':'Year'})[['Day','Month','Year']])

movies = movies.drop(['user_rated_day', 'user_rated_month', 'user_rated_year'], axis = 1)

movies['movie_rating_avg'] = movies.movie_rating_avg.apply(lambda x: float(x.replace(',', '.').replace(' ', '')))
movies['movie_rating_no'] = movies.movie_rating_no.apply(lambda x: float(x.replace(',', '.').replace(' ', '')))

movies['user_rating'] = movies.user_rating.astype(int)

movies['user_name'] = movies.user_url.apply(lambda x: x.replace('https://www.filmweb.pl/user/', '').split('/')[0])
movies['user_page'] = movies.user_url.apply(lambda x: int(x.replace('https://www.filmweb.pl/user/', '').split('/')[1].replace('films?page=', '')))
movies = movies.drop(['user_url'], axis = 1)

movies.to_csv('data/movies_cleaned.csv')

print('successful!')