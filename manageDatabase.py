#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#Este script permite realizar algunas operaciones basicas sobre la base de datos para poder incorporar y eliminar terminos de busqueda a la herramienta

import pathlib
import json
import sqlite3
import sys

Rutas = {}
Rutas["script"] = str(pathlib.Path(__file__).parent.resolve())
Rutas["config"] = Rutas["script"] + "/config.json"
Rutas["databaseSchema"] = Rutas["script"] + "/schema.sql"

try:
    with open(Rutas["config"], 'r') as file:
         Config = json.loads(file.read())
except:
    print("No config file available. Run install.py first.")
    quit()

if len(Config["databasePath"]) < 2:
    print("Database has not been created")
    quit()

conn = sqlite3.connect(Config["databasePath"])
c = conn.cursor()

c.execute("SELECT Busqueda FROM Registro")
Config["ListaTerminos"] = list(map(lambda x: x[0], c.fetchall()))

conn.close()


def Help():
    print("""
This script allows you to perform some basic operations with the database. The first command line parameter determines which action you want to perform. Some actions require a second parameter.
---------------------

Actions:
help: displays this message again

add: adds an expression to the database. Requires a second parameter, the expression itself as a string. If the expression contains spaces it must be put between quotes.

remove: removes an expression from the database. Requires a second parameter, the expression itself as a string. If the expression contains spaces it must be put between quotes.

list: lists the terms on the database.
          """)

def AddExpression(term):
    #Esta funcion añade una expresion de busqueda a la lista de terminos para descargar articulos que lo contienen. Recibe como parametro un string (la expresion)
    global Config
    
    term = str(term)
    
    if term not in Config["ListaTerminos"]:
        conn = sqlite3.connect(Config["databasePath"])
        c = conn.cursor()
        
        c.execute("INSERT INTO Registro (Busqueda) VALUES ('" + term + "')")
        conn.commit()
        
        conn.close()
        print(term + " added to the list of search terms")
    else:
        print("Term is already on the database. No change made.")
    
    
def RemoveExpression(term):
    #Esta funcion elimina la expresion de la base de datos
    global Config
    
    term = str(term)
    
    if term in Config["ListaTerminos"]:
        conn = sqlite3.connect(Config["databasePath"])
        c = conn.cursor()
        
        c.execute("DELETE FROM Registro WHERE Busqueda == '" + term + "'")
        conn.commit()
        
        conn.close()
        
        print(term + " removed from the list of search terms")
    else:
        print("Term is already on the database. No change made.")
    
def ListTerms():
    #Esta funcion lista los articulos descargados para cada busqueda
    conn = sqlite3.connect(Config["databasePath"])
    c = conn.cursor()
    
    c.execute("SELECT * FROM ResumenBusquedas ORDER BY Frecuencia DESC")
    Consulta = c.fetchall()
    
    conn.close()
    
    print("Terms in database to download articles:")
    print(Config["ListaTerminos"])
    
    if len(Consulta) > 1:
        print("-----------------")
        for i in range(len(Consulta)):
            print("Search term: " + str(Consulta[i][0]) + " (" + str(Consulta[i][1]) + " downloads)")
    else:
        print("No articles have been downloaded to the database")

if len(sys.argv) > 1:
    if sys.argv[1] == "list":
        ListTerms()
    elif sys.argv[1] == "add":
        if len(sys.argv) > 2:
            AddExpression(sys.argv[2])
        else:
            print("You must pass a valid search term")
    elif sys.argv[1] == "remove":
        if len(sys.argv) > 2:
            RemoveExpression(sys.argv[2])
        else:
            if len(Config["ListaTerminos"]) == 0:
                print("No search terms on the database. Nothing to delete")
            else:
                print("You must pass a valid search term that is on the database:")
                print(Config["ListaTerminos"])
    elif sys.argv[1] in ["help", "h"]:
        Help()
else:
    print("No action has been pased")
    Help()