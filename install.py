#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#Este script crea el archivo de configuracion, la base de datos y añade algunas variables imprescindibles para su funcionamiento. Ejecutar al instalar.

import pathlib
import json
import sqlite3

Rutas = {}
Rutas["script"] = str(pathlib.Path(__file__).parent.resolve())
Rutas["config"] = Rutas["script"] + "/config.json"
Rutas["databaseSchema"] = Rutas["script"] + "/schema.sql"


print("We need to do some configuration. If you want to change the configuration you can find it at config.json")
Config = {}
Config["databasePath"] = input("Please introduce a path for the database. If no path is specified, the database will be created in the same directory as the rest of the files")
Config["APIkey"] = input("Please introduce your Scopus API key. If you skip this you will have to enter the key every time you want to download data.")

if Config["databasePath"] == "":
    Config["databasePath"] = Rutas["script"] + "/database.sqlite"

Config["databaseExists"] = "False"

#Comprobamos si la base de datos existía
BaseDatosExiste = pathlib.Path(Config["databasePath"]).exists()

#Creamos la base de datos
conn = sqlite3.connect(Config["databasePath"])
c = conn.cursor()

with open(Rutas["databaseSchema"], 'r') as sql_file:
    sql_script = sql_file.read()

c.executescript(sql_script)

#Si acabamos de crear la base de datos
Archivo = pathlib.Path(Config["databasePath"])
if BaseDatosExiste == False:
    c.executescript("""
              INSERT INTO "Variables" VALUES (NULL,'LimiteDescargas','20000','Muchos terminos de busqueda generan cientos de miles de resultados. Esta variable define el numero maximo de resultados que se descargaran.');
INSERT INTO "Variables" VALUES (NULL,'ResultadosPagina','25','Numero de resultados que se obtienen por cada solicitud a la API de busqueda.');
INSERT INTO "Variables" VALUES (NULL,'DescargaAutomatica','1','Especifica si el algoritmo debe descargar los datos automáticamente. Si vale 0 (cero) el algoritmo se detiene.');
              """)

conn.commit()
conn.close()

Config["databaseExists"] = "True"

#Actualizamos el archivo de configuracion
with open(Rutas["config"], 'w') as file:
    json.dump(Config, file)