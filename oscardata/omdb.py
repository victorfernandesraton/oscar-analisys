import concurrent.futures
import logging

import httpx
import pandas as pd


class OmdbExtractor:
    """
    Extracts movie metadata from OMDb API.
    """

    def __init__(self, api_keys: list[str]):
        self.api_keys = api_keys
        self.current_key_index = 0

    def _get_api_key(self):
        """Cycles through the available API keys."""
        key = self.api_keys[self.current_key_index]
        self.current_key_index = (self.current_key_index + 1) % len(self.api_keys)
        return key

    def search_movie_metadata(self, name: str, year: str | int) -> dict | None:
        """
        Searches for movie metadata based on name and year.

        Args:
            name: The name of the movie.
            year: The release year of the movie.

        Returns:
            A dictionary containing the movie metadata.

        Raises:
            httpx.HTTPStatusError: If the OMDb API request fails.
        """
        request = httpx.get(
            "http://www.omdbapi.com/",  # Added trailing slash for consistency
            params={"apikey": self._get_api_key(), "t": name, "y": year},
        )
        if request.status_code != 200:
            logging.error(f"Request for {name}/{year} not go well")
            return None
        data = request.json()
        box_office = data.get("BoxOffice", "N/A")
        cost: float | None = None  # Renamed 'coast' to 'cost'
        if box_office != "N/A":
            box_office = box_office.replace("$", "").replace(",", "")
            try:
                cost = float(box_office)
            except ValueError:
                pass  # Keep cost as None if conversion fails

        director = data.get("Director")
        runtime = data.get("Runtime")  # Renamed 'total_time' to 'runtime'
        imdb_id = data.get("imdbID")
        return {
            "Movie": name,
            "Release": year,
            "Cost": cost,  # Use 'cost'
            "Director": director,
            "Duration": runtime,  # Use 'runtime'
            "IMDB": imdb_id,
        }

    def execute(self, df: pd.DataFrame) -> pd.DataFrame:
        self.current_key_index = 0
        """
        Executes the metadata search for multiple movies in a DataFrame.

        Args:
            df: A Pandas DataFrame containing 'Film' and 'Release' columns.

        Returns:
            A DataFrame containing the movie metadata.
        """
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = [
                executor.submit(self.search_movie_metadata, name, year)
                for name, year in zip(df["Movie"], df["Release"])
            ]
            results = [
                future.result()
                for future in concurrent.futures.as_completed(futures)
                if future.result() is not None
            ]
        return pd.DataFrame(results)
