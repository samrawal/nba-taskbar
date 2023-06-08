import rumps
from datetime import datetime, timezone
from nba_api.live.nba.endpoints import scoreboard
from nba_api.live.nba.endpoints import boxscore


def game_data(gameid, emoji=True, abbr=False):
    box = boxscore.BoxScore(gameid)
    gamedata = box.game.get_dict()
    if abbr == False:
        scorefmt = lambda d, key: "{} {} ({})".format(d[key]["teamCity"], d[key][
            "teamName"], d[key]["score"])
        out = "{} @ {} -- {}".format(scorefmt(gamedata, "awayTeam"),
                                    scorefmt(gamedata, "homeTeam"),
                                    gamedata["gameStatusText"])
    else:
        scorefmt = lambda d, key: "{} ({})".format(d[key][
            "teamName"], d[key]["score"])
        out = "{} @ {}".format(scorefmt(gamedata, "awayTeam"),
                                    scorefmt(gamedata, "homeTeam"),
                               )
    
    if "Phoenix Suns" in out:
        suns_emoji = "☀️" if emoji else "*"
        out = f"{suns_emoji} : " + out
    return out


def get_scores(split="\n", emoji=False, abbr=False):
    basketball_emoji = "🏀" if emoji else ""
    payload = ""
    board = scoreboard.ScoreBoard()
    payload += f"{basketball_emoji} Scoreboard for " + board.score_board_date + split
    payload += "=" * 30 + split

    games = board.games.get_dict()
    for game in games:
        try:
            res = game_data(game["gameId"], emoji, abbr)
            payload += res + split
        except:
            payload += split
    return payload


class NBAApp(rumps.App):
    def __init__(self):
        super(NBAApp, self).__init__("NBA Scores")
        self.menu = ["Loading..."]
        self.timer = rumps.Timer(self.update_scores, 30)
        self.timer.start()
        self.update_scores(None)  # Immediately update scores on initialization.

    @rumps.clicked("Loading...")
    def placeholder(self, _):
        pass  # This function does nothing, but is needed for the menu item to be clickable.

    def update_scores(self, _):
        #print('Updating scores...')
        scores = get_scores().split('\n')
        self.menu.clear()
        for score in scores[:-1]:  # Ignore the last score for the menu.
            self.menu.add(rumps.MenuItem(score))
        quit_button = rumps.MenuItem("Quit App", callback=lambda _: rumps.quit_application())
        self.menu.add(quit_button)
        if scores:  # Only update title if scores were fetched.
            scores = get_scores(abbr=True).split('\n')
            scores = list(filter(lambda x: x != '', scores))
            self.title = scores[-1]


if __name__ == "__main__":
    NBAApp().run()
