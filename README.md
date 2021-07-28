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

Next, create a plain text file named config.json, and add the following contents to it.

```
{
  "databasePath": "[path where you want to store the database]": ,
  "databaseExists": "False", 
  "APIkey" : "[your API key]"
}
```

"databaseExists" must always be "False", the other two values .

Next, run install.py with the python interpreter to create the database at the specified path.

You can move the database file to another location after creating it, but remember to change the path at config.json so that the scripts are aware of the change. The rest of the files (scripts and config.json) must be in the same directory, but you can move the directory itself.

Once the database has been created and it is at the desired location, you have to add some search terms to query the scopus API.

## manageDatabase.py


