import random
from datetime import date
from protorpc import messages
from google.appengine.ext import ndb
from utils import getEmptyBoard


class User(ndb.Model):

    """User profile"""
    name = ndb.StringProperty(required=True)
    email = ndb.StringProperty(required=True)
    wins = ndb.IntegerProperty(default=0)
    games_played = ndb.IntegerProperty(default=0)

    @property
    def win_percentage(self):
        if self.games_played > 0:
            return float(self.wins)/float(self.games_played)
        else:
            return 0

    def to_form(self):
        return UserForm(name=self.name,
                        email=self.email,
                        wins=self.wins,
                        games_played=self.games_played,
                        win_percentage=self.win_percentage)

    def add_win(self):
        """Add a win"""
        self.wins += 1
        self.games_played += 1
        self.put()

    def add_played(self):
        """Add game played"""
        self.games_played += 1
        self.put()


class Game(ndb.Model):

    """Game object"""
    board = ndb.PickleProperty(required=True)
    boardsize = ndb.IntegerProperty(default=1)
    next_move = ndb.KeyProperty(required=True)
    player_1 = ndb.KeyProperty(required=True, kind='User')
    player_2 = ndb.KeyProperty(required=True, kind='User')
    game_over = ndb.BooleanProperty(required=True, default=False)
    winner = ndb.KeyProperty()
    history = ndb.PickleProperty(required=True)

    @classmethod
    def new_game(cls, player_1, player_2, boardsize):
        """Creates and returns a new game"""
        game = Game(boardsize=boardsize,
                    player_1=player_1,
                    player_2=player_2,
                    next_move=player_1)
        if boardsize == 1:
            # normal board
            game.board = getEmptyBoard(6, 7)
        elif boardsize == 2:
            # wide board
            game.board = getEmptyBoard(6, 11)
        else:
            # enormous board
            game.board = getEmptyBoard(11, 11)
        game.history = []
        game.put()
        return game

    def to_form(self, message=None):
        """Returns a GameForm representation of the Game"""
        form = GameForm(urlsafe_key=self.key.urlsafe(),
                        board=str(self.board),
                        player_1=self.player_1.get().name,
                        player_2=self.player_2.get().name,
                        next_move=self.next_move.get().name,
                        game_over=self.game_over,
                        message=message
                        )
        if self.winner:
            form.winner = self.winner.get().name
        return form

    def end_game(self, winner):
        """Ends the game and updates the winner"""
        self.winner = winner
        self.game_over = True
        self.put()
        loser = self.player_2 if winner == self.player_1 else self.player_1

        winner.get().add_win()
        loser.get().add_played()

    def tie_game(self):
        """Ends the game on a tie (indicated by full board)"""
        self.game_over = True
        self.put()

        self.player_1.get().add_played()
        self.player_2.get().add_played()


class UserForm(messages.Message):

    """User Form to represent a User"""
    name = messages.StringField(1, required=True)
    email = messages.StringField(2)
    wins = messages.IntegerField(3, required=True)
    games_played = messages.IntegerField(4, required=True)
    win_percentage = messages.FloatField(5, required=True)


class UserForms(messages.Message):

    """Returns multiple User Forms"""
    items = messages.MessageField(UserForm, 1, repeated=True)


class GameForm(messages.Message):

    """GameForm for outbound game state information"""
    urlsafe_key = messages.StringField(1, required=True)
    board = messages.StringField(2, required=True)
    player_1 = messages.StringField(3, required=True)
    player_2 = messages.StringField(4, required=True)
    next_move = messages.StringField(5, required=True)
    game_over = messages.BooleanField(6, required=True)
    winner = messages.StringField(7)
    message = messages.StringField(8)


class GameForms(messages.Message):

    """Returns multiple GameForms"""
    items = messages.MessageField(GameForm, 1, repeated=True)


class NewGameForm(messages.Message):

    """Used to create a new game"""
    player_1 = messages.StringField(1, required=True)
    player_2 = messages.StringField(2, required=True)
    board_size = messages.IntegerField(3, default=1)


class MakeMoveForm(messages.Message):

    """Used to make a move in an existing game"""
    user_name = messages.StringField(1, required=True)
    move = messages.IntegerField(2, required=True)


class StringMessage(messages.Message):

    """StringMessage-- outbound (single) string message"""
    message = messages.StringField(1, required=True)
