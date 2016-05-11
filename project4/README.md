# Udacity Project Design a Game - Connect 4

## Project 4 (Now 6) - Full Stack Web Developer Nanodegree
by Eric Ni, in fulfillment of Udacity's [Full-Stack Web Developer Nanodegree](https://www.udacity.com/course/nd004)

## Set-Up Instructions:
1.  Update the value of application in app.yaml to the app ID you have registered in the App Engine admin console and would like to use to host your instance of this sample.
1.  Run the app with the devserver using dev_appserver.py DIR, and ensure it's running by visiting the API Explorer - by default localhost:8080/_ah/api/explorer.
1.  (Optional) Generate your client library(ies) with the endpoints tool.
 Deploy your application.


##Game Instructions:
Connect 4 is a 2-player board game. Players take turn dropping their pieces into a grid. Players can choose which column their piece goes into, but not the row. Each piece will occupy the lowest available space in the column chosen. Players cannot pick a column that has been filled with pieces. The objective of the game is for a player to connect 4 of their own pieces, either vertically, horizontally, or diagonally. There is no score to keep track of throughout the game. The first player to Connect 4 wins.

##Files Included:
 - api.py: Contains endpoints.
 - app.yaml: App configuration.
 - cron.yaml: Cronjob configuration.
 - main.py: Handler for taskqueue handler.
 - models.py: Entity and message definitions including helper methods.
 - utils.py: Helper function for retrieving ndb.Models by urlsafe Key string. Also includes all the game logic

##Endpoints Included:
 - **create_user**
    - Path: 'user'
    - Method: POST
    - Parameters: user_name, email
    - Returns: Message confirming creation of the User.
    - Description: Creates a new User. user_name provided must be unique. Will raise a ConflictException if a User with that user_name already exists.

 - **new_game**
    - Path: 'game'
    - Method: POST
    - Parameters: player_1, player_2, board size (optional, default=1)
    - Returns: GameForm with initial game state.
    - Description: Creates a new Game. Both player names provided must correspond to an existing user - will raise a NotFoundException if not. Board size takes an integer value 1-3 which correspond to: (1 - Normal 6x7 board, 2 - Wide 6x11 board, 3 - Enormous 11x11 board). 1 is the default if none is chosen.

 - **get_game**
    - Path: 'game/{urlsafe_game_key}'
    - Method: GET
    - Parameters: urlsafe_game_key
    - Returns: GameForm with current game state.
    - Description: Returns the current state of a game.

 - **make_move**
    - Path: 'game/{urlsafe_game_key}'
    - Method: PUT
    - Parameters: urlsafe_game_key, user, move
    - Returns: GameForm with new game state.
    - Description: Makes a move for the specified player. Will raise a NotFoundException if the game specified does not exist. Will raise a BadRequestException if the user specified is not supposed to make the next move in the given game, or if the move made is invalid.

 - **get_user_games**
    - Path: 'user/games'
    - Method: GET
    - Parameters: user_name
    - Returns: GameForms for every GameForm with the specified user.
    - Description: Returns all ACTIVE games that a specified user is in.

 - **cancel_game**
    - Path: 'game/{urlsafe_game_key}'
    - Method: DELETE
    - Parameters: urlsafe_game_key
    - Returns: StringMessage confirming deletion
    - Description: Cancels a game. Raises a BadRequestException if the game is already over, or a NotFoundException if the game was not found.

 - **get_user_rankings**
    - Path: 'user/ranking'
    - Method: GET
    - Parameters: None
    - Returns: UserForms for all players with at least 1 game.
    - Description: Returns all user forms for players who have completed at least 1 game. This list is sorted by decreasing win percentage.

 - **get_game_history**
    - Path: 'game/{urlsafe_game_key}/history'
    - Method: GET
    - Parameters: urlsafe_game_key
    - Returns: StringMessage with the history of the game.
    - Description: Returns the game history of a game. This is represented as a list of tuples (player, move). Raises a NotFoundException if the game was not found.



##Models Included:
 - **User**
    - Stores the state of a user (unique user_name, and email address)

 - **Game**
    - Stores unique-game states. Associated with User model via KeyProperty.

##Forms Included:
 - **UserForm**
    - Representation of a User (name, email, wins, games played, win percentage).
 - **UserForms**
    - Container for multiple User Forms.
 - **GameForm**
    - Representation of a Game's state (urlsafe_key, player_1, player_2, next_move, board, game_over flag, message).
 - **GameForms**
    - Container for multiple Game Forms.
 - **NewGameForm**
    - Used to create a new game (player_1, player_2, boardsize)
 - **MakeMoveForm**
    - Used to make a move (move, player)
 - **StringMessage**
    - General purpose String container.