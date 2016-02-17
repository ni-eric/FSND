## Project 2 - Full Stack Web Developer Nanodegree
by Eric Ni, in fulfillment of Udacity's [Full-Stack Web Developer Nanodegree](https://www.udacity.com/course/nd004)

A Catalog Application that provides categories of items, which have names, descriptions, and images. Provided is a user registration/authenication system via Google+. Logged in users are able to add, delete, and edit items.

Frontend design utilizes the Bootstrap framework, and backend uses PostgreSQL to manage the database.

####Requires:
[Vagrant](http://www.vagrantup.com/)

[VirtualBox](https://www.virtualbox.org/wiki/Downloads)

[Python 2.7](https://www.python.org/download/releases/2.7.7/)


####Usage:
```bash
#clone this repo
git clone https://github.com/nihaitian/FSND.git

cd project3/
vagrant up
vagrant ssh

# You should now be in the vagrant VM
cd /vagrant

# The database should be there already when you vagrant up
# But just in case it isn't, do this:
psql
\i catalog.sql
\q

# fill in the database with placeholder categories, items, and images
python initialize.py

# start the webserver on http://localhost:5000
python project.py
```
