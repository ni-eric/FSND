import logging
from google.appengine.ext import ndb
import endpoints


def get_by_urlsafe(urlsafe, model):
    """Returns an ndb.Model entity that the urlsafe key points to. Checks
        that the type of entity returned is of the correct kind. Raises an
        error if the key String is malformed or the entity is of the incorrect
        kind
    Args:
        urlsafe: A urlsafe key string
        model: The expected entity kind
    Returns:
        The entity that the urlsafe Key string points to or None if no entity
        exists.
    Raises:
        ValueError:"""
    try:
        key = ndb.Key(urlsafe=urlsafe)
    except TypeError:
        raise endpoints.BadRequestException('Invalid Key')
    except Exception, e:
        if e.__class__.__name__ == 'ProtocolBufferDecodeError':
            raise endpoints.BadRequestException('Invalid Key')
        else:
            raise

    entity = key.get()
    if not entity:
        return None
    if not isinstance(entity, model):
        raise ValueError('Incorrect Kind')
    return entity


def getEmptyBoard(rows, cols):
    """Returns an empty board of given # rows and columns.
    Note that the array-board is positioned 'sideways' relative to
    an actual board"""
    board = []
    for i in range(cols):
        board.append([None]*rows)
    return board


def makeMove(player, col, board):
    """Performs a new move"""
    # find lowest space in column
    lowest = -1
    for i in range(len(board[0])):
        if board[col][i] == None:
            lowest += 1
    # update value in board
    board[col][lowest] = player


def IsValidMove(col, board):
    """Checks if given column exists, and that there is an empty space there.
    Returns True if move is valid"""
    return not (col < 0 or col > len(board) or board[col][0] != None)


def check_winner(board):
    """Returns whether there is a winner. """
    cols = len(board)
    rows = len(board[0])
    # check rows
    for x in range(cols-3):
        for y in range(rows):
            if board[x][y]==board[x+1][y] and board[x][y]==board[x+2][y] \
                    and board[x][y]==board[x+3][y] and board[x][y]:
                return True
    # check columns
    for x in range(cols):
        for y in range(rows-3):
            if board[x][y]==board[x][y+1] and board[x][y]==board[x][y+2] \
                    and board[x][y]==board[x][y+3] and board[x][y]:
                return True
    # check / diagonals
    for x in range(cols-3):
        for y in range(3, rows):
            if board[x][y]==board[x+1][y-1] and board[x][y]==board[x+2][y-2] \
                    and board[x][y]==board[x+3][y-3] and board[x][y]:
                return True
    # check \ diagonals
    for x in range(cols-3):
        for y in range(rows-3):
            if board[x][y]==board[x+1][y+1] and board[x][y]==board[x+2][y+2] \
                    and board[x][y]==board[x+3][y+3] and board[x][y]:
                return True
    return False


def check_full(board):
    """Return True if there are no empty spaces left. """
    cols = len(board)
    rows = len(board[0])
    for x in range(cols):
        for y in range(rows):
            if not board[x][y]:
                return False
    return True
