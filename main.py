import json
from datetime import datetime
from modules import compare
from modules import file_io
from modules import stats

from modules.scraper import Scraper
from modules.utils import ask_input, ask_multiple_option

groups = ['followers', 'following']

# # Ask for input
# target = ask_input('Enter the target username: ')
# group = ask_multiple_option(options = groups + ['both']);
# print('\nEnter your Instagram credentials')
# username = ask_input('Username: ')
# #password = ask_input(is_password = True)
# password = ask_input('Password: ')

def scrape(group):
    differs = False
    scraper = Scraper(target)
    startTime = datetime.now()

    scraper.authenticate(username, password, cookies_list)
    input("Press Enter to continue...")
    users = scraper.get_users(group, verbose=True)
    scraper.close()

    last_users = file_io.read_last(target, group)
    if last_users:
        differs = bool(compare.get_diffs(users, last_users))

    if (differs or not last_users):
        file_io.store(target, group, users)
    # Stats
    stats.numbers(len(users), scraper.expected_number)
    if (differs): stats.diff(users, last_users)
    print('Took ' + str(datetime.now() - startTime))

if __name__ == "__main__":
    with open("data/credentials.json", 'r') as file:
        credentials = json.load(file)
    with open("data/cookies.json", "r") as file:
        cookies = json.load(file)
    username = credentials["username"]
    password = credentials["password"]
    target = credentials["target"]
    
    cookies_list = []
    for cookie in cookies:
        cookies_dict = {}
        cookies_dict["name"] = cookie
        cookies_dict["value"] = cookies[cookie]
        cookies_list.append(cookies_dict)
        
    for group in groups:
        scrape(group)

# if (group == 'both'):
#     for group in groups:
#         scrape(group)
# else:
#     scrape(group)
