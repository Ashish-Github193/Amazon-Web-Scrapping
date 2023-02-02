#Master class for scrapping data from pages
class GET_DATA_FROM_PAGES:
    def __init__(self, __user_agents):
        self.__user_agents = __user_agents
        self.page_no = 1
        self.max_page_no = 20
        self.headers = choice(__user_agents)
        self.base_url = "https://www.amazon.in/s?k=bags&crid=2M096C61O4MLT&qid=1675243279&sprefix=ba%2Caps%2C283"
        self.data = pd.DataFrame(columns=["LINKS", "PRODUCT_NAMES", "RATINGS", "NUMBER_OF_REVIEWS", "PRICES"])

    #Manipulating Base URL for scrapping next pages
    def CREATE_URL_LIST(self):
        for page in range(self.page_no, self.max_page_no+1):
            page_url = self.base_url.split("&")
            page_url[0]+="&page="+str(page)
            page_url = "&".join(page_url)
            self.SCRAP_DATA_FROM_URLS(page_url)
            self.page_no += 1

    #Scrapping data from given URL
    def SCRAP_DATA_FROM_URLS(self, page_url):
        
        #Sending GET request to server
        self.headers = choice(self.__user_agents)
        data = requests.get(page_url, headers=self.headers)

        #Printing http request status on teminal
        if data.status_code == 503:
            print(f"Status code {data.status_code}. Scrapper detected... Changing request header...")
        elif data.status_code == 200:
            print(f"Status code 200. Request has succeeded for page {self.page_no}.")

        #Trying with random headers (if denied)
        while data.status_code != 200:
            self.headers = choice(self.__user_agents)
            data = requests.get(page_url, headers=self.headers)

            if data.status_code == 503:
                print(f"Status code {data.status_code}. Scrapper detected... Changing request header...")
            elif data.status_code == 200:
                print(f"Status code 200. Request has succeeded for page {self.page_no}.")

        #Parsing data with BeautifulSoup
        soup = BeautifulSoup(data.text, 'html.parser')

        #Searching for product element in parsed HTML file
        start = 2
        optimal_list_limit = 22
        for i in range(start, optimal_list_limit):

            items = soup.find_all('div', attrs={"cel_widget_id": f"MAIN-SEARCH_RESULTS-{i}"})

            #Storing clean data in clean_txt variable
            clean_txt = []

            #Iterating over items list item
            for item in items:
                texts = item.find_all(text=True)[:-9]
                for txt in texts:
                    if not (len(txt) <= 2 or (txt in ["Deal of the Day", "Best seller", "Amazon's ",  "₹", "FREE Delivery by Amazon", "Get it by ", "Choice", "Limited time deal"]) or (txt[-1] == "stars") or (txt[-4: -1] == "off") or (txt[-5: ] == "stars") or (txt[:3] == "for") or (txt[:2] == "in")):
                        clean_txt.append(txt) if (len(txt) >= 1) else 0
                

            #Appending clean product data to main list
            if (len(clean_txt) >= 4):
                matched_tags = soup.find_all(lambda tag: len(tag.find_all()) == 0 and clean_txt[0] in tag.text)
                for tag in matched_tags:
                    link = [self.base_url[:self.base_url.index("/", 8)] + tag.parent.get("href")]
                    name = [clean_txt[0]]
                    price = [int(float((clean_txt[3][1:]).replace(",", "")))]
                    rating = [float(clean_txt[1])]
                    number_of_reviews = [int((clean_txt[2][1:-1]).replace(",", ""))]
                    data_list = link + name + rating + number_of_reviews + price
                self.data.loc[len(self.data.index)] = data_list

    #Printing desired data in terminal
    def PRINT_DATA(self):
        entr = "\n"
        print(f"{entr*4}{'_'*150}{len(self.data)} results found")
        print(self.data.head(len(self.data.index)))

    #Run to get product data
    def RUN(self):
        self.CREATE_URL_LIST()
        self.PRINT_DATA()

if __name__ == "__main__":

    #Dependencies
    import requests
    import pandas as pd
    from random import choice
    from bs4 import BeautifulSoup
    from random_user_agent.user_agent import UserAgent
    from random_user_agent.params import SoftwareName, OperatingSystem

    #Creating random agents for user-agents rotation
    software_names = [SoftwareName.CHROME.value]
    operating_systems = [OperatingSystem.WINDOWS.value, OperatingSystem.LINUX.value]
    user_agent_rotator = UserAgent(software_names=software_names, operating_systems=operating_systems, limit=100)
    __user_agents = user_agent_rotator.get_user_agents()
     
    #main
    obj = GET_DATA_FROM_PAGES(__user_agents)
    obj.RUN()
    obj.data.to_csv("first_20_pages.csv")