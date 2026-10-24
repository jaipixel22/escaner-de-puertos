import tkinter as tk
from tkinter import messagebox, ttk
import socket
from datetime import datetime
import bd

class VentanaPrincipal:
    def __init__(self, root):
        self.root = root
        self.root.title("Escaneo de Puertos - UNC")
        self.root.geometry("750x550")
        self.root.configure(bg="#eaecee")

        self.id_usuario = None
        self.usuario_actual = None

        self.pantalla_login()

    def limpiar(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def pantalla_login(self):
        self.limpiar()

        encabezado = tk.Frame(self.root, bg="#2c3e50", pady=12)
        encabezado.pack(fill="x")
        tk.Label(encabezado, text="UNIVERSIDAD NACIONAL DE LAS CIENCIAS DR. HUMBERTO FERNÁNDEZ MORÁN",
                 fg="white", bg="#2c3e50", font=("Arial", 10, "bold")).pack()
        tk.Label(encabezado, text="Sistema de Escaneo de Puertos",
                 fg="#bdc3c7", bg="#2c3e50", font=("Arial", 9)).pack()

        caja = tk.Frame(self.root, bg="white", padx=25, pady=20, relief="groove", bd=1)
        caja.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(caja, text="Control de Acceso", bg="white", font=("Arial", 12, "bold")).pack(pady=(0, 15))

        tk.Label(caja, text="Usuario:", bg="white", font=("Arial", 10)).pack(anchor="w")
        self.txt_user = tk.Entry(caja, width=30, font=("Arial", 10))
        self.txt_user.pack(pady=(0, 10))

        tk.Label(caja, text="Contraseña:", bg="white", font=("Arial", 10)).pack(anchor="w")
        self.txt_pass = tk.Entry(caja, width=30, show="*", font=("Arial", 10))
        self.txt_pass.pack(pady=(0, 15))

        tk.Button(caja, text="Ingresar", command=self.iniciar_sesion, bg="#2980b9", fg="white",
                  width=25, font=("Arial", 10, "bold")).pack(pady=4)
        tk.Button(caja, text="Registrar Usuario", command=self.registrar_usuario, bg="#27ae60", fg="white",
                  width=25, font=("Arial", 10)).pack(pady=4)

        pie = tk.Label(self.root, text="Integrantes: Mervin Urdaneta, Russmann Libre, Esteban Hinestroza, Victor Oropeza",
                       bg="#eaecee", fg="#555555", font=("Arial", 8))
        pie.pack(side="bottom", pady=8)

    def registrar_usuario(self):
        user = self.txt_user.get().strip()
        clave = self.txt_pass.get().strip()

        if user == "" or clave == "":
            messagebox.showwarning("Aviso", "Debe completar todos los campos.")
            return

        conn = bd.conectar()
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO USUARIOS (usuario, pass) VALUES (?, ?)",
                           (user, bd.encriptar_clave(clave)))
            conn.commit()
            messagebox.showinfo("Registro", f"Usuario {user} guardado correctamente.")
        except Exception:
            messagebox.showerror("Error", "El nombre de usuario ya está registrado.")
        finally:
            conn.close()

    def iniciar_sesion(self):
        user = self.txt_user.get().strip()
        clave = self.txt_pass.get().strip()

        conn = bd.conectar()
        cursor = conn.cursor()
        cursor.execute("SELECT id, usuario FROM USUARIOS WHERE usuario = ? AND pass = ?",
                       (user, bd.encriptar_clave(clave)))
        fila = cursor.fetchone()
        conn.close()

        if fila:
            self.id_usuario = fila[0]
            self.usuario_actual = fila[1]
            self.pantalla_escaner()
        else:
            messagebox.showerror("Error", "Datos de acceso incorrectos.")

    def pantalla_escaner(self):
        self.limpiar()

        barra = tk.Frame(self.root, bg="#2c3e50", pady=8, padx=10)
        barra.pack(fill="x")
        tk.Label(barra, text=f"Operador: {self.usuario_actual} (ID: {self.id_usuario})",
                 fg="white", bg="#2c3e50", font=("Arial", 10, "bold")).pack(side="left")
        tk.Button(barra, text="Salir", command=self.pantalla_login, bg="#c0392b", fg="white",
                  font=("Arial", 9)).pack(side="right")

        panel_datos = tk.LabelFrame(self.root, text=" Datos del Escaneo ", bg="#eaecee", font=("Arial", 10, "bold"), padx=10, pady=10)
        panel_datos.pack(fill="x", padx=12, pady=10)

        tk.Label(panel_datos, text="Host / IP:", bg="#eaecee").grid(row=0, column=0, padx=5)
        self.txt_ip = tk.Entry(panel_datos, width=20)
        self.txt_ip.insert(0, "127.0.0.1")
        self.txt_ip.grid(row=0, column=1, padx=5)

        tk.Label(panel_datos, text="Desde puerto:", bg="#eaecee").grid(row=0, column=2, padx=5)
        self.txt_p1 = tk.Entry(panel_datos, width=8)
        self.txt_p1.insert(0, "20")
        self.txt_p1.grid(row=0, column=3, padx=5)

        tk.Label(panel_datos, text="Hasta puerto:", bg="#eaecee").grid(row=0, column=4, padx=5)
        self.txt_p2 = tk.Entry(panel_datos, width=8)
        self.txt_p2.insert(0, "100")
        self.txt_p2.grid(row=0, column=5, padx=5)

        tk.Button(panel_datos, text="Analizar Puertos", command=self.escanear, bg="#2980b9", fg="white",
                  font=("Arial", 9, "bold"), padx=10).grid(row=0, column=6, padx=15)

        panel_tablas = tk.Frame(self.root, bg="#eaecee")
        panel_tablas.pack(fill="both", expand=True, padx=12, pady=(0, 12))

        # Tabla Resumen Escaneo
        f_izq = tk.LabelFrame(panel_tablas, text=" Historial (RESUMEN_ESCANEO) ", bg="#eaecee", font=("Arial", 9, "bold"))
        f_izq.pack(side="left", fill="both", expand=True, padx=(0, 5))

        self.tabla_resumen = ttk.Treeview(f_izq, columns=("id", "fecha", "cant"), show="headings")
        self.tabla_resumen.heading("id", text="ID")
        self.tabla_resumen.heading("fecha", text="Fecha")
        self.tabla_resumen.heading("cant", text="Analizados")
        self.tabla_resumen.column("id", width=45, anchor="center")
        self.tabla_resumen.column("fecha", width=130, anchor="center")
        self.tabla_resumen.column("cant", width=80, anchor="center")
        self.tabla_resumen.pack(fill="both", expand=True, padx=5, pady=5)
        self.tabla_resumen.bind("<<TreeviewSelect>>", self.mostrar_detalle)

        # Tabla Puertos Abiertos
        f_der = tk.LabelFrame(panel_tablas, text=" Detalle (PUERTOS_ABIERTOS) ", bg="#eaecee", font=("Arial", 9, "bold"))
        f_der.pack(side="right", fill="both", expand=True, padx=(5, 0))

        self.tabla_puertos = ttk.Treeview(f_der, columns=("puerto", "proto", "estado", "id_esc"), show="headings")
        self.tabla_puertos.heading("puerto", text="Puerto")
        self.tabla_puertos.heading("proto", text="Protocolo")
        self.tabla_puertos.heading("estado", text="Estado")
        self.tabla_puertos.heading("id_esc", text="ID Escaneo")
        self.tabla_puertos.column("puerto", width=65, anchor="center")
        self.tabla_puertos.column("proto", width=75, anchor="center")
        self.tabla_puertos.column("estado", width=75, anchor="center")
        self.tabla_puertos.column("id_esc", width=80, anchor="center")
        self.tabla_puertos.pack(fill="both", expand=True, padx=5, pady=5)

        self.actualizar_historial()

    def escanear(self):
        host = self.txt_ip.get().strip()
        try:
            ip = socket.gethostbyname(host)
            p_ini = int(self.txt_p1.get())
            p_fin = int(self.txt_p2.get())
        except Exception:
            messagebox.showerror("Error", "Verifique la dirección IP y los puertos ingresados.")
            return

        total = (p_fin - p_ini) + 1
        fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        conn = bd.conectar()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO RESUMEN_ESCANEO (fecha, puertos_analizados, id_usuario) VALUES (?, ?, ?)",
                       (fecha_actual, total, self.id_usuario))
        id_escaneo = cursor.lastrowid

        abiertos = 0
        self.root.config(cursor="watch")
        self.root.update()

        for p in range(p_ini, p_fin + 1):
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(0.2)
            if s.connect_ex((ip, p)) == 0:
                abiertos += 1
                cursor.execute("INSERT INTO PUERTOS_ABIERTOS (puerto, protocolo, estado, id_escaneo) VALUES (?, ?, ?, ?)",
                               (p, "TCP", "Abierto", id_escaneo))
            s.close()

        self.root.config(cursor="")
        conn.commit()
        conn.close()

        self.actualizar_historial()
        messagebox.showinfo("Resultado", f"Análisis finalizado.\nPuertos analizados: {total}\nAbiertos encontrados: {abiertos}")

    def actualizar_historial(self):
        for item in self.tabla_resumen.get_children():
            self.tabla_resumen.delete(item)

        conn = bd.conectar()
        cursor = conn.cursor()
        cursor.execute("SELECT id, fecha, puertos_analizados FROM RESUMEN_ESCANEO WHERE id_usuario = ? ORDER BY id DESC",
                       (self.id_usuario,))
        for fila in cursor.fetchall():
            self.tabla_resumen.insert("", "end", values=fila)
        conn.close()

    def mostrar_detalle(self, event):
        sel = self.tabla_resumen.selection()
        if not sel:
            return
        id_escaneo = self.tabla_resumen.item(sel[0])["values"][0]

        for item in self.tabla_puertos.get_children():
            self.tabla_puertos.delete(item)

        conn = bd.conectar()
        cursor = conn.cursor()
        cursor.execute("SELECT puerto, protocolo, estado, id_escaneo FROM PUERTOS_ABIERTOS WHERE id_escaneo = ?",
                       (id_escaneo,))
        for fila in cursor.fetchall():
            self.tabla_puertos.insert("", "end", values=fila)
        conn.close()

if __name__ == "__main__":
    bd.crear_tablas()
    ventana = tk.Tk()
    app = VentanaPrincipal(ventana)
    ventana.mainloop()