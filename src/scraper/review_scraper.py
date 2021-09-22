from bs4 import BeautifulSoup
import requests


class ReviewScraper:
    def __init__(self, movie_name, review_count=500) -> None:
        self.movie_name = movie_name
        self.base_url = "https://www.imdb.com/"

        self.search_url = (
            f"https://www.imdb.com/find?q={movie_name}&s=tt&ttype=ft&ref_=fn_ft"
        )
        self.review_count = review_count
        self.movie_id = self.get_movie_id()

    def get_soup(self, url, payload=None):
        r = requests.get(url, params=payload)
        if r.status_code == 200:
            soup = BeautifulSoup(r.text, "lxml")
            return soup

    def get_movie_id(self):
        search_result = self.get_soup(self.search_url).find_all(
            "td", class_="result_text"
        )
        for i in search_result:
            if i.a.text.lower() == self.movie_name:
                movie_id = i.a["href"].split("/")[2]
                return movie_id

    def get_reviews(self):
        self.review_list = []
        self.review_page_url = self.base_url + f"title/{self.movie_id}/reviews/_ajax"
        self.pagination_key = ""  # blank pagination key for the 1st page
        payload = {
            "sort": "helpfulnessScore",
            "dir": "desc",
            "spoiler": "hide",
            "ratingFilter": "0",
            "ref_": "undefined",
            "paginationKey": self.pagination_key,
        }

        # Scraping reviews from the 1st page
        review_page = self.get_soup(url=self.review_page_url, payload=payload)
        self.review_list.extend(
            [
                review.text.replace("\n", " ")
                for review in review_page.find_all(
                    "div", class_="text show-more__control"
                )
            ]
        )

        # Scraping page-2 onwards
        num_pages = self.review_count // 25
        for _ in range(num_pages - 1):

            page_soup = self.get_soup(url=self.review_page_url, payload=payload)
            self.review_list.extend(
                [
                    review.text.replace("\n", " ")
                    for review in page_soup.find_all(
                        "div", class_="text show-more__control"
                    )
                ]
            )
            payload["pagination_key"] = page_soup.find("div", class_="load-more-data")[
                "data-key"
            ]

        return self.review_list
