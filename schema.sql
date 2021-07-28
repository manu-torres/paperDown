BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS "Variables" (
	"ID"	INTEGER,
	"Variable"	INTEGER,
	"Valor"	TEXT,
	"Descripcion"	TEXT,
	PRIMARY KEY("ID" AUTOINCREMENT)
);
CREATE TABLE IF NOT EXISTS "Log" (
	"ID"	INTEGER,
	"Mensaje"	TEXT,
	"Fecha"	TEXT DEFAULT (STRFTIME('%Y-%m-%d %H:%M:%S', 'NOW', 'localtime')),
	PRIMARY KEY("ID" AUTOINCREMENT)
);
CREATE TABLE IF NOT EXISTS "Datos" (
	"ID"	INTEGER,
	"Title"	TEXT,
	"Author"	TEXT,
	"Organization"	TEXT,
	"Country"	TEXT,
	"Date"	TEXT,
	"DOI"	TEXT,
	"PublicationName"	TEXT,
	"Abstract"	TEXT,
	"AuthorList"	TEXT,
	"Keywords"	TEXT,
	"Busqueda"	TEXT,
	PRIMARY KEY("ID" AUTOINCREMENT)
);

CREATE TABLE IF NOT EXISTS "Registro" (
	"ID"	INTEGER,
	"Busqueda"	TEXT,
	"ResultadosTotales"	INTEGER DEFAULT 0,
	"IteracionesTotales"	INTEGER DEFAULT 0,
	"UltimaIteracion"	INTEGER DEFAULT 0,
	"Terminado"	TEXT DEFAULT 'FALSE',
	PRIMARY KEY("ID" AUTOINCREMENT)
);
CREATE INDEX IF NOT EXISTS "Registro_ID" ON "Registro" (
	"ID"
);
CREATE VIEW IF NOT EXISTS "ResumenAutores" AS 
SELECT Author, count() AS Frecuencia 
FROM
	(SELECT DISTINCT(Title), Author FROM Datos)
GROUP BY
	Author
ORDER BY 
	Frecuencia DESC;
CREATE VIEW IF NOT EXISTS "ResumenCentros" AS SELECT Organization, count() AS Frecuencia 
FROM 
	(SELECT DISTINCT(Title), Organization FROM Datos)
GROUP BY
	Organization
ORDER BY
	Frecuencia DESC;
CREATE VIEW IF NOT EXISTS "ResumenRevistas" AS SELECT PublicationName, count() AS Frecuencia 
FROM 
	(SELECT DISTINCT(Title), PublicationName FROM Datos)
GROUP BY
	PublicationName
ORDER BY
	Frecuencia DESC;
CREATE VIEW IF NOT EXISTS "ResumenPais" AS SELECT Country, count() AS Frecuencia 
FROM 
	(SELECT DISTINCT(Title), Country FROM Datos)
GROUP BY
	Country
UNION
SELECT "Total", count() FROM 
	(SELECT DISTINCT(Title), Country FROM Datos)
ORDER BY 
	Frecuencia DESC;
CREATE VIEW IF NOT EXISTS "ResumenBusquedas" AS SELECT Busqueda, count() AS Frecuencia 
FROM Datos
GROUP BY
	Busqueda
UNION
SELECT "Total", count() FROM 
	(SELECT DISTINCT(Title) FROM Datos)
ORDER BY 
	Frecuencia DESC;
CREATE VIEW IF NOT EXISTS SinDuplicados AS
SELECT Title, ID, Author, Organization,
	Country, Date, DOI, PublicationName,
	Abstract, AuthorList, Keywords, Busqueda
FROM Datos
GROUP BY
	Title
ORDER BY
	Date DESC;
COMMIT;
