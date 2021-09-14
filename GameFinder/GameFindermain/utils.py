import requests
import time
from bs4 import BeautifulSoup
from flask import Markup
import lxml
import urllib.request
import os

# human-testing-URL:
# https://www.boardgamegeek.com/xmlapi2/collection?username=username&own=1


class BGGError(Exception):

    def __init__(self, errorcode):
        self.message = f"Error from BGG API, code: {errorcode}"
        print(self.message)

    def __str__(self):
        return self.message


def recommend_games(playercount, username, bestonly=False, hidePlayed=False, minimumcomplexity=0, maximumcomplexity=5):
    usergames = get_games(username, hidePlayed)
    if usergames is None:
        return None
    # filter out games that can't be played with the current playercount.
    filteredgames = filter_games(usergames, playercount, bestonly, minimumcomplexity, maximumcomplexity)
    return filteredgames


def get_games(username, hidePlayed):
    response = query_bgg(f"collection?username={username}&own=1")
    if response is None:
        return None
    data = BeautifulSoup(response, "lxml")
    games_list = get_game_ids(data, hidePlayed)
    return get_game_info(games_list)


def query_bgg(query, delay=0):
    response = requests.get(f"https://www.boardgamegeek.com/xmlapi2/{query}")
    # print("I pinged BGG here")
    if response.status_code == 200:
        if response.text is None:
            delay = delay + 1
            time.sleep(delay)
            query_bgg(query, delay)
        else:
            return response.text

    elif response.status_code == 202:
        print("Retrying...")
        delay = delay + 1
        time.sleep(delay)
        query_bgg(query, delay)

    elif response.status_code == 404:
        print(f"404, {query} Not Found, try again")
        raise BGGError(response.status_code)

    else:
        print(f"Unexpected response: {response.status_code}")
        raise BGGError(response.status_code)


def get_game_ids(data, hidePlayed):
    item_list = data.find_all("item")
    games_list = []
    for item in item_list:
        if hidePlayed:
            if int(item.find("numplays").text) != 0:
                continue
        id_dict = item.attrs['objectid']
        games_list.append(id_dict)
    return games_list


def get_game_info(game_ids):
    # breaks up ids into ids_per_query-sized chunks that can be parsed by the BGG API, and passes that to get_game_data.
    ids_per_query = 750
    games_list = []

    if len(game_ids) < ids_per_query:
        data = get_game_data(game_ids)
        games_list.extend(parse_game_data(data))
    else:
        for count, _ in enumerate(game_ids, 1):
            if count % ids_per_query == 0:
                sublist = game_ids[count - ids_per_query:count]
            elif count == len(game_ids):
                sublist = game_ids[-count % ids_per_query:len(game_ids)]
            else:
                continue
            data = get_game_data(sublist)
            games_list.extend(parse_game_data(data))

    return games_list


def get_game_data(game_ids):
    query = "thing?id="
    # adds game ids to the query to form a "megaquery" with a ton of ids in it, up to the ids_per_query in get_game_info
    for game_id in game_ids:
        query = query + f",{game_id}"
    # additional parameters to the query past the list of games being queried
    query = query + "&type=boardgame,boardgameexpansion&stats=1"
    response = query_bgg(query)
    data = BeautifulSoup(response, "xml")
    return data


def parse_game_data(data):
    # List will grab expansions as well as standalone games, due to possible differing playercounts.
    games_list = []
    for item in data.find_all('item'):
        # Deliberately not declaring as a dictionary literal. I think this is more human-readable.
        game = {}
        # "game" is a dictionary to be more JSON-able. Could (arguably should) have been a class.
        game["name"] = item.find("name").attrs["value"]
        # Grabbing ID again because passing each ID separately seems like a PitA. Needed for image naming convention.
        gameid = item["id"]
        game["image"] = save_images(item.find("thumbnail").text, gameid)
        # Markup used to turn the escaped HTML tags to English
        game["description"] = Markup(item.find("description").text).striptags()
        game["minplayers"] = int(item.find("minplayers").attrs["value"])
        game["maxplayers"] = int(item.find("maxplayers").attrs["value"])
        game["bestplayers"] = calculate_best_playercount(item, game["minplayers"], game["maxplayers"])
        game["rating"] = float(item.find("average").attrs["value"])
        game["complexity"] = float(item.find("averageweight").attrs["value"])
        games_list.append(game)
    return games_list


def save_images(image_url, gameid):
    # checks if image is already stored, if it is, return that. Otherwise, save it, then return that.
    basepath = get_main_directory()
    imagepath = os.path.join(basepath, "static", "thumbnails", f"{gameid}.jpg")

    if not os.path.exists(imagepath):
        urllib.request.urlretrieve(image_url, imagepath)

    #gameimage = Image.open(os.path.join(imagepath))
    gameimage = f"thumbnails/{gameid}.jpg"
    return gameimage


def get_main_directory():
    # configures relative path for use with save_images
    absolutepath = os.path.abspath(__file__)
    subdirectory = os.path.dirname(absolutepath)
    maindirectory = os.path.dirname(subdirectory)
    return maindirectory


def calculate_best_playercount(item, minplayers, maxplayers):
    results = item.find("poll").find_all("results")
    bestpoll = {}
    # threshold for difference in votes between most best and other best votes to be considered as a best playercount.
    sensitivity = .80

    for voteoption in results:
        # ignores BGG's weird convention to list players over the max the game allows as "X+"
        isvalid = True
        numplayers = voteoption.attrs["numplayers"]

        # Throws out nonsense votes for "N+" players, where N is greater than the allowed number of players.
        # Also allows for comparison
        if numplayers.isnumeric():
            numplayers = int(numplayers)
        else:
            continue

        if numplayers < minplayers or numplayers > maxplayers:
            # Throws out nonsense votes for more or less players than the game allows
            continue
        currentvotes = int(voteoption.find("result").attrs["numvotes"])

        bestpoll[numplayers] = float(currentvotes)

    bestplayers = []
    topvote = 0
    for player, vote in bestpoll.items():
        if vote >= topvote:
            topvote = vote
            # for each "bestplayer" evaluated, if the number of votes for that player is within sensitivity%
            # of the amount of votes for the new best player, keep that within the bestplayer range.

            # lists cannot be modified during a for loop (?) so we need to make a temporary list
            tempbest = []
            for bestplayer in bestplayers:
                if bestpoll[bestplayer] >= sensitivity * topvote:
                    tempbest.append(bestplayer)
            # add the player with the top votes to the temporary list
            tempbest.append(player)
            # temporary list becomes the new best list
            bestplayers = tempbest
    if topvote == 0:
        bestplayers = [None]
    return bestplayers


def filter_games(games, playercount, bestonly, mincomplexity, maxcomplexity):
    filteredgames = []
    for candidategame in games:
        if candidategame["maxplayers"] < playercount or candidategame["minplayers"] > playercount:
            continue
        if bestonly:
            if playercount not in candidategame["bestplayers"]:
                continue
        if candidategame["complexity"] < mincomplexity or candidategame["complexity"] > maxcomplexity:
            continue
        filteredgames.append(candidategame)
    filteredgames.sort(key=sort_by_rating, reverse=True)
    return filteredgames


def sort_by_rating(game):
    return game["rating"]


if __name__ == '__main__':

    try:
        recgames = recommend_games(5, "iomio", bestonly=False, hidePlayed=True, minimumcomplexity=0, maximumcomplexity=5)
        for game in recgames:
            print(
                f"{game['name']}, rating:{game['rating']}/10, best with {game['bestplayers']} players, complexity:{game['complexity']}/5")
        print(len(recgames))

    except BGGError:
        pass