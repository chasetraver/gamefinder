Website I made in 2021 to help figure out what the best board games are to play given a collection and a number of players.
Live at https://chasegamefinder.herokuapp.com/ as of 9/14/2021
Website *heavily* relies on the BGG XML API to get the data necessary. (https://boardgamegeek.com/wiki/page/BGG_XML_API2)
As a result of this, any person searching their collection would have to have a Board Game Geek account, and have their games already uploaded to there.

Launch via executing 'run.py'
First search may take a few minutes, as the program will download the thumbnails to the static folder for each game it does not have a thumbnail for yet. This is especially true is the first game collection ran is particularly large.

made using Python 3.9 with the following libraries:
Flask 2.0.1
Flask-Bootstrap 3.3.7.1
Flask-WTF 0.15.1
Jinja2 3.0.1
MarkupSafe 2.0.1
WTForms 2.3.3
beautifulsoup4 4.9.3
flask-paginate 0.8.1
requests 2.25.1
urllib3 1.26.5

All the necessary image credits for this project are on the about page, but to repeat them:
All images of board games with the exception of the GameFinder "logo" come from Board Game Geek.
The wood texture background was from myfreetextures.com
Everything else was free to use commercial license.
