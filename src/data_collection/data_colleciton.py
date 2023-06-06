import csv
import time
from bs4 import BeautifulSoup
import logging
from src.scraper.credits_scraper import CreditsScraper

DATA_PATH = "data/"


def get_credits_write_to_csv(
    scraper: CreditsScraper,
    movie_list_page: BeautifulSoup,
    id_list: list[str],
    title_list: list[str],
    writer: csv.DictWriter,
):
    for i, id in enumerate(id_list):
        credits_page = scraper.get_soup(scraper.credits_url.format(id))
        print("Loaded credits page...")
        cast_list = scraper.get_cast_list(credits_page)
        print("Loaded cast list...", title_list[i])
        directors = scraper.get_directors(credits_page)
        print("Loaded director list...", title_list[i])
        producers = scraper.get_producers(credits_page)
        print("Loaded producer list...", title_list[i])
        genres = scraper.get_genre(movie_list_page, i)
        print("Loaded genre list...", title_list[i])
        singers = scraper.get_singers(credits_page)
        print("Loaded singer list...")
        print("Writing to csv...", title_list[i])
        writer.writerow(
            [
                id_list[i],
                title_list[i],
                cast_list,
                directors,
                producers,
                singers,
                genres,
            ]
        )


def total_number_of_titles(movie_list_page):
    number_of_titles = int(
                movie_list_page.find("div", class_="desc")
                .span.text.split()[-2]
                .replace(",", "")
            )
     
    return number_of_titles













if __name__ == "__main__":
    scraper = CreditsScraper()
    first_page = True
    
    
    with csv.writer(open(DATA_PATH + "movies_data.csv", "w")) as writer:
        writer.writerow(
            [
                "movie_ids",
                "movie_title",
                "cast_list",
                "directors",
                "producers",
                # "singers",
                "genres",
            ]
        )

        total_titles: int = 0 # no. of titles to be scraped
        
        while True:
            t1 = time.time()
            if not first_page:
                # updating the url with the next page
                scraper.payload["start"] = str(
                    int(scraper.payload.get("start", 1)) + 250
                )
                scraper.payload["ref_"] = "adv_nxt"
                if int(scraper.payload.get("start", 1)) > total_titles:
                    break
            first_page = False

            # main movie list page
            movie_list_page = scraper.get_soup(scraper.main_url, scraper.payload)
            # reducing the search space
            movie_list_page = movie_list_page.find("div", class_="lister-list")
            total_titles = total_number_of_titles(movie_list_page)
            id_list, title_list = scraper.get_movie_ids_and_title(movie_list_page)
            get_credits_write_to_csv(scraper, writer, movie_list_page, id_list, title_list)
































            t2 = time.time()
            print(f"Time taken: {t2-t1}")
