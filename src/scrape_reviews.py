from bs4 import BeautifulSoup
import requests

# from selenium import webdriver


# driver_path = "../webdriver/chromedriver.exe"
# brave_path = "C:/Program Files/BraveSoftware/Brave-Browser/Application/brave.exe"


# option = webdriver.ChromeOptions()
# option.binary_location = brave_path
# option.add_argument("--incognito")
# # option.add_argument("--headless") OPTIONAL

# Create new Instance of Chrome
# driver = webdriver.Chrome(executable_path=driver_path, options=option)




def get_soup(url):
    r = requests.get(url)
    soup = BeautifulSoup(r.text, "lxml")
    return soup


def get_movie_id(search_url, movie_name):
    search_result = get_soup(search_url).find_all("td", class_="result_text")
    for i in search_result:
        if i.a.text.lower() == movie_name:
            movie_id = i.a["href"].split("/")[2]
            return movie_id


def get_reviews(movie_name):
    # search_term = "Shershaah"
    base_url = "https://www.imdb.com/"
    search_url = f"https://www.imdb.com/find?q={movie_name}&s=tt&ttype=ft&ref_=fn_ft"
    movie_id = get_movie_id(search_url, movie_name)
    review_page_url = (
        base_url
        + f"title/{movie_id}/reviews?spoiler=hide&sort=helpfulnessScore&dir=desc&ratingFilter=0"
    )
    review_page = get_soup(review_page_url)
    reviews = review_page.find_all("div", class_="text show-more__control")
    review_list = [review.text.replace("\n", " ") for review in reviews]
    return review_list


# driver.get(review_page_url)
# load_more_button = driver.find_elements_by_class_name("ipl-load-more__button")
# load_more_button
