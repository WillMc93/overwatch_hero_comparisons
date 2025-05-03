# %% Imports
# Std Lib
import time

# PyPI
import pandas as pd
import requests
from bs4 import BeautifulSoup

# Local


# Constants
BASE_URL = "https://overwatch.fandom.com/wiki/"
ROSTER_URL = f"{BASE_URL}Template:Heroes"

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
    soup = BeautifulSoup(page.content, "html.parser")

    # Find the heros
    table = soup.find("table", {"class": "navbox"})
    table = table.find("tbody")
    hero_td = table.find_all("td")

    # Get the link to the hero pages
    hero_links = []
    for td in hero_td:
        link = td.find("a")
        if link is None or "href" not in link.attrs:
            continue
        hero_links.append(link)

    # Get the hero names and urls
    df = pd.DataFrame(
        [(link['title'], link["href"]) for link in hero_links],
        columns=["name", "url"],
    )

    return df


# %% Main
if __name__ == "__main__":
    df = get_roster()
