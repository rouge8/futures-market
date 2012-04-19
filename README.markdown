# Futures Market

by Andy Freeland

## Getting Started

### Requirements

The Futures Market requires `Django==1.3`, `tornado==2.0`, and `PyYAML`. These can be easily installed with pip: `pip install -r requirements.txt`.

### Running

The Futures Market can be run with the `runserver-dev` script, which uses Django's management command functionality to run the application on port 8000 with the Tornado server. This is fine for testing purposes, but for production use see **Deployment**. To setup a development database, run the `setup-dev` script.

### Usage

- `http://hostname/admin/` will bring you to the admin interface where you can edit objects.
- `http://hostname/` will take you to the interface to create markets.
- `http://hostname/marketname/` will take you to the market manager view.
- `http://hostname/marketname/tradername/` will take you to an individual trader portfolio.

## Data

Data is stored in an SQLite database called futures-market.db. Once the market is running, [YAML](http://en.wikipedia.org/wiki/YAML)-formatted data can be uploaded. An example can be found in `data/carleton.yaml`.

## Deployment

For installing all of the server software, see `docs/server-setup.txt`. Copy `conf/nginx.conf` to `/etc/nginx/nginx.conf`.

nginx can also be configured for multiple processes, with some information about that at <http://www.hyperionreactor.net/blog/running-tornado-production> and <http://www.tornadoweb.org/documentation/overview.html#running-tornado-in-production>.

- Run `setup-production` to setup the database and collect the static files.

- Run `runserver-production` to start the server. `runserver-production` takes an optional port number as an argument and defaults to port 8000. The included nginx.conf is set to listen on ports 8000 and 8001.

The URL prefix in production can be configured in `futures_market/settings_production.py`. This lets you host the market at URLs like `http://hostname/markets/` rather than `http://hostname/`.

## Internals

The Futures Market is built using [Django](https://www.djangoproject.com/) and uses [Tornado](http://www.tornadoweb.org/) as its server. [jQuery](http://jquery.com/) and [flot](http://code.google.com/p/flot/) are used to plot graphs and do refresh the data.

The `futures_market` directory contains the project itself. The only files that matter here are `settings.py`, containing all of the application settings, and `urls.py` which maps urls to applications.

`templates` contains the templates, HTML files using the Django Templating Language.

`market` is the actual market application. `static` contains static files (CSS/JS). The CSS uses the [inuit.css framework](http://csswizardry.com/inuitcss/) with a very small `screen.css` for other styling. `management` contains a `runtornado.py` command for Django's management commands. This wraps the application for serving by the Tornado server.

`models` contains all of the data models for Holding, Market, Order, Stock, Trader.

Of the files in `market`, `urls.py` maps urls to views. `views.py` is where the actual logic of the market lies.
