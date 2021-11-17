from __future__ import print_function
from os.path import expanduser
import json

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from time import sleep
import igraph as ig
from igraph import plot


PATH_TO_CHROMEDRIVER = ""
FB_EMAIL = ""
FB_PASSWORD = ""
FB_USERNAME = ""
SCROLL_PAUSE_TIME = 2


driver = webdriver.Chrome(PATH_TO_CHROMEDRIVER)
driver.get("http://www.facebook.com")

email = driver.find_element_by_name("email")
passw = driver.find_element_by_name("pass")
email.clear()
passw.clear()
email.send_keys(FB_EMAIL)
passw.send_keys(FB_PASSWORD)
passw.submit()

driver.get("https://www.facebook.com/{FB_USERNAME}/friends")

# Get scroll height
last_height = driver.execute_script("return document.body.scrollHeight")
while True:
    # Scroll down to bottom
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    # Wait to load page
    sleep(SCROLL_PAUSE_TIME)

    # Calculate new scroll height and compare with last scroll height
    new_height = driver.execute_script("return document.body.scrollHeight")
    if new_height == last_height:
        break
    last_height = new_height

friend_links = driver.find_elements_by_class_name("_5q6s")
N = len(friend_links)

names = {}
name_id = 1
for i in xrange(N):
    link = friend_links[i].get_attribute('href')
    if link is not None:
        name = link.split('.com/')[1].split('?')[0]
        if name != 'profile.php':
            names[name] = name_id
            name_id += 1

f = open('friend_names.txt', 'w')
f.write(json.dumps(names))
f.close()

E = set()

count = 0
for name, n_id in names.iteritems():
    print(count)
    count += 1
    E.add((0, n_id))
    link = f'https://www.facebook.com/{name}/friends_mutual?pnref=lhc'
    driver.get(link)

    # Get scroll height
    last_height = driver.execute_script("return document.body.scrollHeight")

    while True:
        # Scroll down to bottom
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        # Wait to load page
        sleep(SCROLL_PAUSE_TIME)

        # Calculate new scroll height and compare with last scroll height
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

    mutual_friend_links = driver.find_elements_by_class_name("_5q6s")
    mut_names = [link.get_attribute('href').split('.com/')[1].split('?')[0]
                 for link in mutual_friend_links
                 if link.get_attribute('href') is not None]
    for mut_name in mut_names:
        if names.get(mut_name, None) is not None:
            if (names[mut_name], n_id) not in E:
                E.add((n_id, names[mut_name]))

driver.close()
f = open('friends_edges.txt', 'w')
for edge in E:
    f.write(str(edge) + '\n')
f.close()
