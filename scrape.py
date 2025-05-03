# %% Imports
# Std Lib
import time

# PyPI
import pandas as pd
import requests
from bs4 import BeautifulSoup

# Local


# Constants
BASE_URL = 'https://overwatch.fandom.com/'
ROSTER_URL = f'{BASE_URL}/wiki/Template:Heroes'

# %% Functions
def get_roster() -> pd.DataFrame:
    """
    Gather the wiki urls for each hero.
    """
    # Get the page
    page = requests.get(ROSTER_URL, timeout=5)
    time.sleep(2) # Be nice to the server
    if page.status_code != 200:
        raise Exception(f"Failed to load page: {ROSTER_URL}")
    soup = BeautifulSoup(page.content, 'html.parser')

    # Find the heros
    table = soup.find('table', {'class': 'navbox'})
    table = table.find('tbody')
    hero_td = table.find_all('td')

    # Get the link to the hero pages
    hero_links = []
    for td in hero_td:
        link = td.find('a')
        if link is None or 'href' not in link.attrs:
            continue
        hero_links.append(link)

    # Get the hero names and urls
    df = pd.DataFrame(
        [(link['title'], link['href']) for link in hero_links],
        columns=['name', 'url'],
    )

    return df


def get_hero_data(df: pd.DataFrame, squishy_test: bool = False) -> pd.DataFrame:
    """
    Get the hero data from the wiki.
    """
    # Create a list to hold the data
    data = []

    #re_tank_healths = re.compile(r'(?P<open_queue>\d+)\s+\(open queue)(?:\s*\+\s*(?P<armor>\d+))?')

    # DEBUG: Jump to some non tank heroes (pick one's with different health, armor, and shield values)
    if squishy_test:
        df = df[df['name'].isin(['Mei', 'Tracer', 'Cassidy', 'Widowmaker', 'Zenyatta', 'Torbjörn', 'Bastion'])]

    # Loop through the urls
    for name, url in df[['name', 'url']].values:
        print(name)

        if name == 'D.Va':
            # # Handle D.Va separately
            # row = df[df['name'] == name]
            # row = _handle_dva(row)
            # data.append(row)
            continue

        # Get the page
        url = f'{BASE_URL}{url}'
        page = requests.get(url, timeout=5)
        time.sleep(2) # Be nice to the server
        if page.status_code != 200:
            raise Exception(f"Failed to load page: {url}")
        soup = BeautifulSoup(page.content, 'html.parser')

        # Find role
        role = soup.find('a', class_='mw-redirect', title=lambda x: x in ['Tank', 'Damage', 'Support'])
        if role is None:
            raise Exception(f"Failed to find role: {url}")
        role = role['title']
        print(role)


        # Find health
        health_div = soup.find('div', string='Health')
        if health_div is None:
            raise Exception(f"Failed to find health div: {url}")
        health = health_div.parent.find_next_sibling('td')
        print(health)

        # Find the ability divs
        # ability_divs = soup.find_all('div', {'class': 'ability-details'})


    df = pd.concat([df, pd.DataFrame(data)], axis=1)


    return pd.DataFrame(data)
# %% Main
if __name__ == "__main__":
    df = get_roster()
