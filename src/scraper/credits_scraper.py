import csv
import time
import random
from typing import Union
import requests
from bs4 import BeautifulSoup
import asyncio
# import logging

# logger = logging.getLogger(__name__)
# logger.setLevel(logging.INFO)
# logger.addHandler()


USER_AGENT_LIST = [
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:73.0) Gecko/20100101 Firefox/73.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.5 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36 Edge/16.16299",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:63.0) Gecko/20100101 Firefox/63.0",
]


class CreditsScraper:
    def __init__(self):
        self.main_url = "https://www.imdb.com/search/title/" # ?title_type=feature&release_date=2000-01-01,&num_votes=100,&countries=in&languages=hi&sort=year,asc&count=250"

        self.payload = {
            
            "title_type":"feature",
            "release_date":"2000-01-01,",
            "num_votes":"100,",
            "countries":"in",
            "languages":"hi",
            "sort":"year,asc",
            "count": "250",
            "start": "1751", 
            "ref_": "adv_nxt",
            
            # "start": "501",
            # "ref_": "adv_nxt",
        }

        self.credits_url = "https://www.imdb.com/title/{}/fullcredits?ref_=tt_ov_wr_sm"
        self.session = requests.Session()

    async def get_soup(
        self, url: str, payload: dict = None, headers: dict = None
    ) -> Union[BeautifulSoup, None]:
        """Get soup from url

        Args:
            url (str): url to get soup from
            payload (dict, optional): payload. Defaults to None.
            headers (dict, optional): request headers. Defaults to None.

        Returns:
            Union[BeautifulSoup, None]: returns soup if request is successful else None
        """

        self.session.headers.update({"user-agent": random.choice(USER_AGENT_LIST)})
        r = self.session.get(url, params=payload, headers=headers)
        if r.status_code == 200:
            soup = BeautifulSoup(r.text, "lxml")
            return soup
        r.raise_for_status()

    async def get_movie_ids_and_title(self, movie_list_page: BeautifulSoup):
        self.headings = movie_list_page.find_all("h3", class_="lister-item-header")
        self.title_list = [item.a.text for item in self.headings]
        self.id_list = [item.a["href"].split("/")[2] for item in self.headings]
        self.year_list = [i.find('span', class_="lister-item-year text-muted unbold").text for i in self.headings]
        
        return self.id_list, self.title_list, self.year_list

    async def get_genre(
        self, movie_list_page: BeautifulSoup, i: int
    ) -> Union[list[str], float]:
        try:
            self.genres = (
                movie_list_page.find_all("span", class_="genre")[i]
                .text.strip()
                .replace(",", "")
                .split()
            )
        except AttributeError:
            return float("nan")
        return self.genres

    async def get_directors(
        self, credits_page: BeautifulSoup
    ) -> Union[list[str], float]:
        try:
            self.directors = [
                director.a.text.strip()
                for director in credits_page.find(
                    "h4", attrs={"name": "director"}
                ).next_sibling.next_sibling.find_all(
                    "td", class_="name"
                )  # type: ignore
            ]
        except AttributeError:
            return float("nan")
        return self.directors

    async def get_writers(self, credits_page: BeautifulSoup) -> Union[list[str], float]:
        try:
            self.writers = [
                writer.a.text.strip()
                for writer in credits_page.find(
                    "h4", attrs={"name": "writer"}
                ).next_sibling.next_sibling.find_all("td", class_="name")
            ]
        except AttributeError:
            return float("nan")
        return self.writers

    async def get_producers(
        self, credits_page: BeautifulSoup
    ) -> Union[list[str], float]:
        try:
            self.producers = [
                producer.a.text.strip()
                for producer in credits_page.find(
                    "h4", attrs={"name": "producer"}
                ).next_sibling.next_sibling.find_all("td", class_="name")
            ]
        except AttributeError:
            return float("nan")
        return self.producers

    async def get_cast_list(
        self, credits_page: BeautifulSoup
    ) -> Union[list[str], float]:
        try:
            self.cast_table = credits_page.find("table", class_="cast_list").find_all(
                "tr", class_=["odd", "even"]
            )
            self.cast_list = [
                row.td.next_sibling.next_sibling.a.text.strip()
                for row in self.cast_table
            ]
        except AttributeError:
            return float("nan")
        return self.cast_list

    async def get_singers(self, credits_page: BeautifulSoup) -> Union[list[str], float]:
        self.singers_list = []
        try:
            self.singers_table = credits_page.find(
                "h4", attrs={"name": "music_department"}
            ).next.next.next.find_all("td", class_=["name", "credit"])
            for i in range(0, len(self.singers_table), 2):
                self.singers_list.append(
                    (
                        self.singers_table[i].a.text.strip(),
                        self.singers_table[i + 1].text.strip(),
                    )
                )
        except AttributeError:
            return float("nan")
        return self.singers_list


async def main():
    scraper = CreditsScraper()
    print(" * scraper initialized * ")
    first_page = True
    writer = csv.writer(open("movies_data5.csv", "w", newline="", encoding="utf-8"))
    print(" * csv file opened * ")
    writer.writerow(
        [
            "movie_ids",
            "movie_title",
            "year",
            "cast_list",
            "directors",
            "producers",
            # "singers",
            "genres",
        ]
    )
    
    print(" * csv file header written * ")
    idx = 1751
    while True:
        print(" * Loading movie list page... * ")
        t1 = time.time()
        if not first_page:
            scraper.payload["start"] = str(int(scraper.payload.get("start", 1)) + 250)
            scraper.payload["ref_"] = "adv_nxt"
        movie_list_page = await scraper.get_soup(scraper.main_url, scraper.payload)
        print(" * loaded movie list page * ")
        id_list, title_list, year_list = await scraper.get_movie_ids_and_title(movie_list_page)
        print( "* Length of items " , len(id_list), len(title_list), '*')
        for i, id in enumerate(id_list):
            credits_page = await scraper.get_soup(scraper.credits_url.format(id))
            print(f" * {idx} {i} Loaded credits page... {id} {title_list[i]} *")
            
            
            print(" * Loading credits...")
            cast_list, directors, producers, genres = await asyncio.gather(
                scraper.get_cast_list(credits_page),
                # print(" * Loaded cast list...", title_list[i])
                scraper.get_directors(credits_page),
                # print(" * Loaded director list...", title_list[i])
                scraper.get_producers(credits_page),
                # print(" * Loaded producer list...", title_list[i])
                scraper.get_genre(movie_list_page, i),
                # print(" * Loaded genre list...", title_list[i])
                # singers = scraper.get_singers(credits_page)
            )
            # print(" * Loaded singer list...")
            print(" * Writing to csv...", title_list[i], "*")
            writer.writerow(
                [
                    id_list[i],
                    title_list[i],
                    year_list[i],
                    cast_list,
                    directors,
                    producers,
                    # singers,
                    genres,
                ]
            )
            idx += 1
            # break
        # break
        first_page = False
        t2 = time.time()
        print(f"\n\n* Time taken: {t2-t1} *\n\n")
        
        
    # await writer.close()


if __name__ == "__main__":
    asyncio.run(main())
    
