#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#Este script descarga los datos de scopus. Esta pensado para ejecutarse periodicamente a traves de cron. Consulta una lista de terminos de busqueda e itera sobre ellos descargando todos los articulos que los contienen (hasta un limite) y anexandolos a la base de datos
#Cada vez que se ejecuta hace una sola solicitud a la API.

import time

start_time = time.time()

import pathlib
import urllib.request
from urllib.error import HTTPError
import traceback
import json
import math
import numpy as np
import pandas as pd
from elsapy.elsclient import ElsClient
from elsapy.elsdoc import FullDoc
import re
import sqlite3
import os #Notificaciones ante errores
from datetime import datetime #para conseguir la fecha

print(datetime.now().strftime("%d/%m/%Y %H:%M:%S") + "   --------------------------")

Rutas = {}
Rutas["script"] = str(pathlib.Path(__file__).parent.resolve())
Rutas["config"] = Rutas["script"] + "/config.json"

with open(Rutas["config"], 'r') as file:
     Config = json.loads(file.read())

APIkey = Config["APIkey"] #Clave de la API

if APIkey == "":
    APIkey = input("No API key in config.json, please enter your SCOPUS API key: ")

def RegistraMensaje(Mensaje, Alerta = False):
    global BaseDatos
    #Esta funcion permite registrar mensajes, errores, etc...    
    conn = sqlite3.connect(BaseDatos)

    c = conn.cursor()
       
    c.execute("INSERT INTO Log (Mensaje) VALUES ('" + Mensaje + "')")

    conn.commit()
    conn.close()
    
    if Alerta:
        try:
            os.system("notify-send " + Mensaje.strip("<").strip(">"))
        except:
            pass

def LimpiaDatos(Datos):
    #Esta funcion limpia los datos
    #Eliminamos duplicados
    Datos = Datos.loc[Datos.duplicated() == False]
    
    #Eliminamos los que no tienen abstract
    Datos = Datos.loc[Datos["Abstract"].isna() == False]
    
    #Eliminamos los abstracts excesivamente cortos
    Datos = Datos.loc[Datos["Abstract"].str.len() > 200]
    
    #Limpiamos el texto
    Patron = re.compile(" {2,}") #Quitamos espacios iniciales
    Datos["Abstract"] = Datos["Abstract"].str.replace(Patron, "")
    
    #Quitamos los saltos de linea iniciales
    Datos["Abstract"].loc[Datos["Abstract"].str.startswith("\n") == True] = Datos["Abstract"].loc[Datos["Abstract"].str.startswith("\n") == True].str[1:]
    
    #Convertimos los campos con unos valores determinados en perdidos
    Datos = Datos.fillna(value = np.nan) #Para eliminar los valores de tipo Nonetype
    Datos = Datos.replace("", np.nan)
    
    return Datos

def DescargaDatos(Busqueda):
    global APIkey, ResultadosPagina, LimiteDescargas, BaseDatos, RegistraMensaje
    #Esta funcion se ocupa de descargar los datos. Primero debemos ver si ya se han descargado datos para la busqueda
    conn = sqlite3.connect(BaseDatos)
    c = conn.cursor()
    
    c.execute("SELECT UltimaIteracion FROM Registro WHERE Busqueda == '" + Busqueda + "'")
    
    IteracionActual = int(c.fetchone()[0]) + 1
    
    c.execute("SELECT IteracionesTotales FROM Registro WHERE Busqueda == '" + Busqueda + "'")
    
    IteracionesTotales = int(c.fetchone()[0]) #Maximo numero de iteraciones para descargar todos los resultados de la busqueda
    
    conn.close()
    
    #Convertimos el termino de busqueda en una query apta para la URL
    if Busqueda.endswith("PRE-MADE-QUERY"):
        #Si la busqueda termina con un patron especial, se asume que es una query hecha de antemano
        Query = Busqueda.replace("PRE-MADE-QUERY", "")
        Query = urllib.parse.quote_plus(Query)
    elif Busqueda.isdigit() and len(Busqueda) == 4:
        #Si la busqueda es un entero de 4 cifras, se asume que es un año
        Query = urllib.parse.quote_plus("PUBYEAR = " + Busqueda)
    else:
        #Si no contiene dicho patron, el termino se encapsula en una query
        Query = urllib.parse.quote_plus("KEY(" + Busqueda + ")")
    
    urlAPI = "https://api.elsevier.com/content/search/scopus?query=" + Query + "+AND+SUBJAREA%28PSYC%29+AND+LANGUAGE%28english%29+AND+DOI%2810.1016%2F%2A%29"
    
    if IteracionActual > 1 and IteracionActual < 200:
        urlAPI = urlAPI + "&start=" + str(ResultadosPagina * IteracionActual)
    
    elif IteracionActual == int(5000 / ResultadosPagina):
        #La API solo permite descargar los primeros 5000 elementos de una busqueda (por defecto los mas recientes), cuando llegamos al tope, empezamos a descargar los mas antiguos.
        urlAPI = urlAPI + "&sort=+coverDate"
    elif IteracionActual > int(5000 / ResultadosPagina):
        urlAPI = urlAPI + "&start=" + str(ResultadosPagina * (IteracionActual - int(5000 / ResultadosPagina)))
        urlAPI = urlAPI + "&sort=+coverDate"
    
    hdr = {"X-ELS-APIKey" : APIkey}
    req = urllib.request.Request(url = urlAPI,
                                 headers = hdr)
    
    try:
        with urllib.request.urlopen(req) as Solicitud:
           DatosTexto = Solicitud.read().decode('utf-8')
           DatosTexto = json.loads(DatosTexto)
    except HTTPError as err:
        if err.code == 401:
            RegistraMensaje("AUTHENTICATON ERROR, BAD API KEY?")
        elif err.code == 429:
            RegistraMensaje("API LIMIT REACHED")
            
        quit()
        
    
    Resultados = pd.DataFrame({
                "Title" : [""],
                "Author" : [""],
                "Organization" : [""],
                "Country" : [""],
                "Date" : [""],
                "DOI" : [""],
                "PublicationName" : [""]
                })
    
    ListaResultados = DatosTexto["search-results"]["entry"]
    for i in range(len(ListaResultados)):
        VarDisponibles = list(ListaResultados[i].keys())
        Dict = {
        "Title" : [""],
        "Author" : [""],
        "Organization" : [""],
        "Country" : [""],
        "Date" : [""],
        "DOI" : [""],
        "PublicationName" : [""]
        }
        
        if "dc:title" in VarDisponibles:
            Dict["Title"] = [ListaResultados[i]["dc:title"]]
        if "dc:creator" in VarDisponibles:
            Dict["Author"] = [ListaResultados[i]["dc:creator"]]
        if "affiliation" in VarDisponibles:
            Dict["Organization"] = [ListaResultados[i]["affiliation"][0]["affilname"]]
            try:
                Dict["Country"] = [ListaResultados[i]["affiliation"][0]["affiliation-country"]]
            except:
                pass
        if "prism:coverDate" in VarDisponibles:
            Dict["Date"] = [ListaResultados[i]["prism:coverDate"]]
        if "prism:doi" in VarDisponibles:
            Dict["DOI"] = [ListaResultados[i]["prism:doi"]]
        if "prism:publicationName" in VarDisponibles:
            Dict["PublicationName"] = [ListaResultados[i]["prism:publicationName"]]
            
        Resultados = Resultados.append(pd.DataFrame(Dict))
    
    nResultados = int(DatosTexto["search-results"]["opensearch:totalResults"])
    Iteraciones = math.ceil(nResultados / ResultadosPagina)
    #Limitamos el numero de articulos descargados por tag
    if (Iteraciones * ResultadosPagina) > LimiteDescargas:
        Iteraciones = math.ceil(LimiteDescargas / ResultadosPagina)
        
    #Filtramos los que no tienen DOI
    Resultados = Resultados.loc[Resultados["DOI"].str.len() > 5]
    
    #Para obtener el abstract usamos elsapy
    myCl = ElsClient(APIkey)
    
    Resultados["Abstract"] = ""
    Resultados["AuthorList"] = ""
    Resultados["Keywords"] = ""
    
    for i in range(Resultados.shape[0]):
        try:        
            Doc = FullDoc(doi = Resultados["DOI"].iloc[i]) #Documento por DOI a traves de science direct
            
            if Doc.read(myCl):
                #Si conseguimos obtener el documento, descargamos los datos
                Resultados["Abstract"].iloc[i] = Doc.data["coredata"]["dc:description"]
                
                try:
                    KeyWords = ""
                    for j in range(len(Doc.data["coredata"]["dcterms:subject"])):
                        KeyWords = KeyWords + "<" + Doc.data["coredata"]["dcterms:subject"][j]["$"] + ">"
                    Resultados["Keywords"].iloc[i] = KeyWords
                except:
                    pass
                
                try:
                    Autores = ""
                    for j in range(len(Doc.data["coredata"]["dc:creator"])):
                        Autores = Autores + "<" + Doc.data["coredata"]["dc:creator"][j]["$"] + ">"
                            
                    Resultados["AuthorList"].iloc[i] = Autores 
                    #Sobreescribimos el autor principal
                    Resultados["Author"].iloc[i] = Doc.data["coredata"]["dc:creator"][0]["$"]
                except:
                    pass
                
        except:
            Mensaje = "ERROR:UNABLE TO DOWNLOAD " + Resultados["DOI"].iloc[i]
            RegistraMensaje(Mensaje)

    Resultados["Busqueda"] = Busqueda
    
    #Limpiamos los datos
    Resultados = LimpiaDatos(Resultados)
    
    #Creamos la variable id como una columna vacia (la rellena la base de datos)
    Resultados["ID"] = np.nan
    
    #Guardamos los datos en la base de datos
    conn = sqlite3.connect(BaseDatos)
    
    #Consultamos los articulos existentes para no meter duplicados
    try:
        #Esta comprobacion puede fallar si se ha borrado la tabla
        Query = "SELECT Title FROM Datos WHERE Busqueda == '" + Busqueda + "'"
        Existentes = pd.read_sql_query(Query, conn)
        
        Resultados = Resultados.loc[Resultados["Title"].isin(Existentes["Title"]) == False]
    except:
        pass
    
    if Resultados.shape[0] > 0:
        Resultados.to_sql(con = conn,
                          name = "Datos",
                          if_exists = "append",
                          index = False)
        Mensaje = str(Resultados.shape[0]) + " ARTICLES ADDED FOR " + Busqueda
        RegistraMensaje(Mensaje)
        
    else:
        Mensaje = "NO ARTICLES ON CURRENT ITERATION FOR " + Busqueda
        RegistraMensaje(Mensaje)
    
    if IteracionesTotales == 0:
        IteracionesTotales = Iteraciones
    
    if IteracionActual >= IteracionesTotales:
        Terminado = "True"
        Mensaje = "DONE WITH " + Busqueda
        RegistraMensaje(Mensaje)
    else:
        Terminado = "False"
    
    #Registramos la descarga de los datos en la base de datos
    c = conn.cursor()
    
    if IteracionActual == 1:
        c.execute("UPDATE Registro SET ResultadosTotales = " + str(nResultados) + ", IteracionesTotales = " + str(Iteraciones) + ", UltimaIteracion = 1, Terminado = '" + Terminado + "' WHERE Busqueda == '" + Busqueda + "'")
    else:
        c.execute("UPDATE Registro SET UltimaIteracion = " + str(IteracionActual) + ", Terminado = '" + Terminado + "' WHERE Busqueda == '" + Busqueda + "'")
        
    conn.commit()
        
    conn.close()

#Inicio del script
    
#Comprobamos que la base de datos esta creada
if Config["databaseExists"] != "True":
    print("Database has not been created. Run createDatabase.py first.")
    quit()
#Recuperamos algunas variables de la base de datos
BaseDatos = Config["databasePath"]

conn = sqlite3.connect(BaseDatos)
    
c = conn.cursor()

c.execute("SELECT Valor FROM Variables WHERE Variable == 'LimiteDescargas'")
LimiteDescargas = int(c.fetchone()[0])

c.execute("SELECT Valor FROM Variables WHERE Variable == 'ResultadosPagina'")
ResultadosPagina = int(c.fetchone()[0])

c.execute("SELECT Valor FROM Variables WHERE Variable == 'DescargaAutomatica'")
DescargaAutomatica = int(c.fetchone()[0])

conn.close()

#Seleccionamos la query para descargar los datos
conn = sqlite3.connect(BaseDatos)
    
c = conn.cursor()

c.execute("SELECT Busqueda FROM Registro WHERE UltimaIteracion <= 400 AND (IteracionesTotales > UltimaIteracion OR IteracionesTotales == 0) ORDER BY UltimaIteracion ASC, ID ASC")

try:
    Busqueda = c.fetchone()[0]
except:
    #Si no encontramos terminos que cumplan la condicion anterior, buscamos otros nuevos (el campo iteraciones totales vale cero)
    try:
        c.execute("SELECT Busqueda FROM Registro WHERE IteracionesTotales == 0 ORDER BY ID")
        Busqueda = c.fetchone()[0]
    except:
        conn.close()
        print("There are no search terms on the database. Add one with manageDatabase.py")
        quit()

conn.close()

#Descargamos los datos
try:
    if DescargaAutomatica != 0:
        DescargaDatos(Busqueda)
except Exception as OutputError:
    print("ERROR:")
    print(OutputError)
    print("TRACEBACK:")
    traceback.print_exc()
    RegistraMensaje("UNABLE TO DOWNLOAD ARTICLES FOR " + Busqueda)
    #Si no se pueden descargar los datos, hacemos que salte a la siguiente iteracion
    conn = sqlite3.connect(BaseDatos)
    
    c = conn.cursor()
    
    c.execute("SELECT UltimaIteracion FROM Registro WHERE Busqueda == '" + Busqueda + "'")
    Iteracion = int(c.fetchone()[0]) + 1 #Saltamos la iteracion que da problemas
    
    c.execute("UPDATE Registro SET UltimaIteracion = '" + str(Iteracion) +"' WHERE Busqueda == '" + Busqueda + "'")
    
    conn.commit()
    
    conn.close()
