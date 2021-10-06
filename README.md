# Daily Python Tip Online
 Have you ever heard of Daily Python Tip? It's a Twitter account that posts one python tip per day, run by @karlafej and @simecek.  The goal is to make a web app to make it easier to navigate the collection of tips
## Instructions
- Run ```python manage.py runapscheduler``` to schedule the job that syncs
 the tweets to the database. The server must be running for the job to run
  every three(3) hours. You can also go to the django admin
   platform to run the ```fetch_tweets``` job anytime you want
## Keys needed in ```.env``` file to be placed in root of directory
- DATABASE_URL ```string```
- SECRET_KEY ```string```
- DEBUG ```boolean```
- CONSUMER_KEY ```string```
- CONSUMER_SECRET ```string```
- BEARER_TOKEN ```string```
- ACCESS_TOKEN ```string```
- ACCESS_TOKEN_SECRET ```string```