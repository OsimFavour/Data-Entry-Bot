from bs4 import BeautifulSoup
import requests
import lxml
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from time import sleep

options = Options()
options.add_experimental_option('excludeSwitches', ['enable-logging'])


CHROME_DRIVER_PATH = "C:\Development\chromedriver.exe"
GOOGLE_FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSdeEyBMdNoJeiAZdu-Z8de5adZcajroQ88oAKdnfcNcrMnuQQ/viewform?usp=sf_link"



class DataEntry:

    def __init__(self, driver_path) -> None:
        self.driver = webdriver.Chrome(executable_path=driver_path, options=options)
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9"
        }


    def url(self, i):
        """the url of the website """
        ZILLOW_URL = f"https://www.zillow.com/homes/for_rent/{i}_p/?searchQueryState=%7B%22pagination%22%3A%7B%22currentPage%22%3A{i}%7D%2C%22mapBounds%22%3A%7B%22west%22%3A-122.64481581640625%2C%22east%22%3A-122.22184218359375%2C%22south%22%3A37.63350123056882%2C%22north%22%3A37.91681026197016%7D%2C%22mapZoom%22%3A11%2C%22isMapVisible%22%3Atrue%2C%22filterState%22%3A%7B%22price%22%3A%7B%22max%22%3A872627%7D%2C%22beds%22%3A%7B%22min%22%3A1%7D%2C%22fore%22%3A%7B%22value%22%3Afalse%7D%2C%22mp%22%3A%7B%22max%22%3A3000%7D%2C%22auc%22%3A%7B%22value%22%3Afalse%7D%2C%22nc%22%3A%7B%22value%22%3Afalse%7D%2C%22fr%22%3A%7B%22value%22%3Atrue%7D%2C%22fsbo%22%3A%7B%22value%22%3Afalse%7D%2C%22cmsn%22%3A%7B%22value%22%3Afalse%7D%2C%22fsba%22%3A%7B%22value%22%3Afalse%7D%7D%2C%22isListVisible%22%3Atrue%7D"
        return ZILLOW_URL


    def main_requests(self, url):
        """make requests to it's url page"""
        response = requests.get(url, headers=self.headers)
        zillow = response.content
        soup = BeautifulSoup(zillow, "lxml")
        return soup


    def get_address(self, soup):
        """get all the addresses of the site page"""
        property_address = soup.find_all("address", {"data-test": "property-card-addr"})
        addresses = [address.getText().split(" | ")[-1] for address in property_address]
        return addresses


    def get_prices(self, soup):
        """get all the prices of the site page"""
        property_prices = soup.find_all("span", {"data-test": "property-card-price"})
        pricing = [price.text for price in property_prices]
        price_deals = [cash.split("+")[0] if "+" in cash else cash.split("/")[0] for cash in pricing]
        return price_deals


    def get_links(self, soup):
        """get all the links of the site page"""
        links = []
        property_links = soup.find_all("a", {"class": "StyledPropertyCardDataArea-c11n-8-73-8__sc-yipmu-0"})
        for link in property_links:
            href = link["href"]
            if "http" not in href:
                links.append(f"https://www.zillow.com{href}")
            else:
                links.append(href)
        return links


    def pagination(self):
        """get more than one page of the website"""
        self.address_list = []
        self.price_list = []
        self.link_list = []
        for page in range(1, 8):
            data = self.main_requests(self.url(page))
            self.address_list.extend(self.get_address(data))
            self.price_list.extend(self.get_prices(data))
            self.link_list.extend(self.get_links(data))


    def store_data(self):
        """store it's data into csv format using google forms"""
        for number in range(len(self.address_list)):      
            try:
                self.driver.get(GOOGLE_FORM_URL)
            except NoSuchElementException:
                self.driver.refresh()
            sleep(5)

            property_address = self.driver.find_element(By.XPATH, '//*[@id="mG61Hd"]/div[2]/div/div[2]/div[1]/div/div/div[2]/div/div[1]/div/div[1]/input')
            property_price = self.driver.find_element(By.XPATH, '//*[@id="mG61Hd"]/div[2]/div/div[2]/div[2]/div/div/div[2]/div/div[1]/div/div[1]/input')
            property_link = self.driver.find_element(By.XPATH, '//*[@id="mG61Hd"]/div[2]/div/div[2]/div[3]/div/div/div[2]/div/div[1]/div/div[1]/input')
            submit_button = self.driver.find_element(By.XPATH, '//*[@id="mG61Hd"]/div[2]/div/div[3]/div[1]/div[1]/div/span/span')

            property_address.send_keys(self.address_list[number])
            property_price.send_keys(self.price_list[number])
            property_link.send_keys(self.link_list[number])
            submit_button.click()




deals = DataEntry(CHROME_DRIVER_PATH)
deals.pagination()
deals.store_data()


