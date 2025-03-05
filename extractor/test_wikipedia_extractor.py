import unittest

from extractor import WikipediaExtractor


class TestWikipediaExtractor(unittest.TestCase):
    def setUp(self):
        """Configura o extractor antes de cada teste."""
        self.extractor = WikipediaExtractor()

    def test_get_ceremonies(self):
        df = self.extractor.get_ceremonies()

        self.assertEqual(
            df.columns.to_list(),
            [
                "#",
                "Date",
                "Best Picture",
                "U.S. viewers (millions)",
                "HH Rating",
                "Host(s)",
                "Producer(s)",
                "Venue",
                "Network",
                "url",
            ],
        )
        self.assertGreater(len(df), 0)

    def test_get_movies(self):
        df = self.extractor.get_ceremonies()
        movies = self.extractor.get_movies_all(df[-3:])

        self.assertGreater(len(movies), 0)
        self.assertEqual(
            movies.columns.to_list(),
            ["#", "Date", "Category", "Winner", "Movie", "Wikipedia_URL"],
        )


if __name__ == "__main__":
    unittest.main()
