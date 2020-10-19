import math

from PyQt5.QtCore import Qt, QEvent
from PyQt5.QtGui import QPainter
import GamePlayer

board = None
cols = 7
rows = 6


# optional function - if defined, is called when the game has started before the first move
# can be necessary, e.g. when having game options
def initGame():
    global board
    board = [["_" for x in range(cols)] for y in range(rows)]


# HI

# paint the Game - obligatory function that must exist!
# change here the size of the board!!!!
def paintGame(painter: QPainter):
    painter.fillRect(0, 0, 700, 600, Qt.blue)  # FUELLT RECHTECK AUS

    pen = painter.pen()  # STIFT WIRD ERZEUGT
    pen.setWidth(3)
    painter.setPen(pen)  # PEN WIRD ANGESETZ
    for y in range(1, rows + 1):
        painter.drawLine(0, y * 100, 700, y * 100)
    # painter.drawLine(0, 200, 700, 200)
    # painter.drawLine(0, 300, 700, 300)
    # painter.drawLine(0, 400, 700, 400)
    # painter.drawLine(0, 500, 700, 500)
    # painter.drawLine(0, 600, 700, 600)  # HORIZONTALE LINIEN

    for x in range(1, cols + 1):
        painter.drawLine(x * 100, 0, x * 100, 600)
    # painter.drawLine(100, 0, 100, 600)
    # painter.drawLine(200, 0, 200, 600)
    # painter.drawLine(300, 0, 300, 600)
    # painter.drawLine(400, 0, 400, 600)
    # painter.drawLine(500, 0, 500, 600)
    # painter.drawLine(600, 0, 600, 600)
    # painter.drawLine(700, 0, 700, 600)          # VERTIKALE LINIEN

    font = painter.font()
    font.setPixelSize(80)                       # PIXELGROESSE VON FONT
    painter.setFont(font)

    for i in range(6):                          # BERECHNET STELLE IM FELD AUF X EBENE
        for j in range(7):                      # BERECHNET STELLE IM FELD AUF Y EBENE
            if board[i][j] != '_':
                painter.drawText(i * 100, j * 100, 100, 100, Qt.AlignCenter, board[i][j])


playerSymbols = ['X', 'O']


# process an event for making a move - obligatory function that must exist!
# return a value in 0...playerCount-1 as the index of the next player to move
# return nothing or None if the move is not yet finished
# return -1 if the game is over
def makeMove(event: QEvent):  # DEFINITON DER FUNKTION MAKE A MOVE
    currentPlayerIndex = GamePlayer.getCurrentPlayerIndex()

    if event.type() == QEvent.MouseButtonRelease:  # BERECHNET FELD AN DER MOUSE LOSGELASSEN WURDE
        pos = event.pos()
        i = math.floor(pos.x() / 100)
        j = math.floor(pos.y() / 100)
        if i < 0 or i > 5 or j < 0 or j > 6:  # CHECK OB AUSSERHALB DES FELDES GEDRÜCKT WURDE WENN NICHT ZU PLAYERSYMBOL
            return None

        playerSymbol = playerSymbols[currentPlayerIndex]
        if board[i][j] == '_':  # WENN STELLE X LEER DANN WIRD PLAYERSYMBOL AUF DEM BOARD ZUGEWIESEN
            board[i][j] = playerSymbol
            # CHANGE FOR VIERGEWINNT WENN FELD DRUNTER FREI IST; DANN J ERHOEHEN UND NÄCHSTEN CHECKEN

            if hasWon(playerSymbol):
                GamePlayer.showMessageLaterForAll('Game Over', GamePlayer.getPlayerNames()[
                    currentPlayerIndex] + ' has won the game.')
                return -1

            draw = True
            for i in range(6):
                for j in range(7):
                    if board[i][j] == '_':
                        draw = False
                        break
            if draw:
                GamePlayer.showMessageForAll('Game Over', 'The game is a draw.')
                return -1
            else:
                return (GamePlayer.getCurrentPlayerIndex() + 1) % GamePlayer.getPlayerCount()


# helper function
def hasWon(playerSymbol: str): #PLAYERSYMBOL = X/0 #SCHAUT OB DREI GLEICHE SYMBOLE VORLIEGEN
    for i in range(6):
        won = True
        for j in range(7):
            if board[i][j] != playerSymbol:
                won = False
                break
        if won:
            return True

    for j in range(7):
        won = True
        for i in range(6):
            if board[i][j] != playerSymbol:
                won = False
                break
        if won:
            return True

    if board[0][0] == playerSymbol and \
            board[1][1] == playerSymbol and \
            board[2][2] == playerSymbol:
        return True

    if board[2][0] == playerSymbol and \
            board[1][1] == playerSymbol and \
            board[0][2] == playerSymbol:
        return True


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
