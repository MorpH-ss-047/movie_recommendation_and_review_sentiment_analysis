from bs4 import BeautifulSoup
import requests


class MovieNotFound(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(message)

    def __str__(self):
        return self.message
    
class ReviewScraper:
    def __init__(self, movie_name: str, review_count: int = 500) -> None:
        self.movie_name_for_url = "+".join(movie_name.lower().split())
        self.movie_name = movie_name.lower() 
        self.base_url = "https://www.imdb.com/"

        self.search_url = (
            f"https://www.imdb.com/find?q={self.movie_name_for_url}&s=tt&ttype=ft&ref_=fn_ft"
        )
        self.review_count = review_count
        self.movie_id = self.get_movie_id()
        if self.movie_id is None:
            raise MovieNotFound("Enter the movie with correct spelling")


    def get_soup(self, url, payload=None, headers=None) -> BeautifulSoup:
        r = requests.get(url, params=payload, headers=headers)
        if r.status_code == 200:
            soup = BeautifulSoup(r.text, "lxml")
            return soup
        else:
            print("Error: ", r.status_code)

    def get_movie_id(self) -> str:
        search_result = self.get_soup(self.search_url).find_all(
            "td", class_="result_text"
        )
        for i in search_result:
            if i.a.text.lower() == self.movie_name:
                movie_id = i.a["href"].split("/")[2]
                return movie_id

    def get_reviews(self) -> list[str]:
        self.review_list = []
        self.review_page_url1 = self.base_url + f"title/{self.movie_id}/reviews/"
        self.review_page_url2 = self.base_url + f"title/{self.movie_id}/reviews/_ajax"
        self.payload = {
            "sort": "curated",
            "dir": "desc",
            "spoiler": "hide",
            "ratingFilter": "0",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36",
        }
        self.headers = {
            "referer": "https://www.imdb.com/title/tt1187043/reviews?spoiler=hide&sort=curated&dir=desc&ratingFilter=0",
            "sec-ch-ua": '"Chromium";v="106", "Google Chrome";v="106", "Not;A=Brand";v="99"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36",
        }

        # Scraping reviews from the 1st page
        print("Scraping reviews from the 1st page")
        self.review_page_soup = self.get_soup(url=self.review_page_url1, payload=self.payload)
        self.review_list.extend(
            [
                review.text.replace("\n", " ")
                for review in self.review_page_soup.find_all(
                    "div", class_="text show-more__control"
                )
            ]
        )
        print("[FINISHED] Scraping reviews from the 1st page")

        self.pagination_key = self.review_page_soup.find("div", class_="load-more-data")[
            "data-key"
        ]
        self.payload["paginationKey"] = self.pagination_key
        
        

        
        # Scraping page-2 onwards
        print("[INFO] Scraping reviews from the 2nd page onwards")
        # checking if the movie has less than the specified review count
        self.total_reviews = int(
            self.review_page_soup.find("div", class_="header").div.span.text.split()[0]
        )
        self.review_count = min(self.review_count, self.total_reviews)
        num_pages = self.review_count // 25
        print(f"[INFO] Total pages to scrape: {num_pages}")
        
        for i in range(num_pages - 1):
            """Loop to scrape reviews from the 2nd page onwards"""
            
            print(f"[INFO] Scraping reviews from the page: {i+2}/{num_pages}")
            
            self.review_page_soup = self.get_soup(url=self.review_page_url2, payload=self.payload, headers=self.headers)
            self.review_list.extend(
                [
                    review.text.replace("\n", " ")
                    for review in self.review_page_soup.find_all(
                        "div", class_="text show-more__control"
                    )
                ]
            )
            print(len(self.review_list), len(set(self.review_list)))
            print(f"[FINISHED] Scraping reviews from the {i+2} page")
            # print(f"Extracting pagination key from page {i+2} for page {i+3}")
            
            
            self.load_more_data =  self.review_page_soup.find("div", class_="load-more-data")
            if self.load_more_data is None: 
                # no more reviews to scrape, represents the last page
                break                   
            
            self.pagination_key = self.review_page_soup.find("div", class_="load-more-data")[
                "data-key"
            ]
            self.payload["paginationKey"] = self.pagination_key
        return self.review_list


if __name__ == "__main__":
    movie_name = input("Enter movie name: ")
    review_count = int(input("Enter number of reviews to scrape: "))
    review_scraper = ReviewScraper(movie_name, review_count)
    reviews = review_scraper.get_reviews()
    # print(*reviews, sep="\n\n")
    print(len(reviews))
    print(len(set(reviews)))
    print(reviews[-1])
    