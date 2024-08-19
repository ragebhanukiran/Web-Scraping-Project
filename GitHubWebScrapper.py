import requests
import os
import pandas as pd
from bs4 import BeautifulSoup
topics_url = 'https://github.com/topics'
response = requests.get(topics_url)
page_content = response.text


with open('webpage.html', 'w', encoding='utf-8') as f:
    f.write(page_content)


doc = BeautifulSoup(page_content, 'html.parser')



def parse_star_count(stars_str):
    stars_str = stars_str.strip()
    if stars_str[-1] == 'k':
        return int(float(stars_str[:-1]))*1000




def get_repo_info(h3_tag, star_tags):
    base_url = "https://github.com"
    a_tags = h3_tag.find_all('a')
    username = a_tags[0].text.strip()
    repo_name = a_tags[1].text.strip()
    repo_url = base_url + a_tags[1]["href"]
    stars = parse_star_count(star_tags.text.strip())
    return username, repo_name, stars, repo_url


def get_topic_page(topic_url):
    # Download the page
    response = requests.get(topic_url)
    # check the status
    if response.status_code != 200:
        raise Exception('Failed to load page {}'.format(topic_url))
    # parse using beautiful soup
    topic_doc = BeautifulSoup(response.text, 'html.parser')
    return topic_doc


def get_topic_repos(topic_doc):
    # Get the h3 tags conatining repo titles, urls and username
    repo_tags = topic_doc.find_all('h3', {'class': "f3 color-fg-muted text-normal lh-condensed"})
    # get_star_tags
    star_tags = topic_doc.find_all('span', {'class': "Counter js-social-count"})
    # get repo info
    topic_repos_dict = {
        'username': [],
        'reponame': [],
        'stars': [],
        'repo_url': []
    }
    for i in range(len(repo_tags)):
        repo_info = get_repo_info(repo_tags[i], star_tags[i])
        topic_repos_dict['username'].append(repo_info[0])
        topic_repos_dict['reponame'].append(repo_info[1])
        topic_repos_dict['stars'].append(repo_info[2])
        topic_repos_dict['repo_url'].append(repo_info[3])
    topic_repos_df = pd.DataFrame(topic_repos_dict)
    return topic_repos_df


def scrape_topic(topic_url, path):
    if os.path.exists(path):
        print("the file {} already exists. Skipping... ".format(path))
    topic_df = get_topic_repos(get_topic_page(topic_url))
    topic_df.to_csv(path, index=None)



def get_topic_titles(doc):
    selection_class ="f3 lh-condensed mb-0 mt-1 Link--primary"
    topic_title_tags = doc.find_all('p',{'class' : selection_class})
    topic_titles = []
    for tag in topic_title_tags:
      topic_titles.append(tag.text)
    return topic_titles
def get_topic_descs(doc):
   desc_selector = "f5 color-fg-muted mb-0 mt-1"
   topic_desc_tags = doc.find_all('p',{'class' : desc_selector})
   topic_description = []
   for tag in topic_desc_tags:
    topic_description.append(tag.text.strip())
   return topic_description

def get_topic_urls(doc):
  topic_link_tags = doc.find_all('a',{'class' :"no-underline flex-1 d-flex flex-column"})
  topic_urls = []
  base_url = 'https://github.com'
  for tag in topic_link_tags:
    topic_urls.append(base_url+tag['href'])
  return topic_urls
def scrape_topics():
  topics_url = 'https://github.com/topics'
  response = requests.get(topics_url)
  if response.status_code != 200:
    raise Exception('Failed to load page {}'.format(topics_url))
  topics_dict = {
      'title': get_topic_titles(doc),
      'description' : get_topic_descs(doc),
      'url' : get_topic_urls(doc)
  }
  return pd.DataFrame(topics_dict)


def scrape_topics_repos():
    print("Scraping list of topics from GitHub ")
    topics_df = scrape_topics()

    os.makedirs('../Practice/data', exist_ok=True)
    for index, row in topics_df.iterrows():
        print('Scraping top repositories for "{}"'.format(row['title']))
        scrape_topic(row['url'], 'data/{}.csv'.format(row['title']))
    print('Scraping is Completed!')
print(scrape_topics_repos())
