from flask import render_template, redirect, url_for, request, flash
from flask_paginate import Pagination, get_page_parameter
from GameFinder import app
from GameFinder.GameFindermain.forms import GameFinderForm
from GameFinder.GameFindermain.utils import recommend_games


@app.route('/', methods=['GET', 'POST'])
@app.route("/home/", methods=['GET', 'POST'])
def home():
    form = GameFinderForm()
    if request.method == 'POST':
        if form.validate_on_submit():

            return redirect(url_for('search', username=form.username.data, numplayers=form.numplayers.data,
                                    bestonly=form.bestonly.data, hideplayed=form.hideplayed.data,
                                    minimumcomplexity=form.minimumcomplexity.data,
                                    maximumcomplexity=form.maximumcomplexity.data))
        else:
            flash("Invalid username, please try again.")
            return render_template('home.html', title='Gamefinder', form=form)
    else:

        return render_template('home.html', title='Gamefinder', form=form)


@app.route("/search/<string:username>/<int:numplayers>/<bestonly>/<hideplayed>/<minimumcomplexity>/<maximumcomplexity>/"
    , methods=['GET', 'POST'])
def search(username, numplayers, bestonly="False", hideplayed="False", minimumcomplexity=0, maximumcomplexity=5):
    form = GameFinderForm()

    if request.method == 'POST':
        if form.validate_on_submit():

            return redirect(url_for('search', username=form.username.data, numplayers=form.numplayers.data,
                                    bestonly=form.bestonly.data, minimumcomplexity=form.minimumcomplexity.data,
                                    maximumcomplexity=form.maximumcomplexity.data, hideplayed=form.hideplayed.data))
        else:
            flash("Invalid username, please try again.")
            return render_template('home.html', title='GameFinder', form=form)
    else:

        # convert strings from URL to booleans
        bestonly = bestonly == "True"
        hideplayed = hideplayed == "True"

        # query BGG for user's games & sort them
        games = recommend_games(int(numplayers), username, bestonly, hideplayed,
                                int(minimumcomplexity), int(maximumcomplexity))

        # handling if user does not exist or if they own no games
        if games is None or len(games) == 0:
            return render_template("nogames.html", title=f'Could not find games for {username} :(', form=form,
                                   username=username)
        # pagination
        page = request.args.get(get_page_parameter(), type=int, default=1)
        pagination = Pagination(page=page, total=len(games), show_single_page=False, per_page=15)

        return render_template('searchresults.html', title=f"Recommendations for {username}",
                               games=games, form=form, pagination=pagination)


@app.route("/about/", methods=["GET"])
def about():
    return render_template("about.html")


# error handling
@app.errorhandler(404)
def page_not_found(e):
    error = "Sorry, I wasn't able to find that page you're looking for."
    return render_template('error.html', error=error), 404


@app.errorhandler(403)
def forbidden(e):
    error = "Sorry, you don't have access to this page."
    return render_template('error.html', error=error), 403


@app.errorhandler(500)
def servererror(e):
    error = "Sorry, something went wrong on our end. Please try again."
    return render_template('error.html', error=error), 500

    # TODO about/contact pages
