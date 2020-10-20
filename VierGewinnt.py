import math

from PyQt5.QtCore import Qt, QEvent
from PyQt5.QtGui import QPainter
import GamePlayer

cols = 7
rows = 7 # TODO: There actually 6 draw
board = [["_" for y in range(rows)] for x in range(cols)]


# optional function - if defined, is called when the game has started before the first move
# can be necessary, e.g. when having game options
def initGame():
    pass
    # global board
    # board = [["_" for x in range(cols)] for y in range(rows)]


# paint the Game - obligatory function that must exist!
# change here the size of the board!!!!
def paintGame(painter: QPainter):
    global board
    painter.fillRect(0, 0, 700, 700, Qt.white)  # ERSCHAFFT FREIEN PLATZ OBEN
    painter.fillRect(0, 100, 700, 600, Qt.blue)  # FUELLT RECHTECK AUS

    pen = painter.pen()  # STIFT WIRD ERZEUGT
    pen.setWidth(3)
    painter.setPen(pen)  # PEN WIRD ANGESETZ

    # We offset the rows by one to leave space to "throw the chips"
    for y in range(2, rows):
        y1 = y * 100
        x1 = 0
        x2 = 700
        painter.drawLine(x1, y1, x2, y1)  # HORIZONTALE LINIEN


    for x in range(1, cols):
        y1 = 100
        y2 = 700
        x1 = x * 100
        painter.drawLine(x1, y1, x1, y2)  # VERTIKALE LINIEN

    font = painter.font()
    font.setPixelSize(80)  # PIXELGROESSE VON FONT
    painter.setFont(font)

    for y in range(rows):  # BERECHNET STELLE IM FELD AUF X EBENE
        for x in range(cols):  # BERECHNET STELLE IM FELD AUF Y EBENE
            if board[x][y] != '_':
                painter.drawText(x * 100, y * 100, 100, 100, Qt.AlignCenter, board[x][y])


playerSymbols = ['X', 'O']


# process an event for making a move - obligatory function that must exist!
# return a value in 0...playerCount-1 as the index of the next player to move
# return nothing or None if the move is not yet finished
# return -1 if the game is over
def makeMove(event: QEvent):  # DEFINITON DER FUNKTION MAKE A MOVE
    currentPlayerIndex = GamePlayer.getCurrentPlayerIndex()

    if event.type() == QEvent.MouseButtonRelease:  # BERECHNET FELD AN DER MOUSE LOSGELASSEN WURDE
        pos = event.pos()
        x = math.floor(pos.x() / 100)
        y = math.floor(pos.y() / 100)
        print("==================")
        print("x", x)
        print("y", y)
        if y != 0 or (x < 0 or x > cols - 1):  # CHECK OB AUSSERHALB DES FELDES GEDRÜCKT WURDE WENN NICHT ZU
            return None

        playerSymbol = playerSymbols[currentPlayerIndex]
        # If the place at the top if not empty, then it means that the
        # whole column is occupy
        if board[x][1] == '_':
            # ZUGEWIESEN
            for yToCheck in range(rows - 1, 0, -1):
                # if board[y + 1][x] == '_':
                if board[x][yToCheck] == '_':
                    board[x][yToCheck] = playerSymbol
                    break

            # board[y][x] = playerSymbol
            # CHANGE FOR VIERGEWINNT WENN FELD DRUNTER FREI IST; DANN J ERHOEHEN
            # UND NÄCHSTEN CHECKEN

            if hasWon(playerSymbol):
                GamePlayer.showMessageLaterForAll('Game Over', GamePlayer.getPlayerNames()[
                    currentPlayerIndex] + ' has won the game.')
                return -1

            draw = True
            for y in range(rows):
                for x in range(cols):
                    if board[y][x] == '_':
                        draw = False
                        break
            if draw:
                GamePlayer.showMessageForAll('Game Over', 'The game is a draw.')
                return -1
            else:
                return (GamePlayer.getCurrentPlayerIndex() + 1) % GamePlayer.getPlayerCount()


# helper function
def hasWon(playerSymbol: str):  # PLAYERSYMBOL = X/0 #SCHAUT OB DREI GLEICHE SYMBOLE
    # VORLIEGEN
    return (checkHorizontalMatch(playerSymbol) or checkVerticalMatch(playerSymbol))




def checkVerticalMatch(playerSymbol: str):
    counter = 0
    for y in range(rows):
        for x in range(cols):
            if counter > 3:
                return True
            if x == cols - 1 and y == rows - 1 and counter < 4:
                return False
            if board[y][x] == playerSymbol:
                counter += 1
            if board[y][x] != playerSymbol:
                counter = 0

    return False

def checkHorizontalMatch(playerSymbol: str):
    counter = 0
    for x in range(cols):
        for y in range(rows):
            if counter > 3:
                return True
            if x == cols - 1 and y == rows - 1 and counter < 4:
                return False
            if board[y][x] == playerSymbol:
                counter += 1
            if board[y][x] != playerSymbol:
                counter = 0

    return False

# optional function - only relevant for network mode
# if not defined, the game will be over if a player leaves the game (e.g. by network interruption)
# must return the index of the next player to move or -1 if the game is over
# the next player to move will be probably the currently moving player in most cases but consider
# the case playerIndex == GamePlayer.getCurrentPlayerIndex(), i.e. the currently moving player left the game!!!
# is only called for the currently moving player or the next player if the moving player left the game
# playerLeftGame and makeMove must not return the index of players who already left the game!!!
# def playerLeftGame(playerIndex : int):
#     return -1


# obligatory call to start the game - must be the last command in your program because it will not return!
GamePlayer.run(
    playerTitles=playerSymbols,
)
