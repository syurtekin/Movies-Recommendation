# TASK 1
######################################


import pandas as pd
pd.set_option('display.max_columns', 20)

movie = pd.read_csv('datasets/movie.csv')
movie.shape
rating = pd.read_csv('datasets/rating.csv')
rating.shape
df = movie.merge(rating, how="left", on="movieId")
df.head()


df.shape

df["title"].nunique()

df["title"].value_counts().head()

comment_counts = pd.DataFrame(df["title"].value_counts())
rare_movies = comment_counts[comment_counts["title"] <= 1000].index
common_movies = df[~df["title"].isin(rare_movies)]

common_movies.shape
common_movies["title"].nunique()

user_movie_df = common_movies.pivot_table(index=["userId"], columns=["title"], values="rating")

user_movie_df.shape
user_movie_df.head(10)
user_movie_df.columns

len(user_movie_df.columns)
common_movies["title"].nunique()

# TASK 2
# Öneri yapılacak kullanıcının izlediği filmleri belirleyiniz.

random_user = int(pd.Series(user_movie_df.index).sample(1, random_state=45).values)
random_user_df = user_movie_df[user_movie_df.index == random_user]

#kullanıcının izlediği filmler
# USER ID 28941
movies_watched = random_user_df.columns[random_user_df.notna().any()].tolist()
user_movie_df.loc[user_movie_df.index == random_user, user_movie_df.columns == "Jurassic Park (1993)"]
len(movies_watched) # 33 tane film izlemiş

# TASK 3
pd.set_option('display.max_columns', 5)
movies_watched_df = user_movie_df[movies_watched]
movies_watched_df.head()

movies_watched_df.shape # 33 tane filmden en az bir tane izleyenlerde dahil.

user_movie_count = movies_watched_df.T.notnull().sum() #her bir kullanıcı için kullanıcı kaç tane film izlemiş onu yakaladık.

user_movie_count = user_movie_count.reset_index()

user_movie_count.columns = ["userId", "movie_count"]

user_movie_count[user_movie_count["movie_count"] > 20].sort_values("movie_count", ascending=False)

user_movie_count[user_movie_count["movie_count"] == 33].count()

perc = len(movies_watched) * 60 / 100
users_same_movies = user_movie_count[user_movie_count["movie_count"] > perc]["userId"] #kullanıcı ile %60  aynı filmi izleyen kişilerin idleri
#4139 kişi

# TASK 4
final_df = pd.concat([movies_watched_df[movies_watched_df.index.isin(users_same_movies.index)],random_user_df[movies_watched]])
final_df.shape
final_df.T.corr()

corr_df = final_df.T.corr().unstack().sort_values().drop_duplicates()
corr_df = pd.DataFrame(corr_df, columns=["corr"])

corr_df.index.names = ['user_id_1', 'user_id_2']

corr_df = corr_df.reset_index() #user 1 kullanıcı user 2 diğer kullanıcılar.

top_users = corr_df[(corr_df["user_id_1"] == random_user) & (corr_df["corr"] >= 0.65)][
    ["user_id_2", "corr"]].reset_index(drop=True) #kullanıcı ile 65 korelasyona sahip olanlar

top_users = top_users.sort_values(by='corr', ascending=False) # kullanıcı ile en fazla corelasyona sahip olanlar

top_users.rename(columns={"user_id_2": "userId"}, inplace=True)

rating = pd.read_csv('../input/movielense20m/rating.csv')
top_users_ratings = top_users.merge(rating[["userId", "movieId", "rating"]], how='inner')

# TASK 5
top_users_ratings['weighted_rating'] = top_users_ratings['corr'] * top_users_ratings['rating'] # hem korelasyon hem de rating açısından değerlendirebilmek için

top_users_ratings.groupby('movieId').agg({"weighted_rating": "mean"}) #filmlere göre tekilleştirildi

recommendation_df = top_users_ratings.groupby('movieId').agg({"weighted_rating": "mean"})
recommendation_df = recommendation_df.reset_index()

movies_to_be_recommend = recommendation_df[recommendation_df["weighted_rating"] > 4].sort_values("weighted_rating", ascending=False)

# TASK 6
#user based
movie = pd.read_csv('../input/movielense20m/movie.csv')
movies_to_be_recommend.merge(movie[["movieId", "title"]])["title"].head()
# 0           Happy Gilmore (1996)
# 1               Labyrinth (1986)
# 2    Boondock Saints, The (2000)
# 3                  Snatch (2000)
# 4                 Frailty (2001)
# Name: title, dtype: object

user = 28941
movie = pd.read_csv('../input/movielense20m/movie.csv')
rating = pd.read_csv('../input/movielense20m/rating.csv')
movie_id = rating[(rating["userId"] == user) & (rating["rating"] == 5.0)].sort_values(by="timestamp", ascending=False)["movieId"][
0:1].values[0]
#movieid = 7
#item based
movie_name = movie[movie['movieId'] == movie_id]['title'].values[0]
movie_name = user_movie_df[movie_name]
movies_from_item_based = user_movie_df.corrwith(movie_name).sort_values(ascending=False)
movies_from_item_based[1:6].index

# Index(['Intouchables (2011)', 'Father of the Bride (1991)',
#        'Anna and the King (1999)', 'Runaway Bride (1999)',
#        'Phantom of the Opera, The (2004)'],
#       dtype='object', name='title')
