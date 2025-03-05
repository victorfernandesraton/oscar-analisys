# Implementando um dataframe gigantesco onde
from io import StringIO

import httpx
import pandas as pd
from bs4 import BeautifulSoup
from lxml import etree


class WikipediaExtractor:
    def __init__(
        self,
        ceremony_table_xpath="//*[@id='Ceremonies']/../following-sibling::table[1]",
        wikipedia_domain="https://en.wikipedia.org",
    ):
        self.ceremony_table_xpath = ceremony_table_xpath
        self.wikipedia_domain = wikipedia_domain

    def get_ceremonies(self) -> pd.DataFrame:
        request = httpx.get(
            f"{self.wikipedia_domain}/wiki/List_of_Academy_Awards_ceremonies"
        )
        request.raise_for_status()

        cerimony_table_bs4 = BeautifulSoup(request.text, "html.parser")

        cerimony_table_src = cerimony_table_bs4.select(
            "#mw-content-text > div.mw-content-ltr.mw-parser-output table"
        )

        cerimony_list_df = pd.read_html(StringIO(str(cerimony_table_src[1])))[0]

        cerimony_list_df.head()

        cerimony_list_df["url"] = cerimony_list_df["#"].apply(
            lambda x: f"https://en.wikipedia.org/wiki/{x}_Academy_Awards"
        )

        return cerimony_list_df

    def get_movies_all(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        movies_in_ceremony_list = list()
        for i, row in dataframe.iterrows():
            request = httpx.get(row["url"])
            request.raise_for_status()

            tree = etree.HTML(request.text)

            categories_in_ceremony_table = tree.xpath(
                "//*[@id='Winners_and_nominees']/../following-sibling::table[1]"
            )[0]
            for tr in categories_in_ceremony_table.xpath(".//tbody/tr/td"):
                winner = tr.xpath(".//ul/li/b/i/a")
                if not winner:
                    winner = tr.xpath(".//ul/li/i/b/a")
                if not winner:
                    continue
                category_name = tr.xpath(".//div/b/a")
                if not category_name:
                    category_name = tr.xpath(".//div/b")
                category_name = category_name[-1].text.strip()
                winner = winner[0].text.strip()
                movies_in_ceremony_list.append(
                    {
                        "#": row["#"],
                        "Date": row["Date"],
                        "Category": category_name,
                        "Winner": True,
                        "Movie": winner,
                        "Wikipedia_URL": row["url"],
                    }
                )
                others = list(
                    map(lambda x: x.text.strip(), tr.xpath(".//ul/li/ul/li/i/a"))
                )
                for other in others:
                    movies_in_ceremony_list.append(
                        {
                            "#": row["#"],
                            "Date": row["Date"],
                            "Category": category_name,
                            "Winner": False,
                            "Movie": other,
                            "Wikipedia_URL": row["url"],
                        }
                    )
        return pd.DataFrame(movies_in_ceremony_list)
