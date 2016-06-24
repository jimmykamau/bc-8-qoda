## QODA

Qoda is a web-based pair-programming platform that helps teams work remotely in real-time. It is written in Python by using the Flask framework is powered by PostgreSQL and Redis. It also utilizes [gevent](http://www.gevent.org/index.html) for networking. Check out the live version [here](http://qoda.apps.winguh.com) 


### Features

* Real-time chat
* Real-time web-based code editor
* Session-based coding sessions


### Local Installation

1. Clone this repository

	`git clone https://github.com/jimmykamau/bc-8-qoda.git`

2. cd into the repo and create a Python virtual environment
	`cd bc-8-qoda`
	`virtualenv env`

2. Install dependencies
	`pip install -r requirements.txt`

3. Create a [PostgreSQL](https://www.postgresql.org/) database and add its endpoint to your path as `DATABASE_URL`
	`export DATABASE_URL="postgresql:///qoda"`

4. Initialize your PostgreSQL database and migrate the tables
	`python manage.py db init`
	`python manage.py db migrate`
	`python manage.py db upgrade`

5. Create a [Redis](http://redis.io/) instance, add its endpoint to your path and start listening to connections
	`export REDIS_URL="redis://localhost:6379/0"`
	`redis-server`

6. Initialize your database and migrate the database models
	`python manage.py db init`
	`python manage.py db upgrade`

7. Run the server
	`gunicorn -k flask_sockets.worker app:app`


## Issues

* Isolated sessions haven't been implemented. All activity can therefore be viewed by everyone who is logged in


## To do

* Create functionality to enable isolated sessions
* Create functionality to add users to isolated sessions 
