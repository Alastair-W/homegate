from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
import time
import requests
from bs4 import BeautifulSoup
import math

# declare a variable that contains the url to be scraped - as these results will be over mutiple pages this will be the first page
url = 'https://www.homegate.ch/rent/real-estate/matching-list?loc=geo-city-geneve%2Cgeo-region-rive-droite-lac%2Cgeo-city-nyon%2Cgeo-region-rive-droite-campagne%2Cgeo-region-rive-gauche%2Cgeo-region-rhone-arve'
# use the 'requests' library to make a 'get' call for that webpage
page = requests.get(url)
# parse the web page content using the BeautifulSoup library
soup = BeautifulSoup(page.content, 'html.parser')
# scrape the html tag containing the total number of results
totalListings = soup.find('span', class_="ResultsNumber_results_3cf8J ResultListHeader_locations_3uuG8")
# take the text within the tag, remove everything but the count of results and convert to an integer
listingsInt = int(totalListings.text[:-8])
# print total count of listings
print(listingsInt)
# as each page contains a maximum of 20 results, divide by 20 and then round up to get the total number of pages that the scraper needs to loop through
numPages = math.ceil(listingsInt/20)
# print the result to confirm it worked
print(f'{numPages} pages of properties')

# create a list for each dimension
rentList = []
sizeList = []
roomList = []

# navigate the tags on the page containing price, size and room number
propertyInfo = soup.find_all('div', class_="ListItemTopPremium_data_3i7Ca")
print(f'number of instances of property data tag: {len(propertyInfo)}')
p=1
def scraper():
    for prop in propertyInfo:
        rent = prop.find('span', class_='ListItemPrice_price_1o0i3')
        size = prop.find('span', class_='ListItemLivingSpace_value_2zFir')
        rooms = prop.find('span', class_='ListItemRoomNumber_value_Hpn8O')
        if 'ListItemPrice_price_1o0i3' in str(prop.contents):
            rentList.append(rent.text)
            print(rent.text)
        else:
            rentList.append('empty')
            print('empty')

        if 'ListItemLivingSpace_value_2zFir' in str(prop.contents):
            sizeList.append(size.contents[0])
            print(size.contents[0])
        else:
            sizeList.append('empty')
            print('empty')

        if 'ListItemRoomNumber_value_Hpn8O' in str(prop.contents):
            roomList.append(rooms.text)
            print(rooms.text)
        else:
            roomList.append('empty')
            print('empty')

    print(f'Page {p}:', len(rentList), len(sizeList), len(roomList))

scraper()


# ---------------------- EVERYTHING BELOW THIS LINE TAKES A WHILE TO RUN ----------

# as the results landing page has a different url structure than the other results pages we scraspe this first
# loop through each item and extract the data without tags, adding it to the appropriater lists
# the rent dimension will need some more clean up as some will contain speciasl characters and spaces
# the tag containing the room data has multiple items but we only want the first one
# now we loop through the remaining results pages by adding '?ep=' and then the page number that starts at 2

# the following line is the full script but I am using a smaller range to test it
for n in range(2,numPages+1):
# for n in range(2,5):
    ind = "ep="+str(n)+"&"
    # create a new variable with the url being created dynamically as we loop through each results page
    newUrl = f'https://www.homegate.ch/rent/real-estate/matching-list?{ind}loc=geo-city-geneve%2Cgeo-region-rive-droite-lac%2Cgeo-city-nyon%2Cgeo-region-rive-droite-campagne%2Cgeo-region-rive-gauche%2Cgeo-region-rhone-arve'
    print(newUrl)
    # Create driver and identify which browser to 'drive'
    driver = webdriver.Firefox()
    # Get a page
    driver.get(newUrl)
    # wait 3 seconds cos sometimes not all elements are ready
    time.sleep(5)  
    # create a loop that updates the element to scroll to by 1 in each iteration so that we trigger the JS for every listing on the page (there are 20 per page)
    for i in range(1,21):
    # Get element using xPath because cant use a distinct HTML tag with a variable that takes the count of each iteration of the loop
        element = driver.find_element_by_xpath(f'//*[@id="app"]/main/div[2]/div/div[3]/div[2]/div[{i}]/a/div/div[2]')
    # Create action chain object
        action = ActionChains(driver)
    # Scroll down to the element on the page to load the listing container first
        driver.execute_script("arguments[0].scrollIntoView(true);",element)  
    # move to each element in the listings to execute the JS and load the content
        action.move_to_element(element).perform()
    # wait 1 second cos sometimes not all elements are ready
        time.sleep(1)  
    # parse the whole web page(s) content using the BeautifulSoup library
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    # loop through the page to find the elements with rent information and add that to a list
    propertyInfo = soup.find_all('div', class_='ListItem_data_18_z_')
    # overwrite the variable used at the very top with the number of the results page
    p = n
    scraper()
    
    # close the browser to stop your task bar getting out of control
    driver.close()




print(f'List of properties with a rental price: {len(rentList)}')
print(f'List of properties with sq m listed: {len(sizeList)}')
print(f'List of properties with number of rooms listed: {len(roomList)}')


print(rentList)
print(sizeList)
print(roomList)



