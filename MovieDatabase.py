import sqlite3
import os
import csv
import re
from typing import Union

class MovieDatabase():
    def __init__(self):
        self.__connection = sqlite3.connect("movies.db")
        self.__create_tables()

    def __split_title_year(self, raw_title: str) -> tuple:
        match = re.search(r"\((\d{4})\)\s*$", raw_title)

        if match:
            year = int(match.group(1))
            title = raw_title[:match.start()].strip()
            return title, year

        return raw_title, None

    def get_movies_same_genre(self, movie_id: int) -> list:
        cursor = self.__connection.cursor()
        cursor.execute("SELECT genres FROM movies WHERE movieId = ?", (movie_id,))
        row = cursor.fetchone()
        if not row or not row[0]:
            return []

        genres_field = row[0]
        genres_list = [g for g in genres_field.split("|") if g and g != "(no genres listed)"]
        if not genres_list:
            return []

        clauses = []
        params = []
        for g in genres_list:
            clauses.append("genres LIKE ?")
            params.append(f"%{g}%")

        params.append(movie_id)
        query = f"SELECT movieId, title, year, genres FROM movies WHERE ({' OR '.join(clauses)}) AND movieId != ?"
        cursor.execute(query, params)
        return cursor.fetchall()

    def get_movieid_from_name(self, movie_name: str) -> int:
        cursor = self.__connection.cursor()
        cursor.execute("SELECT movieId FROM movies WHERE title LIKE ? COLLATE NOCASE LIMIT 1", (f"%{movie_name}%",))
        row = cursor.fetchone()
        return row[0] if row else None

    def get_movies_by_year(self, year: int) -> list:
        cursor = self.__connection.cursor()
        cursor.execute("SELECT movieId, title, year, genres FROM movies WHERE year = ? ORDER BY title", (year,))
        return cursor.fetchall()
    
    def get_movies_by_rating(self, rating: float) -> list:
        cursor = self.__connection.cursor()
        cursor.execute("""
            SELECT m.movieId, m.title, m.year, m.genres
            FROM movies m
            JOIN ratings r ON m.movieId = r.movieId
            WHERE r.rating >= ?
            GROUP BY m.movieId
            ORDER BY AVG(r.rating) DESC
        """, (rating,))
        return cursor.fetchall()
    
    def get_full_movie_info(self, movie_ids: Union[list[int], int]) -> list[tuple]:
        if not movie_ids:
            return []
        if isinstance(movie_ids, int):
            movie_ids = [movie_ids]
        cursor = self.__connection.cursor()
        placeholders = ",".join("?" for _ in movie_ids)
        query = f"""
            SELECT m.movieId, m.title, m.year, m.genres,
                   COALESCE(GROUP_CONCAT(DISTINCT t.tag, '|'), '') AS tags
            FROM movies m
            LEFT JOIN tags t ON m.movieId = t.movieId
            WHERE m.movieId IN ({placeholders})
            GROUP BY m.movieId
        """
        cursor.execute(query, movie_ids)
        rows = cursor.fetchall()

        result = []
        for movieId, title, year, genres, tags in rows:
            tag_list = tags.split('|') if tags else []
            result.append((movieId, title, year, genres, tag_list))

        return result

    def load_data(self, data_path: str, delete_data: bool = True) -> None:
        cursor = self.__connection.cursor()
        if delete_data:
            cursor.execute("DELETE FROM movies")
            cursor.execute("DELETE FROM ratings")
            cursor.execute("DELETE FROM tags")
            self.__connection.commit()

        with open(os.path.join(data_path, "movies.csv"), encoding="utf-8") as file:
            reader = csv.DictReader(file)
            movies_data = []
            for row in reader:
                movie_id = int(row["movieId"])
                raw_title = row["title"]
                title, year = self.__split_title_year(raw_title)
                genres = row["genres"]
                movies_data.append((movie_id, title, year, genres))

        cursor.executemany(
            "INSERT INTO movies (movieId, title, year, genres) VALUES (?, ?, ?, ?)",
            movies_data
        )
        self.__connection.commit()

        with open(os.path.join(data_path, "ratings.csv"), encoding="utf-8") as file:
            reader = csv.DictReader(file)
            ratings_data = [
                (
                    int(row["userId"]),
                    int(row["movieId"]),
                    float(row["rating"])
                )
                for row in reader
            ]

        cursor.executemany(
            "INSERT INTO ratings (userId, movieId, rating) VALUES (?, ?, ?)",
            ratings_data
        )
        self.__connection.commit()

        with open(os.path.join(data_path, "tags.csv"), encoding="utf-8") as file:
            reader = csv.DictReader(file)
            tags_data = [
                (
                    int(row["userId"]),
                    int(row["movieId"]),
                    row["tag"]
                )
                for row in reader
            ]

        cursor.executemany(
            "INSERT INTO tags (userId, movieId, tag) VALUES (?, ?, ?)",
            tags_data
        )
        self.__connection.commit()

    def __create_tables(self) -> None:
        self.__create_movies_table()
        self.__create_ratings_table()
        self.__create_tags_table()

    def __create_movies_table(self) -> None:
        cursor = self.__connection.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS movies (
                movieId INTEGER PRIMARY KEY,
                title TEXT,
                year INTEGER,
                genres TEXT
            )
        """)
        self.__connection.commit()

    def __create_ratings_table(self) -> None:
        cursor = self.__connection.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ratings (
                userId INTEGER,
                movieId INTEGER,
                rating REAL
            )
        """)
        self.__connection.commit()

    def __create_tags_table(self) -> None:
        cursor = self.__connection.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tags (
                userId INTEGER,
                movieId INTEGER,
                tag TEXT
            )
        """)
        self.__connection.commit()
