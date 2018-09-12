from PyQt5.QtCore import Qt, QEvent
from PyQt5.QtGui import QPainter
import GamePlayer


board = None

# optional function - if defined, is called when the game has started before the first move
# can be necessary, e.g. when having game options
def initGame():
    global board
    board = [ [ '_', '_' , '_' ] ,
              [ '_', '_' , '_' ] ,
              [ '_', '_' , '_' ]]


# paint the Game - obligatory function that must exist!
def paintGame(painter : QPainter):
    painter.fillRect(0, 0, 300, 300, Qt.white)

    pen = painter.pen()
    pen.setWidth(3)
    painter.setPen(pen)
    painter.drawLine(0, 100, 300, 100)
    painter.drawLine(0, 200, 300, 200)
    painter.drawLine(100, 0, 100, 300)
    painter.drawLine(200, 0, 200, 300)

    font = painter.font()
    font.setPixelSize(80)
    painter.setFont(font)

    for i in range(3):
        for j in range(3):
            if board[i][j] != '_':
                painter.drawText(i*100, j*100, 100, 100, Qt.AlignCenter, board[i][j])


playerSymbols = ['X', 'O']


# process an event for making a move - obligatory function that must exist!
# return a value in 0...playerCount-1 as the index of the next player to move
# return nothing or None if the move is not yet finished
# return -1 if the game is over
def makeMove(event : QEvent):
    currentPlayerIndex = GamePlayer.getCurrentPlayerIndex()
    if event.type() == QEvent.MouseButtonRelease:
        pos = event.pos()
        i = pos.x() // 100
        j = pos.y() // 100
        if i < 0 or i > 2 or j < 0 or j > 2:
            return None
        playerSymbol = playerSymbols[currentPlayerIndex]
        if board[i][j] == '_':
            board[i][j] = playerSymbol
            if hasWon(playerSymbol):
                GamePlayer.showMessageLaterForAll('Game Over', GamePlayer.getPlayerNames()[currentPlayerIndex] + ' has won the game.')
                return -1
            draw = True
            for i in range(3):
                for j in range(3):
                    if board[i][j] == '_':
                        draw = False
                        break
            if draw:
                GamePlayer.showMessageForAll('Game Over', 'The game is a draw.')
                return -1
            else:
                return (GamePlayer.getCurrentPlayerIndex() + 1) % GamePlayer.getPlayerCount()


# helper function
def hasWon(playerSymbol : str):
    for i in range(3):
        won = True
        for j in range(3):
            if board[i][j] != playerSymbol:
                won = False
                break
        if won:
            return True

    for j in range(3):
        won = True
        for i in range(3):
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
