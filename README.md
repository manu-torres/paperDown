# paperDown

A python3 tool to download articles from Scopus to your local machine. It stores all the articles on a sqlite database.

## How to install

First clone the repository with

```
git clone https://github.com/manu-torres/paperDown.git
```

Once the files are on your machine, open a terminal on the same directory and install the dependencies with 

```
pip install -r requirements.txt
```

You will also need a way to execute scripts periodically, on linux [cron](https://en.wikipedia.org/wiki/Cron) should always be avaible. The script **does not** work on windows (yet).

Next, run install.py with the python interpreter to create the database at the specified path. The installer will prompt you to introduce the path to the database file and your API key.

```
#You may be able to run the script with python rather than python3
python3 install.py
```

You can move the database file to another location after creating it, but remember to change the path at config.json so that the scripts are aware of the change. The rest of the files (scripts and config.json) must be in the same directory, but you can move the directory itself. If you skipped to add the API key on the installation, you can also add it or change it at config.json at any time.

Once the database has been created and it is at the desired location, you have to add some search terms to query the scopus API. After that is done, you then have to execute the script to start downloading the data.

## manageDatabase.py

This script allows you to perform some basic operations with the database. If you execute the script whith the following parameters it will add the term "2020" to the list.

```
python3 manageDatabase.py add 2020
```

You can then check if the term was added to the database with

```
python3 manageDatabase.py list
```

This command also lets us see how many articles we have downloaded so far (none).

If you run the script without parameters, or with the help parameter, you can see all the available actions.

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

### Examples

```
#Download all papers published in 2020
python3 manageDatabase.py add 2020

#Download all papers containing the word depression on the keywords
python3 manageDatabase.py add depression

#Download all papers containing BOTH depression AND anxiety
python3 manageDatabase.py add "depression anxiety"

#Download all papers containing EITHER depression OR anxiety
python3 manageDatabase.py add "depression OR anxiety"

#Download all papers containing the literal sentence "depression and anxiety"
python3 manageDatabase.py add "{depression and anxiety}"
```

## downloadData.py

This is the script that actually downloads the data. Once there are search terms on the database you can execute it to download a few papers.

```
python3 downloadData.py #Can take a couple of minutes

#Check if the papers have been downloaded
python3 manageDatabase.py list
```

Since the response time from the API is quite long, it is designed to download only a few articles every time it is called. Because of this, you must run the script every few minutes.

In linux, you can add the following line to your crontab file

```
crontab -e #To edit the crontab for the current user

#Make sure to send the output to /dev/null or to a log file
#since the script is designed to generate usefull error information.
*/2 * * * * python3 /pathToScript/downloadData.py >> /dev/null 2>&1
```

It is not recommended that you execute the script more often than once every two minutes, since it can take a while to get the data.
