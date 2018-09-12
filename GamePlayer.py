import Internal.Main as Main

############ !!!!!!!!! DO NOT CHANGE THIS FILE !!!!!!!!! ############

# runs the game - must be called as last code line in your game because it will return after your game has finished
# Options:
# gameName           : name for the game - if None, it is derived from the filename
# minPlayerCount     : minimum number of players
# maxPlayerCount     : maximum number of players
# players        : if a list with strings: use these player names in local mode (can be adapted in settings dialog)
#                      if an integer n: same as above and use "player 1", ..., "player n" as player names
#                      if None: same as above with n=minPlayerCount
# autoStart          : if True, start game with default options
# playerTitles       : list of strings for the player titles, e.g. in many cases like chess the player colors
#                      the length of the list must be maxPlayerCount
#                      if None, no titles will be shown in the GUI
# titlesAreChoosable : if the titles can be choosen and are not bound to the order like for chess (white always begins)
# hostGame           : if the game should be immediately be hosted on the server
# hostingName        : the name for hosting if the game file is started directly
#                      if None the last used name or the login name is used
# sessionSecret      : a secret if the game is started directly and hosted on the server
#                      only players with the same session secret will see the session and can join
def run(gameName=None, minPlayerCount=2, maxPlayerCount=2, players=None, autoStart=False, playerTitles=None, \
        titlesAreChoosable=False, hostGame=False, hostingName=None, sessionSecret=None):
    Main.run(locals())

# get the number of players
def getPlayerCount():
    return Main.getGameObject().getPlayerCount()

# get a list of the player names
def getPlayerNames():
    return Main.getGameObject().players

# get a list of the player titles
# is actually the parameter of GamePlayer.run but maybe reordered and shortened to player count length - might be None!
def getPlayerTitles():
    return Main.getGameObject().playerTitles

# get the index of the currently moving player
def getCurrentPlayerIndex():
    return Main.getGameObject().currentPlayerIndex

# show info message by calling from makeMove
# is shown after makeMove has returned and game has been painted again
# title is shown in the message box title bar
def showMessageLater(title, text):
    return Main.showMessageLater(title, text, all=False)

# show info message for all players participating by calling from makeMove
# is shown after makeMove has returned and game has been painted again
# title is shown in the message box title bar
# in local mode same as showMessageLater!
def showMessageLaterForAll(title, text):
    return Main.showMessageLater(title, text, all=True)


##################### functions for querying options #####################

# layout of return object for option functions
# class Option:
#     def __init__(self):
#         self.value = None

# adds a checkbox option - text will be shown next to the checkbox
# value will be True if checked and False otherwise
def addCheckBoxOption(text: str, defaultValue: bool = False):
    return Main.addOption(('checkBox', text, defaultValue))

# add several radio buttons - values must be a list of strings which will be shown next to the buttons
# text is an optional string shown above the buttons
# value will be the text of the selected button
def addRadioButtonsOption(values, text: str = ''):
    return Main.addOption(('radioButtons', (values, str), text))

##################### releveant for network mode only! #####################

# in local mode same as getCurrentPlayerIndex(), in network mode the index of the player
# who runs the participating program, thus it does not change in network mode throughout the game!
def getThisPlayerIndex():
    Main.getGameObject().thisPlayerIndex

# when running this file directly the directory will be searched for games and you can select among the found games
if __name__ == "__main__":
    Main.selectGame()
