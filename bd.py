import sqlite3
import hashlib

NOMBRE_BD = "escaneo_puertos.db"

def conectar():
    return sqlite3.connect(NOMBRE_BD)

def crear_tablas():
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS USUARIOS (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario VARCHAR(50) NOT NULL UNIQUE,
        pass VARCHAR(255) NOT NULL
    )""")

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS RESUMEN_ESCANEO (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        fecha DATETIME NOT NULL,
        puertos_analizados INT NOT NULL,
        id_usuario INT NOT NULL,
        FOREIGN KEY (id_usuario) REFERENCES USUARIOS(id)
    )""")

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS PUERTOS_ABIERTOS (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        puerto INT NOT NULL,
        protocolo VARCHAR(10) NOT NULL,
        estado VARCHAR(20) NOT NULL,
        id_escaneo INT NOT NULL,
        FOREIGN KEY (id_escaneo) REFERENCES RESUMEN_ESCANEO(id)
    )""")

    conn.commit()
    conn.close()

def encriptar_clave(clave):
    return hashlib.sha256(clave.encode()).hexdigest()