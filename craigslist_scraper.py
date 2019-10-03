from bs4 import BeautifulSoup
import requests
import pandas as pd
from time import sleep

# text prompts that gets the search input from the user
inputting = True
print("Welcome to Alex Filbert's Craiglist web scraper.")
sleep(2)
print("Various information about each listing that is found will be put into an excel spreadsheet.")
sleep(2)
print("The Excel documents can be found in this directory once the program is complete. ")
sleep(2)
while inputting:
    print('What would you like to search for? (instead of spaces, use "+". ex: rocking+chair): ')
    input_1 = input()
    print('Begin extracting data from all results under "{}"? (yes/no)'.format(input_1))
    input_2 = input()
    if input_2 == 'yes':
        inputting = False
        print('Beginning data extraction...')
    elif input_2 == 'no':
        pass
    else:
        print("Please answer by typing 'yes' or 'no' and clicking enter. ")

# URL of the craigslist page to be scraped
url = 'https://seattle.craigslist.org/search/sss?query={}&sort=rel'.format(input_1)

# We will append the data into these lists and put into a Pandas dataframe
title_list = []
price_list = []
location_list = []
date_list = []
href_list = []

description_list = []
condition_list = []
posted_time_list = []
last_updated_list = []
post_id_list = []

page = 0

scraping = True
# We use a while loop because switching pages might be necessary to collect all the
# data on one craigslist search.
while scraping:

    # Requesting the server to let us retrieve data from the site
    src = requests.get(url)
    # Getting html of the webpage
    results = src.content
    # Converting html to more readable format with BeautifulSoup
    soup = BeautifulSoup(results, 'lxml')
    # Finding all classes that matches 'result-info', this contains all the basic item info
    front_page_info = soup.find_all(class_='result-info')

    # Gets the number of total results. 120 results max per page.
    num_of_total_results = soup.find(class_='totalcount').get_text()
    # Gets the number of results in the page. Less than 120 results indicates the last page.
    range_to = soup.find(class_='rangeTo').get_text()
    range_from = soup.find(class_='rangeFrom').get_text()
    num_of_items = int(range_to) - int(range_from) + 1
    print('Total number of listings: ' + str(num_of_total_results))
    print('number of items on page: ' + str(num_of_items))
    url = 'https://seattle.craigslist.org/search/sss?query={}&sort=rel'.format(input_1 + '&s=' + str(range_to))

    # Using the find method to get title, price, location, product page, and date for all items
    for item in range(len(front_page_info)):
        title = front_page_info[item].find(class_='result-title hdrlnk').get_text()
        title_list.append(title)
        price = front_page_info[item].find(class_='result-price').get_text()
        price_list.append(price)
        date = front_page_info[item].find(class_='result-date').get_text()
        date_list.append(date)
        href = front_page_info[item].find('a', href = True)['href']
        href_list.append(href)
        # Not all items have locations and some have 'nearby' locations which are
        # different from normal (more specific) location data. This nested if-statement
        # checks for the most specific location first, then the 'nearby' location,
        # and lastly, prints 'no location given' if the previous two searches came up short.
        location = front_page_info[item].find(class_='result-hood')
        if location == None:
            nearby_location = front_page_info[item].find(class_='nearby')
            if nearby_location == None:
                location = 'No location given'
                location_list.append(location)
            else:
                location_list.append(nearby_location.get_text())
        else:
            location_list.append(location.get_text())

    # Getting specific product info from product href:
    tracker = 1
    print("href list "+str(len(href_list)))
    # When scraping from more than one page, the href list will be appended and we can use
    # a for-loop like 'for href in href_list'
    for href in range(num_of_items):
        print('product number: ' + str(tracker) + "| " + 'page: ' + str(page) +"| "+ "range from: " \
        + str(int(range_from)) +"| "+ "range to: " + str(int(range_to)) + "|")
        tracker += 1
        src = requests.get(href_list[int(range_from) - 1 + href])
        results = src.content
        soup = BeautifulSoup(results, 'lxml')
        product_info = soup.find(class_='userbody')
        # This if-statement makes sure the code keep running even if there is no html to be
        # scraped from one of the products for some reason
        if product_info == None:
            print('HTML error for product')
        else:
            description = product_info.find(id='postingbody').get_text()
            description_list.append(description)
            if product_info.find(class_='attrgroup') == None:
                condition = 'No data on condition of product'
                condition_list.append(condition)
            else:
                condition = product_info.find(class_='attrgroup')
                if condition.find('b') == None:
                    condition = 'No data on condition of product'
                    condition_list.append(condition)
                else:
                    condition_type = condition.find('b').get_text()
                    condition_list.append(condition_type)
            # sometimes there isn't a posting time on the page
            has_last_update = len(product_info.find_all(class_='date timeago'))
            if has_last_update == 2:
                if product_info.find_all(class_='date timeago')[1] == None:
                    last_updated = 'Last post update time could not be found.'
                    last_updated_list.append(last_updated)
                else:
                    last_updated = product_info.find_all(class_='date timeago')[1].get_text()
                    last_updated_list.append(last_updated)
            else:
                last_updated = 'Does not have last-update time for the posting'
                last_updated_list.append(last_updated)

            if product_info.find(class_='date timeago') == None:
                posted_time = 'Posting time could not be found.'
                posted_time_list.append(posted_time)
            else:
                posted_time = product_info.find(class_='date timeago').get_text()
                posted_time_list.append(posted_time)

            if product_info.find(class_='postinginfo') == None:
                post_id = 'Posting ID could not be found'
                post_id_list.append(post_id)
            else:
                post_id = product_info.find(class_='postinginfo').get_text()
                post_id_list.append(post_id)
    page += 1
    if num_of_items < 119:
        scraping = False

# Creating a dictionary of the data for the Pandas dataframe
font_page_data = {
        'Title: ' : title_list,
        'Price: ' : price_list,
        'Date: ' : date_list,
        'Location: ' : location_list,
        'href: ' : href_list
}

product_page_data = {
        'description: ' : description_list,
        'condition: ' : condition_list,
        'posted_time: ' : posted_time_list,
        'last_updated: ' : last_updated_list,
        'post_id: ' : post_id_list
}

front_page_df = pd.DataFrame(font_page_data)
product_page_df = pd.DataFrame(product_page_data)
# These csv files will overwrite its contents when run more than once
# unless you change the name of the files
export_csv_1 = front_page_df.to_csv(r'C:\users\alex\pythonprojects\cragslist_front_page_data.csv', index = None, header = True)
export_csv_2 = product_page_df.to_csv(r'C:\users\alex\pythonprojects\cragslist_product_page_data.csv', index = None, header = True)

print('done')
