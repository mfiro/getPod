import os
import time
import xml.etree.ElementTree as ET
from pathlib import Path
import requests

def read_xml(filename):
    tree = ET.parse(filename)
    return tree

def parseEpisodes(eps_elements):
    ''' it parses each element to get title, episode and season number
    and url of the episode to be downloaded.
    it returns a list of dictionaries '''

    meta_data    = []
    for item_no in range(len(eps_elements)):
        ep_dict  = {}

        episode_title = eps_elements[item_no].find(r'{http://www.itunes.com/dtds/podcast-1.0.dtd}title')
        ep_dict["episode_title"] = episode_title.text if episode_title is not None else ''

        episode_no = eps_elements[item_no].find(r'{http://www.itunes.com/dtds/podcast-1.0.dtd}episode')
        ep_dict["episode_no"] = episode_no.text if episode_no is not None else ''

        season_no = eps_elements[item_no].find(r'{http://www.itunes.com/dtds/podcast-1.0.dtd}season')
        ep_dict["season_no"] = season_no.text if season_no is not None else ''

        episode_url = eps_elements[item_no].find('enclosure')

        if (episode_url is not None) and ('url' in episode_url.keys()):
            ep_dict["episode_url"] = episode_url.attrib['url']
        
        # saving name
        season_no  = "S{:02d}".format(int(ep_dict["season_no"])) if ep_dict["season_no"] != '' else ''
        episode_no = "E{:02d}".format(int(ep_dict["episode_no"])) if ep_dict["episode_no"] != '' else ''
        episode_title = ep_dict["episode_title"]

        ep_dict["saving_filename"] = r"{}_{}_{}".format(season_no, episode_no , episode_title)
        meta_data.append(ep_dict)
    return meta_data


def get_episodes(meta_data, podcast_title):
    ''' it iterates over the dictionary file and download the files '''

    for idx, get_item in enumerate(meta_data):
        filename = get_item["saving_filename"]
        filename = Path(r'data/{}/{}.mp3'.format(podcast_title,filename))

        # check if the file is already present in the folder
        if filename.exists():
            print("File already exists {} [{} of {} files]".format(get_item["saving_filename"], idx+1, len(meta_data)))
            continue

        print("\nDownloading {} [{} of {} files]".format(get_item["episode_title"], idx+1, len(meta_data)))

        file_url = get_item["episode_url"]
        if file_url == '':
            continue

        try:
            pass
            response = requests.get(file_url)
            filename.write_bytes(response.content)        
        except Exception:
            print("Something went wrong while downloading {} ".format(get_item["saving_filename"]))
            continue

        print("{} Downloaded".format(filename))
        time.sleep(1)


if __name__ == "__main__":

    read_from_url = True # Either from xml url or from xml file

    if read_from_url:
        rss_url  = "RSS_URL"
        response = requests.get(rss_url)
        root = ET.fromstring(response.text)
    else:
        filename = "XML_FILE.xml"
        tree = read_xml(filename)
        root = tree.getroot()

    # normally podcast title is located under subelement title
    podcast_title = root[0].find('title').text

    # get all the episode elements
    # located in subelements 'item'
    eps_elements = list(root[0].iter('item')) # list of all episodes

    # parse episode elements to get title, url and so on
    meta_data = parseEpisodes(eps_elements)

    # saving path
    save_to = "data/{}".format(podcast_title)
    if not os.path.exists(save_to):
        os.makedirs(save_to)

    # time to get episodes
    print("Downloading the files")

    get_episodes(meta_data, podcast_title)

    print("Downloading Done")

    # look for specific episode? try this:
    #meta_data  = list(filter(lambda episode: episode['episode_no'] == '3', meta_data))
