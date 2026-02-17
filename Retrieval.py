from MovieDatabase import MovieDatabase
from Intent import Intent
import re

class Retrieval():
    def __init__(self, movie_database: MovieDatabase):
        self.__movie_database = movie_database

    def __normalize(self, text: str) -> str:
        return text.lower().strip()

    def __define_intent(self, user_input: str) -> Intent:
        text = self.__normalize(user_input)

        similar_keywords = [
            "similar",
            "like",
            "movies like",
        ]
        if any(k in text for k in similar_keywords):
            return Intent.SIMILAR_MOVIES

        year_match = re.search(r"\b(19\d{2}|20\d{2})\b", text)
        recommend_words = ["recommend", "suggest"]

        if year_match and any(w in text for w in recommend_words):
            return Intent.RECOMMEND_BY_YEAR

        return Intent.GENERAL


    def __get_movie_name(self, input: str) -> str:
        match = re.search(r"\b[A-Z][\w'’-]*", input, re.UNICODE)
        return match.group(0) if match else ''

    def __general(self, input: str):
        movie = self.__get_movie_name(input)
        movie_id = None
        if movie:
            movie_id = self.__movie_database.get_movieid_from_name(movie)
        else:
            raise ValueError("No movie name found in input for general intent.")
        general_info = self.__movie_database.get_full_movie_info(movie_id)
        return {
            "intent": Intent.GENERAL,
            "movie": movie,
            "general_infos": general_info
        }
    
    def __similar_movies(self, input: str):
        movie = self.__get_movie_name(input)
        if movie:
            movie_id = self.__movie_database.get_movieid_from_name(movie)
        else:
            raise ValueError("No movie name found in input for similar movies intent.")
        similar_movies = self.__movie_database.get_movies_same_genre(movie_id)
        return {
            "intent": Intent.SIMILAR_MOVIES,
            "movie": movie,
            "similar_movies": similar_movies
        }
    
    def __recommend_by_year(self, input: str):
        match = re.search(r"\b(19\d{2}|20\d{2})\b", input)
        year = int(match.group(0)) if match else None
        if year is None:
            raise ValueError("No valid year found in input for recommend by year intent.")
        movies_by_year = self.__movie_database.get_movies_by_year(year)
        return {
            "intent": Intent.RECOMMEND_BY_YEAR,
            "year": year,
            "movies_by_year": movies_by_year
        }

    def process_input(self, input: str) -> dict:
        intent = self.__define_intent(input)
        if intent == Intent.SIMILAR_MOVIES:
            return self.__similar_movies(input)
        elif intent == Intent.RECOMMEND_BY_YEAR:
            return self.__recommend_by_year(input)
        else:
            return self.__general(input)