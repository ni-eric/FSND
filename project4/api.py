import endpoints
from protorpc import remote, messages
from google.appengine.ext import ndb

from models import User, Game
from models import StringMessage, NewGameForm, GameForm, MakeMoveForm,\
    GameForms, UserForm, UserForms
from utils import get_by_urlsafe, check_winner, check_full, IsValidMove,\
    makeMove

NEW_GAME_REQUEST = endpoints.ResourceContainer(NewGameForm)
GET_GAME_REQUEST = endpoints.ResourceContainer(
    urlsafe_game_key=messages.StringField(1),)
MAKE_MOVE_REQUEST = endpoints.ResourceContainer(
    MakeMoveForm,
    urlsafe_game_key=messages.StringField(1),)
USER_REQUEST = endpoints.ResourceContainer(user_name=messages.StringField(1),
                                           email=messages.StringField(2))


@endpoints.api(name='connect_four', version='v3')
class ConnectFourAPI(remote.Service):

    """Game API"""
    @endpoints.method(request_message=USER_REQUEST,
                      response_message=StringMessage,
                      path='user',
                      name='create_user',
                      http_method='POST')
    def create_user(self, request):
        """Create a User. Requires a unique username"""
        if User.query(User.name == request.user_name).get():
            raise endpoints.ConflictException(
                'A User with that name already exists!')
        user = User(name=request.user_name, email=request.email)
        user.put()
        return StringMessage(message='User {} created!'.format(
            request.user_name))

    @endpoints.method(request_message=NEW_GAME_REQUEST,
                      response_message=GameForm,
                      path='game',
                      name='new_game',
                      http_method='POST')
    def new_game(self, request):
        """Creates new game"""
        player_1 = User.query(User.name == request.player_1).get()
        player_2 = User.query(User.name == request.player_2).get()
        board_size = request.board_size
        if not player_1:
            raise endpoints.NotFoundException(
                'Player 1 does not exist!')
        elif not player_2:
            raise endpoints.NotFoundException(
                'Player 2 does not exist!')

        game = Game.new_game(player_1.key, player_2.key, board_size)

        return game.to_form('New game started. Good luck, have fun!')

    @endpoints.method(request_message=GET_GAME_REQUEST,
                      response_message=GameForm,
                      path='game/{urlsafe_game_key}',
                      name='get_game',
                      http_method='GET')
    def get_game(self, request):
        """Return the current game state."""
        game = get_by_urlsafe(request.urlsafe_game_key, Game)
        if game:
            return game.to_form('Game found.')
        else:
            raise endpoints.NotFoundException('Game not found!')

    @endpoints.method(request_message=MAKE_MOVE_REQUEST,
                      response_message=GameForm,
                      path='game/{urlsafe_game_key}',
                      name='make_move',
                      http_method='PUT')
    def make_move(self, request):
        """Makes a move. Returns a game state with message"""
        game = get_by_urlsafe(request.urlsafe_game_key, Game)
        if not game:
            raise endpoints.NotFoundException('Game not found!')
        if game.game_over:
            raise endpoints.NotFoundException('Game is already over!')

        user = User.query(User.name == request.user_name).get()
        if user.key != game.next_move:
            raise endpoints.BadRequestException('It\'s not your turn!')

        move = request.move
        if not IsValidMove(move, game.board):
            raise endpoints.BadRequestException('Invalid move!')

        # Game history is a list of which player put pieces into which column.
        # Since the list is chronological, a game can be recreated using only
        # this information.
        if user.key == game.player_1:
            piece = '1'
            game.next_move = game.player_2
            game.history.append((game.player_1, move))
        else:
            piece = '2'
            game.next_move = game.player_1
            game.history.append((game.player_2, move))

        makeMove(piece, move, game.board)

        winner = check_winner(game.board)
        if not winner and check_full(game.board):
            game.tie_game()
        if winner:
            game.end_game(user.key)
        game.put()
        return game.to_form('board updated!')

    @endpoints.method(request_message=USER_REQUEST,
                      response_message=GameForms,
                      path='user/games',
                      name='get_user_games',
                      http_method='GET')
    def get_user_games(self, request):
        """Return all User's active games"""
        user = User.query(User.name == request.user_name).get()
        if not user:
            raise endpoints.BadRequestException('User not found!')
        games = Game.query(ndb.OR(Game.player_1 == user.key,
                                  Game.player_2 == user.key)).\
            filter(Game.game_over == False)
        return GameForms(items=[game.to_form() for game in games])

    @endpoints.method(request_message=GET_GAME_REQUEST,
                      response_message=StringMessage,
                      path='game/{urlsafe_game_key}',
                      name='cancel_game',
                      http_method='DELETE')
    def cancel_game(self, request):
        """Cancel a game. Cannot cancel completed games"""
        game = get_by_urlsafe(request.urlsafe_game_key, Game)
        if game and not game.game_over:
            game.key.delete()
            return StringMessage(message='Game with key: {} canceled.'.
                                 format(request.urlsafe_game_key))
        elif game and game.game_over:
            raise endpoints.BadRequestException('Game is already over!')
        else:
            raise endpoints.NotFoundException('Game not found!')

    @endpoints.method(response_message=UserForms,
                      path='user/ranking',
                      name='get_user_rankings',
                      http_method='GET')
    def get_user_rankings(self, request):
        """Return all Users ranked by their win percentage"""
        users = User.query(User.games_played > 0).fetch()
        users = sorted(users, key=lambda x: x.win_percentage, reverse=True)
        return UserForms(items=[user.to_form() for user in users])

    @endpoints.method(request_message=GET_GAME_REQUEST,
                      response_message=StringMessage,
                      path='game/{urlsafe_game_key}/history',
                      name='get_game_history',
                      http_method='GET')
    def get_game_history(self, request):
        """Return a Game's move history"""
        game = get_by_urlsafe(request.urlsafe_game_key, Game)
        if not game:
            raise endpoints.NotFoundException('Game not found')
        return StringMessage(message=str(game.history))


api = endpoints.api_server([ConnectFourAPI])
