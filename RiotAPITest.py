from riotwatcher import LolWatcher, ApiError
from prettytable import PrettyTable
import itertools
import collections

class LoLStats():
    #global variables
    #api_key = "RGAPI-4cee2f90-9cbd-490d-a169-63f1c2fec9bf"
    #watcher = LolWatcher(api_key)
    #my_region = "NA1"

    def __init__(self,username):
        self.username = username
        self.api_key = "Insert API Key here"
        self.watcher = LolWatcher(self.api_key)
        self.region = "na1"
        self.player = self.watcher.summoner.by_name(self.region, self.username)
        self.playerID = self.player["id"]
        self.champDict = self.makeChampList()

    def makeChampList(self):
        # Check league's latest version
        latest = self.watcher.data_dragon.versions_for_region(self.region)['n']['champion']
        # Champions static information
        static_champ_list = self.watcher.data_dragon.champions(latest, False, 'en_US')
        champ_dict = {}
        for key in static_champ_list['data']:
            row = static_champ_list['data'][key]
            champ_dict[row['key']] = row['id']
        return champ_dict

    def getPlayer(self):
        return self.player

    def getUserName(self):
        return self.username

    #Returns the rankedstats of a player from riotwatcher in the form of a dictionary
    def getRawRankedStats(self):

        ranked_stats = self.watcher.league.by_summoner(self.region, self.playerID)
        if not ranked_stats:
            return dict()
        else:
            return ranked_stats[0]

    #Returns the rank of the player
    def getRank(self):
        ranked_stats = self.getRawRankedStats()
        if ranked_stats :
            return str(ranked_stats["tier"] + " " + ranked_stats["rank"])
        else:
            return ("Unranked")

    #Returns the Ranked Winrate of the player as a float
    def getRankedWinRateFloat(self):
        if ranked_stats:
            ranked_stats = self.getRawRankedStats()
            winrate = ranked_stats ["wins"] / (ranked_stats ["wins"]  + ranked_stats["losses"])
            return round(winrate,2)
        return "NA"

    #Returns the Ranked Winrate of the player as a string
    def getRankedWinRateStr(self):
        ranked_stats = self.getRawRankedStats()
        if ranked_stats:
            winrate = ranked_stats["wins"] / (ranked_stats["wins"] + ranked_stats["losses"])
            return str(round(winrate*100,2)) + "%"
        return "NA"

    #Returns the champion mastery data in its raw format so it can be used in other methods
    def getRawChampionMastery(self):
        mastery = self.watcher.champion_mastery.by_summoner(self.region, self.playerID)
        return mastery

    #Retuns the champion mastery data is a dictionary with champion name and mastery points as the key/value pairs
    def getChampionMastery(self):
        mastery = self.getRawChampionMastery()
        champsPlayed = {}
        for i in mastery:
            if i["championLevel"] > 0:
                champsPlayed[self.champDict[str(i["championId"])]] =  i["championPoints"]
        return champsPlayed

    #Returns the champion mastery of an individual champion
    def getSpecificChampionMastery(self, champName):
        mastery = self.getChampionMastery()
        if champName in mastery:
            return mastery[champName]
        else:
            return "The summoner does not play " + champName

    def bestChamps(self):
        champs = self.getRawChampionMastery()
        bestChamps = []
        for i in champs:
            if i["championPoints"] >= 1:
               bestChamps.append([self.champDict[str(i["championId"])], i["championPoints"]])
        ret = []
        for i in range(0, 5):
            ret.append(bestChamps[i][0])
        return ret

    def getPlayerSummary(self):
        return [self.getRank(), self.getRankedWinRateStr(), self.bestChamps()]

    def rawCurrentGame(self):
        currentGameInfo = self.watcher.spectator.by_summoner(self.region, self.playerID)
        return currentGameInfo

    def getPlayersCurrentGame(self):
        players = self.rawCurrentGame()["participants"]
        blueSide = []
        redSide = []
        for i in players:
            if i["teamId"] == 100:
                blueSide.append(i["summonerName"])
            else:
                redSide.append(i["summonerName"])
        return blueSide, redSide

    def getPlayersCurrentGame_POV(self):
        players = self.rawCurrentGame()["participants"]
        blueSide = []
        redSide = []
        for i in players:
            if i["summonerId"] != self.playerID:
                if i["teamId"] == 100:
                    blueSide.append(i["summonerName"])
                else:
                    redSide.append(i["summonerName"])
        return blueSide, redSide

    def scountCurrentGame_HelperPretty(self,team):
        t = PrettyTable(["Summoner Name", "Rank", "Ranked Win Rate", "Most Played Champs"])
        for i in range(len(team)):
            playerT1 = LoLStats(team[i])
            playerT1Sum = playerT1.getPlayerSummary()
            t.add_row([team[i], playerT1Sum[0], playerT1Sum[1], playerT1Sum[2]])

        return t

    def scoutCurrentGamePretty(self):
        l1, l2 = self.getPlayersCurrentGame()
        print("Blue Team")
        print(self.scountCurrentGame_HelperPretty(l1))
        print("Red Team")
        print(self.scountCurrentGame_HelperPretty(l2))

    def scountCurrentGame_HelperDiscord(self, blueTeam):
        t = []

        for i in range(len(blueTeam)):
            playerT1 = LoLStats(blueTeam[i])
            playerT1Sum = playerT1.getPlayerSummary()
            t.append([blueTeam[i], playerT1Sum[0], playerT1Sum[1], playerT1Sum[2]])
        return t

    def scoutCurrentGameDiscord(self):
        blueSide, redSide = self.getPlayersCurrentGame()
        game = {}
        game["Blue Team"] = self.scountCurrentGame_HelperPretty(blueSide)
        game["Red Team"] = self.scountCurrentGame_HelperPretty(redSide)
        return game

def test():
    test = LoLStats("fort")
    test.scoutCurrentGamePretty()

test()