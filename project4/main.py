#!/usr/bin/env python

import webapp2
from google.appengine.api import mail, app_identity
from api import ConnectFourAPI
from models import User, Game


class SendReminderEmail(webapp2.RequestHandler):

    def get(self):
        """Send a reminder email to each User with an email who in in a game
        where it is their turn.
        Called every hour using a cron job"""
        users = User.query(User.email != None)
        app_id = app_identity.get_application_id()

        for user in users:
            games = Game.query(Game.next_move == user.key).\
                filter(Game.game_over == False)
            if games.count() > 0:
                subject = 'This is a reminder!'
                body = 'Hello {}, it is your turn to move in {} games. Their' \
                       ' keys are: {}'.\
                    format(user.name,
                           games.count(),
                           ', '.join(game.key.urlsafe() for game in games))
                # This will send test emails, the arguments to send_mail are:
                # from, to, subject, body
                mail.send_mail('noreply@{}.appspotmail.com'.format(app_id),
                               user.email,
                               subject,
                               body)


app = webapp2.WSGIApplication([
    ('/crons/send_reminder', SendReminderEmail)
])
