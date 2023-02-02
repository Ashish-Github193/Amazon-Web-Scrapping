#Master class fo scrapping product data fom URL
class GET_DATA_FROM_URL:
    def __init__(self, __user_agents) -> None:
        self.__user_agents = __user_agents
        self.product_urls = pd.read_csv("first_20_pages.csv").loc[:, "LINKS"]
        self.product_no = 0
        self.max_product_no = len(self.product_urls)
        self.headers = choice(self.__user_agents)
        self.data = pd.DataFrame(columns=["ASIN", "MANUFACTURER", "PRODUCT_DESCRIPTION", "DESCRIPTION"])

    def GET_PRODUCT_PAGE_URL(self):
        for idx in range(self.product_no, self.max_product_no):
            self.SCRAP_DATA_FROM_URL(self.product_urls[idx])
            self.product_no += 1

    def SCRAP_DATA_FROM_URL(self, product_url):
        self.headers = choice(self.__user_agents)
        data = requests.get(product_url, headers=self.headers)

        #Printing http request status on teminal
        self.GET_HTTP_REQUEST_STATUS(data=data)

        #Trying with random headers (if denied)
        while data.status_code != 200:
            self.headers = choice(self.__user_agents)
            data = requests.get(product_url, headers=self.headers)
            self.GET_HTTP_REQUEST_STATUS (data=data)

        #Parsing data with BeautifulSoup
        self.soup = BeautifulSoup(data.text, 'html.parser')

        try:
            data = self.PARSING_FROM_PAGE_TEMPLATE_1(product_url)
            self.data.loc[len(self.data.index)] = data
        except:
            try:
                data = self.PARSING_FROM_PAGE_TEMPLATE_2(product_url)
                self.data.loc[len(self.data.index)] = data
            except:
                print('-'*150, "\nUnable to find data... Product skipped\n", '-'*150, sep="")
                return None

    def PARSING_FROM_PAGE_TEMPLATE_1 (self, product_url, data=[]):

        #Asin and Manufacturer
        data = [product_url.split("/")[-1], self.GET_MERCHANT_INFO()]

        #Extracting product description
        try:
            product_description_tag = self.soup.find("div", id="productDescription")
            data.append(product_description_tag.find("p").find("span").text)
        except:
            try:
                for h2 in self.soup.find_all('h2'):
                    if h2.find(text=re.compile("Product Description")):
                        p_tags = (h2.parent).find_all("p")
                        break
                
                product_description_list = [p.text for p in p_tags if len(p.text) > 20]
                if len(product_description_list) == 0:
                    data.append("NA")
                    print("\n>>> Product Description Not found:", product_url)
                else:
                    data.append(str(product_description_list))
            except:
                data.append("NA")
                print("\n>>> Product Description Not found:", product_url)

        data.append(self.EXTRACT_DESCRIPTION())
        return data

    def PARSING_FROM_PAGE_TEMPLATE_2 (self, product_url, data = []):
        print("\n>>> Data not found on page template type 1... trying again...")
        product_description = 'NA'
        data = [product_url.split("/")[-1], self.GET_MERCHANT_INFO(), product_description, self.EXTRACT_DESCRIPTION()]
        return data

    def EXTRACT_DESCRIPTION (self):
        description = self.soup.find("div", id="feature-bullets")
        texts = description.find_all(text=True)
        clean_text = []
        for idx in range(len(texts)):
            if (len(texts[idx]) > 1):
                clean_text.append(texts[idx].strip())
        clean_text = " | ".join(clean_text)
        return clean_text

    def GET_MERCHANT_INFO (self):
        merchant_div = self.soup.find_all("div", id="merchant-info")
        spans = (merchant_div[0]).findAll(texts=False)
        texts = [span.text for span in spans]
        return texts[texts.index("Sold by ")+1]

    def GET_HTTP_REQUEST_STATUS (self, data):
        if data.status_code == 503:
            print(f"Status code {data.status_code}. Scrapper detected... Changing request header...")
        elif data.status_code == 200:
            print(f"\nStatus code 200. Request has succeeded for product {self.product_no}.")
        
    def RUN(self):
        self.GET_PRODUCT_PAGE_URL()
        entr = "\n"
        print(f"{entr*4}{'_'*150}{len(self.data)} results found")
        print(self.data.head(len(self.data.index)))

if __name__ == "__main__":

    #Dependencies
    import re
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
    entr = "\n"
    obj = GET_DATA_FROM_URL(__user_agents)
    obj.RUN()
    obj.data.to_csv("first_200_products.csv")