# exchange_rates

## Setup

The first thing to do is to clone the repository:

```sh
$ git clone https://github.com/AndreSoftwareDeveloper/exchange_rates.git
$ cd exchange_rates/
```

Create a virtual environment to install dependencies in and activate it:

```sh
$ python3 -m venv virtualenv
$ source virtualenv/bin/activate
```

Then install the dependencies:

```sh
(virtualenv)$ pip install -r requirements.txt
```
Note the `(virtualenv)` in front of the prompt. This indicates that this terminal
session operates in a virtual environment set up by `virtualenv`.

Once `pip` has finished downloading the dependencies:
```sh
(virtualenv)$ redis-server
(virtualenv)$ cd exchange_rates/
(virtualenv)$ py manage.py qcluster
(virtualenv)$ py manage.py runserver
```
And navigate to `http://127.0.0.1:8000/currencies/`.
