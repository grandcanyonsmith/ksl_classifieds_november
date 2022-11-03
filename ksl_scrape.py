# Read READ ME.txt before running the script.

# import the required libraries
import csv
import time
from urllib.parse import quote

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

import pandas as pd
from twilio.rest import Client

import os
import shutil
import requests

msg_list = []

while True:
    
    # store the main website url in a variable
    keyword_url = "https://classifieds.ksl.com/search/keyword/{}"
    website_url = "https://classifieds.ksl.com"


    # A simple method to start the chrome driver using selenium. You can check selenium tutorials online.
    # Selenium is used to scrape content from websites which uses javascript to render it's content.
    def start_driver():
        option = Options()
        # You can comment and uncomment the below 2 lines to get window or windowless mode of the google chrome.
        # option.add_argument('--headless')
        # option.add_argument('--disable-gpu')
        # Chrome driver manager automatically downloads the latest driver required to run google chrome using selenium.
        return webdriver.Chrome(executable_path=ChromeDriverManager().install(), chrome_options=option)


    # This is the main method which fetches the url links for all the items listed in the "New Listing" section
    def get_urls(driver, search_url, website_url):
        # driver.get() is used to open chrome and search for the given url
        # I used a while look to refresh page at 3 times before stopping. Because if the websites takes longers than
        # 20 seconds to open the pages, then the script won't be able to fetch the links. In that case, the script should
        # refresh the pages and search for the links again.
        driver.get(search_url)
        n = 3
        try:
            while n > 0:
                time.sleep(20)
                # once the webpage is fully loaded, driver.page_source is used to get all the content including content
                # rendered using javascript.
                page = driver.page_source
                # Then this page source is passed to BeautifulSoup to scrape the required content
                soup = BeautifulSoup(page, 'html.parser')
                # I use the find and find all method of bs4 to extract exact elements. It is accurate and fetches
                # the content all the time. The syntax for this is .find(Tag name, attrs = {'attribute': 'value '})
                # the below line uses find method to get the section tag which has class = 'newestListings-container'
                container = soup.find('section', attrs={'class': 'search-page-results'})
                if container is None:
                    driver.refresh()
                    n -= 1
                else:
                    break
            # Then if the page contains new listing sections, use find_all method to fetch all the anchor tags
            # to get product links
            item_list = container.find_all('a', attrs={'class': 'listing-item-link'})
            return [website_url + a['href'] for a in item_list]
        except Exception as e:
            print(f"Error {e} at {search_url}")
            return None


    # this method is used to get the actual content like name, price and seller info.
    # the logic for the while loop is exactly the same as above.
    def get_container(driver, url):
        driver.get(url.strip())
        n = 3
        try:
            while n > 0:
                time.sleep(20)
                page = driver.page_source
                soup = BeautifulSoup(page, 'html.parser')
                # the syntax is same, if it finds the details container on product page, the method returns this container
                container = soup.find('article', attrs={'id': 'listingContainer'})
                if container is None:
                    driver.refresh()
                    n -= 1
                else:
                    break
            return container
        except Exception as e:
            print(f"Error {e} at {url}")
            return None


    keywords = []
    with open('./keywords.csv', 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            keywords.append(quote(row[0]))

    # this command is used to actually start the chrome browser
    driver = start_driver()
    driver.get("https://www.ksl.com/myaccount/login?forward=https%3A%2F%2Fclassifieds.ksl.com%2F")
    time.sleep(2)

    username = driver.find_element_by_name('email')
    time.sleep(2)
    username.send_keys('canyonfsmith@gmail.com')

    time.sleep(2)
    password = driver.find_element_by_name('password')
    # password.click()
    password.send_keys('Wolf7147')
    # click on submit button
    username.submit()
    time.sleep(10)

    for keyword in keywords:
        search_url = keyword_url.format(keyword)

        data = []
        print("Fetching urls from: ", search_url)
        # fetches all the urls first and then loop over them and fetches each product info one by one.
        urls = get_urls(driver, search_url, website_url)
        
        dir_name = keyword
        
        try:   
            os.makedirs(dir_name)
        except:
            print ("already exist")
            
        if urls:
            print("{} items' urls obtained".format(len(urls)))
            for url in urls:
                print("Fetching data from %s" % url)
                container = get_container(driver, url)
                # Below you can see the bs4 commands to get titles,price and seller info if the get_container() returns the container.
                if container is not None:
                    title = container.find('h1', attrs={'class': 'listingDetails-title'})
                    title = title.text if title else ''
                    price = container.find('h2', attrs={'class': 'listingDetails-price'})
                    price = price.text if price else ''
                    views = container.find('span', attrs={'class': 'viewsDesktop-viewsNumber'})
                    views = views.text if views else ''
                    favorites = container.find('span', attrs={'class': 'viewsDesktop-favoritedNumber'})
                    favorites = favorites.text if favorites else ''
                    sellerName = container.find('span', attrs={'class': 'listingContactSeller-firstName-value'})
                    sellerName = sellerName.text if sellerName else ''
                    sellerPhone = container.find('span', attrs={'class': 'listingContactSeller-optionText'})
                    sellerPhone = sellerPhone.text if sellerPhone else ''
                    #print (views)
                    #print (favorites)
                    try:
                        viewAllLink = driver.find_element_by_class_name('photoViewer-viewAllLink')
                        driver.execute_script("arguments[0].click();", viewAllLink)
                    except NoSuchElementException:
                        pass
                        
                    #viewAllLink.click()
                    # driver.execute_script("arguments[0].click();", viewAllLink)

                    time.sleep(5)
                    #img_urls = container.find('div', attrs={'class': 'photoDesktop-photoContainer'}).find_all('img')
                    #print (img_urls)

                    new_page = driver.page_source
                    # Then this page source is passed to BeautifulSoup to scrape the required content
                    new_soup = BeautifulSoup(new_page, 'html.parser')
                    # I use the find and find all method of bs4 to extract exact elements. It is accurate and fetches
                    # the content all the time. The syntax for this is .find(Tag name, attrs = {'attribute': 'value '})
                    # the below line uses find method to get the section tag which has class = 'newestListings-container'
                    #container = new_soup.find('section', attrs={'class': 'search-page-results'})
                
                    # print (new_soup)
                    div_tags = new_soup.find('div', attrs={'class': 'photoViewer-imagesContainer'}).find_all('div', attrs={'class': 'carousel-carouselItem'})
                    #print (len(div_tags))
                    #print (div_tags)
                    
                    img_url_list = []

                    for div in div_tags:
                        img_tag = div.find('img')
                        img_src = img_tag['src']
                        if('product_small' in img_src):
                            img_src = img_src.replace('product_small', '664x500')
                        img_url_list.append(img_src)

                    print (len(img_url_list), img_url_list)

                    img_final_list = []
                    image_names_list = []
                    img_final_str = ""

                    for img in img_url_list:
                        if(img not in img_final_list):
                            img = 'http:' + img
                            img_final_list.append(img)

                    print (len(img_final_list), img_final_list)

                    for image in img_final_list:
                        img_final_str = img_final_str + image + "\n"
                        img_name = image.split("/")[-2].split("?")[0]
                        image_names_list.append(img_name)

                    
                    print (img_final_str)

                    for o in range(len(img_final_list)):
                        # Open the url image, set stream to True, this will return the stream content.
                        image_name = image_names_list[o]
                        filename = keyword + "/" + image_name
                        
                        r = requests.get(img_final_list[o], stream = True)
                        print (r)
                        # Check if the image was retrieved successfully
                        if r.status_code == 200:
                            # Set decode_content value to True, otherwise the downloaded image file's size will be zero.
                            r.raw.decode_content = True
                            
                            # Open a local file with wb ( write binary ) permission.
                            with open(filename,'wb') as f:
                                shutil.copyfileobj(r.raw, f)
                                
                            print('Image sucessfully Downloaded: ',filename)
                        else:
                            print('Image Couldn\'t be retreived')
    
                    subset = (title, price, views, favorites, sellerName, sellerPhone, url, img_final_str)
                    payload = {"title": title, "price":price, "views": views, "favorite": favorites, 'sellerName': sellerName, "sellerPhone": sellerPhone, 'url': url, 'img_final_str': img_final_str}
                    r = requests.post('https://hooks.zapier.com/hooks/catch/1739571/oq5s6rr/', data=payload)
                    print("Done:  ", subset)
                    # after fetching the info, storing them in a temporary data list so that we can write this to a csv file.
                    data.append(subset)
                else:
                    print('Could not find information for {} \n probably because the page took too long to load.'.format(
                        url.strip()))

            # Using the csv module, write the data to a csv file.
            with open('{}.csv'.format(keyword), 'w', newline='', encoding='utf8') as f:
                writer = csv.writer(f)
                writer.writerow(['title', 'price', 'views', 'favorites', 'sellerName', 'sellerPhone', 'url', 'Image Names'])
                writer.writerows(data)
        else:
            print('{} is taking too long to load. Proceeding to next keyword!'.format(search_url))

    driver.quit()

    # If you still have any sort of confusion or queries, please let me know. Thanks!


    # Developed by mutahhar_bm




    def send_message(info, to_number):
        account_sid = 'AC4edaa4f9768eb268b7907e9c2680d55d'
        auth_token = 'd410ace8a2f8e51a3ab05bf7ceabec88'
        client = Client(account_sid, auth_token)

        message = client.messages \
            .create(
        body=f"{info}",
        from_='+13852501338',
        to=to_number
        )
        print('Text message sent successfully')
        
    keywords = []
    price_range = {}    #Price range manually given
    
    with open('./keywords.csv', 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            keywords.append(quote(row[0]).replace(" ","%20"))
            price_min_max = quote(row[1]) + "-" + quote(row[2])
            price_range[quote(row[0]).replace(" ","%20")] = price_min_max

    print (price_range)

    df = pd.read_csv('msg.csv')
    #print (df.head())
    msgs = []
    msgs = df["message"].tolist()
    
    for keyword in keywords:
        print (keyword)
        file_name = keyword+'.csv'
        df = pd.read_csv(file_name)
        views_mean = df["views"].mean()
        #print ("views mean", views_mean)
        favorites_mean = df["favorites"].mean()
        #print ("favorites mean", favorites_mean)
        ratio_views_favorites = views_mean/favorites_mean
        #print ("ratio views favorites", ratio_views_favorites)
        price_sum = 0
        count = 0
        for i, j in df.iterrows():
            try:
                #print (j["price"])
                price_sum += float(j["price"][1:].replace(",",""))
                count += 1
                #print(i, j)
            except:
                print ()
                #print (j["price"])
        #print (price_sum)
        #price_mean = price_sum/len(df.index)
        price_mean = price_sum/count
        #print (price_mean)

        minimum = int(price_range[keyword].split("-")[0])
        maximum = int(price_range[keyword].split("-")[1])

        print (minimum, maximum)
        
        for i, j in df.iterrows():
            if(j["favorites"]!=0):
                try:
                    item_price = float(j["price"][1:].replace(",",""))
                    if(j["views"]/j["favorites"] > ratio_views_favorites and item_price < price_mean and item_price > minimum and item_price < maximum):
                        #print ("Price is good")
                        offer = item_price*0.7
                        offer = int(round(offer/5.0)*5.0)   #round to nearest 5 multiple
                        #print (item_price, offer)
                        text = "Hey, " + j["sellerName"] + " Do you still have the " + j["url"] + " ? Could you do " + str(offer) + "?"
                        print (text)
                        print ("Price is Good")
                        print ()
                        to_number = j["sellerPhone"].replace("-","")
                        txt = j["sellerPhone"]
                        if txt not in msgs:
                            msgs.append(txt)
                            print (to_number)
                            send_message(text, to_number)
                except:
                    #print (j["price"])
                    print ()

    df = pd.DataFrame(data=msgs, columns=["message"])
    df.to_csv("msg.csv", index=False, encoding="utf-8")
    
    time.sleep(60*60*12)    #Run once per 12 hours continuosly
    
    
