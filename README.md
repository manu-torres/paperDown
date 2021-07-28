# paperDown
A python3 tool to download articles from Scopus to your local machine

# How to use

First clone the repository with

```
git clone https://github.com/manu-torres/paperDown.git
```

Once the files are on your machine, open a terminal on the same directory and install the dependencies with 

```
pip install -r requirements.txt
```

Next, open config.json with a text editor. There, you should see a key named "databasePath", with an empty value. Introduce the path where you want to create the database on your local file system. If you skip this step, the database will be created in the same directory where the files are. You may not want this to happen since the database can grow in size over time.

Next, run createDatabase.py with the python interpreter to create the database at the specified path.

You can move the database file to another location after creating it, but remember to change the path at config.json so that the scripts are aware of the change. The rest of the files (scripts and config.json) must be in the same directory, but you can move the directory itself.

Once the database has been created and it is at the desired location, you have to add some search terms to query the scopus API. 
