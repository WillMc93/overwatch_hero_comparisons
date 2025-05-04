# %% Imports
# Std Lib
import re
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

    # DEBUG: Jump to some non tank heroes (pick one's with different health, armor, and shield values)
    if squishy_test:
        df = df[df['name'].isin(['Mei', 'Tracer', 'Cassidy', 'Widowmaker', 'Zenyatta', 'Torbjörn', 'Bastion'])]

    # Gather the data at the hero pages
    for name, url in df[['name', 'url']].values:
        print(name)

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
        health_raw = health_div.parent.find_next_sibling('td')
        if role == 'Tank':
            healths = _handle_tank_HAS(health_raw)
        else:
            health = health_raw.text.strip()
            assert len(health) in [2,3], f"Failed to parse {name} health: {health_raw}"
            healths = {'open_queue': health, 'role_queue': health, '6v6': health}

        print(f"Healths: {healths}")

        # Find armor
        armors = {}
        armor_div = soup.find('div', string='Armor')
        armor_raw = armor_div.parent.find_next_sibling('td') if armor_div else None
        if armor_raw and role == 'Tank':
            armors = _handle_tank_HAS(armor_raw)
        elif armor_raw:
            armor = armor_raw.text.strip()
            assert len(armor) in [2,3], f"Failed to parse {name} armor: {armor_raw}"
            armors = {'open_queue': armor, 'role_queue': armor, '6v6': armor}
        if armor_raw:
            print(f"Armors: {armors}")

        # Find shield
        shields = {}
        shield_div = soup.find('div', string='Shields')
        shield_raw = shield_div.parent.find_next_sibling('td') if shield_div else None
        if shield_raw and role == 'Tank':
            shields = _handle_tank_HAS(shield_raw)
        elif shield_raw:
            shield = shield_raw.text.strip()
            assert len(shield) in [2,3], f"Failed to parse {name} shield: {shield_raw}"
            shields = {'open_queue': shield, 'role_queue': shield, '6v6': shield}
        if shield_raw:
            print(f"Shields: {shields}")

        data.append({'healths': healths, 'armors': armors, 'shields': shields})

        # Find abilities

    df = pd.concat([df, pd.DataFrame(data)], axis=1)

    return df


def _handle_tank_HAS(has_element_raw: BeautifulSoup) -> dict:
    """
    Handle the tank health/armor/shield values

    @param has_element_raw: The raw health/armor/shield soup tree
    """
    has_element = has_element_raw.stripped_strings
    hass = {'open_queue': None, 'role_queue': None, '6v6': None}
    for h in has_element:
        h = h.lower()
        if 'open queue' in h:
            hass['open_queue'] = h.split(' ')[0]
        elif 'role queue' in h:
            hass['role_queue'] = h.split(' ')[0]
        elif '6v6' in h:
            hass['6v6'] = h.split(' ')[0]
        elif 'pilot form' in h:
            hass['pilot'] = h.split(' ')[0]
        elif re.match(r'^\d+$', h):
            hass['open_queue'] = h
            hass['role_queue'] = h
            hass['6v6'] = h
        else:
            raise Exception(f"Failed to parse health_raw string: {has_element_raw}")

    if hass['6v6'] is None:
        hass['6v6'] = hass['open_queue']

    return hass


# %% Main
if __name__ == "__main__":
    df = get_roster()
    df = get_hero_data(df)
