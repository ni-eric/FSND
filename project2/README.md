## Project 2 - Full Stack Web Developer Nanodegree
by Eric Ni, in fulfillment of Udacity's [Full-Stack Web Developer Nanodegree](https://www.udacity.com/course/nd004)


####Requires:
[Vagrant](http://www.vagrantup.com/)

[VirtualBox](https://www.virtualbox.org/wiki/Downloads)

[Python 2.7](https://www.python.org/download/releases/2.7.7/)


####Running this program:
```bash
#clone this repo
git clone https://github.com/nihaitian/FSND.git

cd project2/
vagrant up
vagrant ssh

# You should now be in the vagrant VM
cd /vagrant
# initialize postgreSQL database
psql
\i tournament.sql
\q

# run tests
python tournament_test.py
```