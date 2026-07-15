import re
import requests
import os
import pandas as pd
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
    )
}

# Anchor all output paths to the script's own directory, so results always
# land in the same place regardless of the current working directory the
# script is invoked from.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")


def sanitize_filename(name):
    """Make a string safe to use as a filename (strip whitespace, drop
    path separators and other invalid characters so it can never create
    an unintended subfolder)."""
    name = name.strip()
    name = re.sub(r'[\\/:"*?<>|]+', "_", name)   # remove path separators & invalid chars
    name = re.sub(r"\s+", " ", name)              # collapse internal whitespace/newlines
    return name


def parse_star_count(stars_str):
    stars_str = stars_str.strip().lower()
    if not stars_str:
        return 0
    if stars_str[-1] == 'k':
        try:
            return int(float(stars_str[:-1]) * 1000)
        except ValueError:
            return 0
    try:
        return int(stars_str.replace(',', ''))
    except ValueError:
        return 0


def get_repo_info(repo_container):
    base_url = "https://github.com"
    h3_tag = repo_container.find('h3', {'class': "f3 color-fg-muted text-normal lh-condensed"})
    a_tags = h3_tag.find_all('a')
    username = a_tags[0].text.strip()
    repo_name = a_tags[1].text.strip()
    repo_url = base_url + a_tags[1]["href"]

    # Scope the star lookup to *this* repo's container instead of a flat,
    # page-wide list. Each repo card actually has two Counter spans (stars
    # and forks); grabbing the first one within this container keeps stars
    # and forks from getting misaligned across repos.
    star_tag = repo_container.find('span', {'class': "Counter js-social-count"})
    stars = parse_star_count(star_tag.text.strip()) if star_tag else 0

    return username, repo_name, stars, repo_url


def get_topic_page(topic_url):
    response = requests.get(topic_url, headers=HEADERS)
    if response.status_code != 200:
        raise Exception('Failed to load page {}'.format(topic_url))
    topic_doc = BeautifulSoup(response.text, 'html.parser')
    return topic_doc


def get_topic_repos(topic_doc):
    # Each repo on the topics page lives inside an <article> (or similar)
    # container. Find those containers directly so h3/star lookups stay
    # scoped per-repo rather than relying on two separately-indexed flat lists.
    h3_tags = topic_doc.find_all('h3', {'class': "f3 color-fg-muted text-normal lh-condensed"})
    repo_containers = [h3.find_parent('article') or h3.parent for h3 in h3_tags]

    topic_repos_dict = {
        'username': [],
        'reponame': [],
        'stars': [],
        'repo_url': []
    }

    for container in repo_containers:
        try:
            username, repo_name, stars, repo_url = get_repo_info(container)
        except (AttributeError, IndexError):
            continue
        topic_repos_dict['username'].append(username)
        topic_repos_dict['reponame'].append(repo_name)
        topic_repos_dict['stars'].append(stars)
        topic_repos_dict['repo_url'].append(repo_url)

    topic_repos_df = pd.DataFrame(topic_repos_dict)
    return topic_repos_df


def scrape_topic(topic_url, path):
    if os.path.exists(path):
        print("the file {} already exists. Skipping... ".format(path))
        return
    os.makedirs(os.path.dirname(path), exist_ok=True)
    topic_df = get_topic_repos(get_topic_page(topic_url))
    topic_df.to_csv(path, index=None)


def get_topic_titles(doc):
    selection_class = "f3 lh-condensed mb-0 mt-1 Link--primary"
    topic_title_tags = doc.find_all('p', {'class': selection_class})
    topic_titles = []
    for tag in topic_title_tags:
        topic_titles.append(tag.text.strip())
    return topic_titles


def get_topic_descs(doc):
    desc_selector = "f5 color-fg-muted mb-0 mt-1"
    topic_desc_tags = doc.find_all('p', {'class': desc_selector})
    topic_description = []
    for tag in topic_desc_tags:
        topic_description.append(tag.text.strip())
    return topic_description


def get_topic_urls(doc):
    topic_link_tags = doc.find_all('a', {'class': "no-underline flex-1 d-flex flex-column"})
    topic_urls = []
    base_url = 'https://github.com'
    for tag in topic_link_tags:
        topic_urls.append(base_url + tag['href'])
    return topic_urls


def scrape_topics():
    topics_url = 'https://github.com/topics'
    response = requests.get(topics_url, headers=HEADERS)
    if response.status_code != 200:
        raise Exception('Failed to load page {}'.format(topics_url))

    os.makedirs(BASE_DIR, exist_ok=True)

    # Save a local cache of the topics webpage (anchored to BASE_DIR)
    with open(os.path.join(BASE_DIR, 'webpage.html'), 'w', encoding='utf-8') as f:
        f.write(response.text)

    doc = BeautifulSoup(response.text, 'html.parser')

    topics_dict = {
        'title': get_topic_titles(doc),
        'description': get_topic_descs(doc),
        'url': get_topic_urls(doc)
    }

    topics_df = pd.DataFrame(topics_dict)
    topics_df.to_csv(os.path.join(BASE_DIR, 'topics.csv'), index=False)
    print("topics.csv created successfully!")
    return topics_df


def scrape_topics_repos():
    print("Scraping list of topics from GitHub")
    topics_df = scrape_topics()

    os.makedirs(DATA_DIR, exist_ok=True)
    for index, row in topics_df.iterrows():
        safe_title = sanitize_filename(row['title'])
        print('Scraping top repositories for "{}"'.format(safe_title))
        path = os.path.join(DATA_DIR, '{}.csv'.format(safe_title))
        scrape_topic(row['url'], path)
    print('Scraping is Completed!')


if __name__ == "__main__":
    scrape_topics_repos()