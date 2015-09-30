import media
import fresh_tomatoes

#A compilation of my favorite movies
confessions = media.Movie("Confessions",
    "http://ia.media-imdb.com/images/M/MV5BMTY1NDQ1MzkzNF5BMl5BanBnXkFtZTcwNjYwNzg1NA@@._V1__SX1379_SY703_.jpg",
    "https://www.youtube.com/watch?v=Vnws8ZymxME",
    "thriller, psychological, drama")
castaway_on_the_moon = media.Movie("Castaway on the Moon",
    "http://ia.media-imdb.com/images/M/MV5BMTk3MTQ3NzU0MF5BMl5BanBnXkFtZTgwNTM0MTE0MjE@._V1__SX1379_SY703_.jpg",
    "https://www.youtube.com/watch?v=061ZyqHhdCo",
    "drama, comedy")
pulp_fiction = media.Movie("Pulp Fiction",
    "http://ia.media-imdb.com/images/M/MV5BMTkxMTA5OTAzMl5BMl5BanBnXkFtZTgwNjA5MDc3NjE@._V1__SX1379_SY703_.jpg",
    "https://www.youtube.com/watch?v=s7EdQ4FqbhY",
    "crime, thriller")
the_matrix = media.Movie("The Matrix",
    "http://ia.media-imdb.com/images/M/MV5BMTkxNDYxOTA4M15BMl5BanBnXkFtZTgwNTk0NzQxMTE@._V1__SX1379_SY703_.jpg",
    "https://www.youtube.com/watch?v=m8e-FF8MsqU",
    "scifi, action, adventure")
my_sassy_girl = media.Movie("My Sassy Girl",
    "http://ia.media-imdb.com/images/M/MV5BMjM2NTYxMTE3OV5BMl5BanBnXkFtZTgwNDgwNjgwMzE@._V1__SX1379_SY703_.jpg",
    "https://www.youtube.com/watch?v=W_P5ANb8LQI",
    "comedy, romance")
fight_club = media.Movie("Fight Club",
    "http://ia.media-imdb.com/images/M/MV5BMjIwNTYzMzE1M15BMl5BanBnXkFtZTcwOTE5Mzg3OA@@._V1__SX1379_SY703_.jpg",
    "https://www.youtube.com/watch?v=SUXWAEX2jlg",
    "psychological, thriller")

movies = [confessions,castaway_on_the_moon,pulp_fiction,the_matrix,my_sassy_girl,fight_club]

#call function from fresh_tomatoes to load the website
fresh_tomatoes.open_movies_page(movies)