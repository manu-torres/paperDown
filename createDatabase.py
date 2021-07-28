#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pathlib
import json
import sqlite3

Rutas = {}
Rutas["script"] = str(pathlib.Path(__file__).parent.resolve())
Rutas["config"] = Rutas["script"] + "/config.json"
Rutas["databaseSchema"] = Rutas["script"] + "/schema.sql"

with open(Rutas["config"], 'r') as file:
     Config = json.loads(file.read())

if Config["databasePath"] == "":
    Config["databasePath"] = Rutas["script"] + "/database.sqlite"

#Creamos la base de datos
conn = sqlite3.connect(Config["databasePath"])
c = conn.cursor()

with open(Rutas["databaseSchema"], 'r') as sql_file:
    sql_script = sql_file.read()

c.executescript(sql_script)

#Si es la primera vez que se ejecuta el script, añadimos algunas variables a la base de datos
if Config["databaseExists"] != "True":
    c.executescript("""
              INSERT INTO "Variables" VALUES (NULL,'LimiteDescargas','20000','Muchos terminos de busqueda generan cientos de miles de resultados. Esta variable define el numero maximo de resultados que se descargaran.');
INSERT INTO "Variables" VALUES (NULL,'ResultadosPagina','25','Numero de resultados que se obtienen por cada solicitud a la API de busqueda.');
INSERT INTO "Variables" VALUES (NULL,'DescargaAutomatica','1','Especifica si el algoritmo debe descargar los datos automáticamente. Si vale 0 (cero) el algoritmo se detiene.');
              """)

conn.commit()
conn.close()

#Especificamos que la base de datos existe en la ruta deseada
Config["databaseExists"] = "True"

#Actualizamos el archivo de configuracion
with open(Rutas["config"], 'w') as file:
    json.dump(Config, file)