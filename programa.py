import tkinter as tk
from tkinter import messagebox, ttk
import sqlite3
import socket
import hashlib
from datetime import datetime

DB_NAME = "escaneo_puertos.db"

# ==========================================
# 1. BASE DE DATOS (MODELO E-R DEL INFORME)
# ==========================================
def inicializar_bd():
    conexion = sqlite3.connect(DB_NAME)
    cursor = conexion.cursor()
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
    conexion.commit()
    conexion.close()

def encriptar_pass(password):
    return hashlib.sha256(password.encode()).hexdigest()

# ==========================================
# 2. INTERFAZ GRÁFICA DE ESCRITORIO (TKINTER)
# ==========================================
class AplicacionEscaneo:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Escaneo de Puertos - UNC Dr. Humberto Fernández Morán")
        self.root.geometry("780x600")
        self.root.configure(bg="#0f172a")
        self.id_usuario_actual = None
        self.nombre_usuario_actual = None

        self.mostrar_login()

    def limpiar_ventana(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    # --- PANTALLA DE LOGIN Y REGISTRO ---
    def mostrar_login(self):
        self.limpiar_ventana()

        frame_header = tk.Frame(self.root, bg="#1e293b", pady=15)
        frame_header.pack(fill="x")
        tk.Label(frame_header, text="UNIVERSIDAD NACIONAL DE LAS CIENCIAS DR. HUMBERTO FERNÁNDEZ MORÁN", 
                 fg="#38bdf8", bg="#1e293b", font=("Segoe UI", 11, "bold")).pack()
        tk.Label(frame_header, text="PROYECTO: ESCANEO DE PUERTOS (MODELO E-R Y BASE DE DATOS)", 
                 fg="#e2e8f0", bg="#1e293b", font=("Segoe UI", 10)).pack()

        frame_box = tk.Frame(self.root, bg="#1e293b", padx=30, pady=25)
        frame_box.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(frame_box, text="CONTROL DE ACCESO (TABLA USUARIOS)", fg="#38bdf8", bg="#1e293b", font=("Segoe UI", 12, "bold")).pack(pady=(0, 15))

        tk.Label(frame_box, text="Usuario:", fg="#cbd5e1", bg="#1e293b", font=("Segoe UI", 10)).pack(anchor="w")
        self.entry_user = tk.Entry(frame_box, width=32, font=("Segoe UI", 11))
        self.entry_user.pack(pady=(0, 12))

        tk.Label(frame_box, text="Contraseña:", fg="#cbd5e1", bg="#1e293b", font=("Segoe UI", 10)).pack(anchor="w")
        self.entry_pass = tk.Entry(frame_box, width=32, show="*", font=("Segoe UI", 11))
        self.entry_pass.pack(pady=(0, 20))

        tk.Button(frame_box, text="Iniciar Sesión", command=self.login, bg="#0284c7", fg="white", 
                  font=("Segoe UI", 10, "bold"), width=28, pady=5, bd=0).pack(pady=5)
        tk.Button(frame_box, text="Registrar Nuevo Operador", command=self.registrar, bg="#10b981", fg="white", 
                  font=("Segoe UI", 10, "bold"), width=28, pady=5, bd=0).pack(pady=5)

        frame_footer = tk.Frame(self.root, bg="#0f172a", pady=10)
        frame_footer.pack(side="bottom", fill="x")
        tk.Label(frame_footer, text="Integrantes: Mervin Urdaneta | Russmann Libre | Esteban Hinestroza | Victor Oropeza", 
                 fg="#64748b", bg="#0f172a", font=("Segoe UI", 9)).pack()

    def registrar(self):
        u = self.entry_user.get().strip()
        p = self.entry_pass.get().strip()
        if not u or not p:
            messagebox.showwarning("Campos vacíos", "Por favor ingresa un usuario y contraseña.")
            return

        conn = sqlite3.connect(DB_NAME)
        cur = conn.cursor()
        try:
            cur.execute("INSERT INTO USUARIOS (usuario, pass) VALUES (?, ?)", (u, encriptar_pass(p)))
            conn.commit()
            messagebox.showinfo("Éxito", f"Operador '{u}' registrado en la tabla USUARIOS.")
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Ese nombre de usuario ya existe.")
        finally:
            conn.close()

    def login(self):
        u = self.entry_user.get().strip()
        p = self.entry_pass.get().strip()
        conn = sqlite3.connect(DB_NAME)
        cur = conn.cursor()
        cur.execute("SELECT id, usuario FROM USUARIOS WHERE usuario = ? AND pass = ?", (u, encriptar_pass(p)))
        res = cur.fetchone()
        conn.close()

        if res:
            self.id_usuario_actual = res[0]
            self.nombre_usuario_actual = res[1]
            self.mostrar_panel()
        else:
            messagebox.showerror("Acceso Denegado", "Usuario o contraseña incorrectos.")

    # --- PANEL PRINCIPAL DE ESCANEO ---
    def mostrar_panel(self):
        self.limpiar_ventana()

        # Barra superior
        top = tk.Frame(self.root, bg="#1e293b", pady=10, padx=15)
        top.pack(fill="x")
        tk.Label(top, text=f"Operador Activo: {self.nombre_usuario_actual} (ID: #{self.id_usuario_actual})", 
                 fg="#38bdf8", bg="#1e293b", font=("Segoe UI", 11, "bold")).pack(side="left")
        tk.Button(top, text="Cerrar Sesión", command=self.mostrar_login, bg="#ef4444", fg="white", 
                  font=("Segoe UI", 9, "bold"), bd=0, padx=10, pady=3).pack(side="right")

        # Formulario de Escaneo
        form = tk.Frame(self.root, bg="#1e293b", pady=15, padx=15)
        form.pack(fill="x", padx=15, pady=15)

        tk.Label(form, text="IP o Dominio:", fg="white", bg="#1e293b", font=("Segoe UI", 10)).grid(row=0, column=0, padx=5, sticky="w")
        self.entry_ip = tk.Entry(form, width=22, font=("Segoe UI", 10))
        self.entry_ip.insert(0, "scanme.nmap.org")
        self.entry_ip.grid(row=0, column=1, padx=5)

        tk.Label(form, text="Puerto Inicial:", fg="white", bg="#1e293b", font=("Segoe UI", 10)).grid(row=0, column=2, padx=5)
        self.entry_p1 = tk.Entry(form, width=8, font=("Segoe UI", 10))
        self.entry_p1.insert(0, "20")
        self.entry_p1.grid(row=0, column=3, padx=5)

        tk.Label(form, text="Puerto Final:", fg="white", bg="#1e293b", font=("Segoe UI", 10)).grid(row=0, column=4, padx=5)
        self.entry_p2 = tk.Entry(form, width=8, font=("Segoe UI", 10))
        self.entry_p2.insert(0, "85")
        self.entry_p2.grid(row=0, column=5, padx=5)

        tk.Button(form, text="Ejecutar Escaneo", command=self.ejecutar_escaneo, bg="#0284c7", fg="white", 
                  font=("Segoe UI", 10, "bold"), bd=0, padx=15, pady=4).grid(row=0, column=6, padx=15)

        # Tablas de Resultados (RESUMEN_ESCANEO y PUERTOS_ABIERTOS)
        contenedor_tablas = tk.Frame(self.root, bg="#0f172a")
        contenedor_tablas.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        # Tabla Izquierda: RESUMEN_ESCANEO
        frame_izq = tk.Frame(contenedor_tablas, bg="#1e293b", padx=10, pady=10)
        frame_izq.pack(side="left", fill="both", expand=True, padx=(0, 7))
        tk.Label(frame_izq, text="Tabla: RESUMEN_ESCANEO (Selecciona uno)", fg="#38bdf8", bg="#1e293b", font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(0, 8))

        self.tree_resumen = ttk.Treeview(frame_izq, columns=("id", "fecha", "total"), show="headings", height=12)
        self.tree_resumen.heading("id", text="ID (PK)")
        self.tree_resumen.heading("fecha", text="Fecha y Hora")
        self.tree_resumen.heading("total", text="Puertos Analizados")
        self.tree_resumen.column("id", width=55, anchor="center")
        self.tree_resumen.column("fecha", width=140, anchor="center")
        self.tree_resumen.column("total", width=110, anchor="center")
        self.tree_resumen.pack(fill="both", expand=True)
        self.tree_resumen.bind("<<TreeviewSelect>>", self.cargar_puertos_detalle)

        # Tabla Derecha: PUERTOS_ABIERTOS
        frame_der = tk.Frame(contenedor_tablas, bg="#1e293b", padx=10, pady=10)
        frame_der.pack(side="right", fill="both", expand=True, padx=(7, 0))
        tk.Label(frame_der, text="Tabla: PUERTOS_ABIERTOS (Relación 1:N)", fg="#34d399", bg="#1e293b", font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(0, 8))

        self.tree_puertos = ttk.Treeview(frame_der, columns=("puerto", "proto", "estado", "fk"), show="headings", height=12)
        self.tree_puertos.heading("puerto", text="Puerto")
        self.tree_puertos.heading("proto", text="Protocolo")
        self.tree_puertos.heading("estado", text="Estado")
        self.tree_puertos.heading("fk", text="id_escaneo (FK)")
        self.tree_puertos.column("puerto", width=70, anchor="center")
        self.tree_puertos.column("proto", width=75, anchor="center")
        self.tree_puertos.column("estado", width=85, anchor="center")
        self.tree_puertos.column("fk", width=100, anchor="center")
        self.tree_puertos.pack(fill="both", expand=True)

        self.cargar_resumenes()

    def ejecutar_escaneo(self):
        objetivo = self.entry_ip.get().strip()
        try:
            ip = socket.gethostbyname(objetivo)
            p1 = int(self.entry_p1.get())
            p2 = int(self.entry_p2.get())
        except Exception:
            messagebox.showerror("Error", "Verifica que la IP/Dominio y el rango de puertos sean válidos.")
            return

        total = (p2 - p1) + 1
        fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        conn = sqlite3.connect(DB_NAME)
        cur = conn.cursor()
        cur.execute("INSERT INTO RESUMEN_ESCANEO (fecha, puertos_analizados, id_usuario) VALUES (?, ?, ?)",
                    (fecha, total, self.id_usuario_actual))
        id_escaneo = cur.lastrowid

        abiertos = 0
        self.root.config(cursor="watch")
        self.root.update()

        for puerto in range(p1, p2 + 1):
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(0.25)
            if sock.connect_ex((ip, puerto)) == 0:
                abiertos += 1
                cur.execute("INSERT INTO PUERTOS_ABIERTOS (puerto, protocolo, estado, id_escaneo) VALUES (?, ?, ?, ?)",
                            (puerto, "TCP", "Abierto", id_escaneo))
            sock.close()

        self.root.config(cursor="")
        conn.commit()
        conn.close()

        self.cargar_resumenes()
        messagebox.showinfo("Escaneo Completado", f"Objetivo: {ip}\nPuertos evaluados: {total}\nPuertos abiertos detectados: {abiertos}")

    def cargar_resumenes(self):
        for row in self.tree_resumen.get_children():
            self.tree_resumen.delete(row)

        conn = sqlite3.connect(DB_NAME)
        cur = conn.cursor()
        cur.execute("SELECT id, fecha, puertos_analizados FROM RESUMEN_ESCANEO WHERE id_usuario = ? ORDER BY id DESC", 
                    (self.id_usuario_actual,))
        for r in cur.fetchall():
            self.tree_resumen.insert("", "end", values=r)
        conn.close()

    def cargar_puertos_detalle(self, event):
        seleccion = self.tree_resumen.selection()
        if not seleccion:
            return
        id_escaneo = self.tree_resumen.item(seleccion[0])["values"][0]

        for row in self.tree_puertos.get_children():
            self.tree_puertos.delete(row)

        conn = sqlite3.connect(DB_NAME)
        cur = conn.cursor()
        cur.execute("SELECT puerto, protocolo, estado, id_escaneo FROM PUERTOS_ABIERTOS WHERE id_escaneo = ?", (id_escaneo,))
        for p in cur.fetchall():
            self.tree_puertos.insert("", "end", values=p)
        conn.close()

if __name__ == "__main__":
    inicializar_bd()
    root = tk.Tk()
    app = AplicacionEscaneo(root)
    root.mainloop()