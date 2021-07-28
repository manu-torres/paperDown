# paperDown
A python3 tool to download articles from Scopus to your local machine

## How to install

First clone the repository with

```
git clone https://github.com/manu-torres/paperDown.git
```

Once the files are on your machine, open a terminal on the same directory and install the dependencies with 

```
pip install -r requirements.txt
```

Next, run install.py with the python interpreter to create the database at the specified path. The installer will prompt you to introduce the path to the database file and you API key.

You can move the database file to another location after creating it, but remember to change the path at config.json so that the scripts are aware of the change. The rest of the files (scripts and config.json) must be in the same directory, but you can move the directory itself.

Once the database has been created and it is at the desired location, you have to add some search terms to query the scopus API.

## manageDatabase.py

This script allows you to perform some basic operations with the database. If you execute the script whith the following parameters it will add the term "2020" to the list.

```
python3 manageDatabase.py add 2020

#You may be able to run the script with python rather than python3
```

You can then check if the term was added to the database with

```
python3 manageDatabase.py list
```

This command also lets us see how many articles we have downloaded so far (none).

If you run the script without parameters, or with the help parameter, you can see all the avaible actions.

```
python3 manageDatabase.py help
```

### Search terms

At the [R markdown report](https://manu-torres.github.io/TFGfunc/#Muestra) (Spanish only), you can see how to create valid search terms and how they are treated by the script that actually downloads the data, but basically, they follow the [Scopus Search API syntax](https://dev.elsevier.com/sc_search_tips.html). If the search expression contains spaces, then you must pass it between double quotes.

If you must use single quotes for your search, you must escape them. Otherwise you may end up performing a SQL injection to your own local database.

```
python3 manageDatabase.py add depression #Good

python3 manageDatabase.py add depression OR anxiety #Bad

python3 manageDatabase.py add "depression OR anxiety" #Good
```
