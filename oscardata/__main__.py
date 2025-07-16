if __name__ == "__main__":
    import logging
    from datetime import datetime

    import pandas as pd
    from decouple import config
    from omdb import OmdbExtractor
    from wikipedia import WikipediaExtractor

    logging.basicConfig(level=logging.INFO)

    omdb_api_keys = config("OMDB_API_KEY", "").split(";")

    logging.info(f"Total de chames OMDB {len(omdb_api_keys)}")

    # Initialize extractors
    wikipedia_extractor = WikipediaExtractor()
    omdb_extractor = OmdbExtractor(api_keys=omdb_api_keys)

    # Extract ceremonies
    ceremonies = wikipedia_extractor.get_ceremonies()
    ceremonies = ceremonies.tail(40)
    # ceremonies = pd.read_csv("ceremony_base.csv", sep=";")

    ceremonies.to_csv("ceremony_base.csv")

    winners = wikipedia_extractor.get_movies_all(ceremonies)

    # winners = pd.read_csv("nominated_all.csv", sep=";")

    winners.to_csv("winners_base.csv")

    # Enrich winners data with OMDb data
    logging.info(winners.columns)

    winners["Release"] = winners["Date"].apply(
        lambda x: datetime.strptime(x, "%B %d, %Y").year - 1
    )

    winners_unique = winners[["Movie", "Release"]].drop_duplicates()

    logging.info(f"Total unique movies {len(winners_unique)}")
    enriched_winners_df = pd.DataFrame(omdb_extractor.execute(winners_unique))

    # Merge enriched data back into the original winners DataFrame
    final_df = pd.merge(
        winners, enriched_winners_df, on=["Movie", "Release"], how="left"
    )

    # Print or save the DataFrame (example: saving to CSV)
    final_df.to_csv("oscar_winners_enriched.csv", index=False, sep=";")
