import tkinter as tk
from tkinter import ttk, messagebox
from sympy import symbols, simplify_logic
from sympy.logic.boolalg import And, Or, Not
from graphviz import Digraph


class AplicacionLogica:
    def __init__(self, raiz):
        self.raiz = raiz
        self.raiz.title("Generador de Circuitos Lógicos")
        self.raiz.geometry("500x500")
        self.raiz.configure(bg="#f0f0f0")

        self.entradas = []
        self.salidas = []
        self.tabla = []
        self.expresiones = []

        self.configurar_interfaz()

    def configurar_interfaz(self):
        # Frame principal para organización
        frame_principal = ttk.Frame(self.raiz, padding="10")
        frame_principal.grid(row=0, column=0, sticky="nsew")

        # Entradas
        frame_entradas = ttk.LabelFrame(frame_principal, text="Entradas", padding="10")
        frame_entradas.grid(row=0, column=0, pady=10, sticky="ew")
        self.var_entrada = tk.StringVar()
        ttk.Entry(frame_entradas, textvariable=self.var_entrada, width=30).grid(row=0, column=0, padx=5, pady=5)
        ttk.Button(frame_entradas, text="Añadir Entrada", command=self.agregar_entrada).grid(row=0, column=1, padx=5, pady=5)

        # Salidas
        frame_salidas = ttk.LabelFrame(frame_principal, text="Salidas", padding="10")
        frame_salidas.grid(row=1, column=0, pady=10, sticky="ew")
        self.var_salida = tk.StringVar()
        ttk.Entry(frame_salidas, textvariable=self.var_salida, width=30).grid(row=0, column=0, padx=5, pady=5)
        ttk.Button(frame_salidas, text="Añadir Salida", command=self.agregar_salida).grid(row=0, column=1, padx=5, pady=5)

        # Tabla de verdad
        self.marco_tabla = ttk.Frame(frame_principal)
        self.marco_tabla.grid(row=2, column=0, pady=10, sticky="ew")

        # Botones para generar y resetear
        frame_botones = ttk.Frame(frame_principal, padding="10")
        frame_botones.grid(row=3, column=0, pady=10, sticky="ew")
        ttk.Button(frame_botones, text="Generar Expresión Booleana", command=self.generar_exp_booleana).grid(row=0, column=0, padx=5, pady=5)
        ttk.Button(frame_botones, text="Generar Diagrama", command=self.generar_diagrama).grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(frame_botones, text="Resetear", command=self.resetear).grid(row=0, column=2, padx=5, pady=5)

        # Etiqueta para mostrar la expresión simplificada
        self.etiqueta_expr = ttk.Label(frame_principal, text="Expresión simplificada:")
        self.etiqueta_expr.grid(row=4, column=0, pady=10, sticky="w")

    def agregar_entrada(self):
        nombre_entrada = self.var_entrada.get()
        if nombre_entrada and nombre_entrada not in self.entradas:
            self.entradas.append(nombre_entrada)
            self.var_entrada.set("")
            self.actualizar_marco_tabla()
        else:
            messagebox.showerror("Error", "Entrada inválida o duplicada.")

    def agregar_salida(self):
        nombre_salida = self.var_salida.get()
        if nombre_salida and nombre_salida not in self.salidas:
            self.salidas.append(nombre_salida)
            self.var_salida.set("")
            self.actualizar_marco_tabla()
        else:
            messagebox.showerror("Error", "Salida inválida o duplicada.")

    def actualizar_marco_tabla(self):
        for widget in self.marco_tabla.winfo_children():
            widget.destroy()

        columnas = self.entradas + self.salidas
        for col, nombre in enumerate(columnas):
            ttk.Label(self.marco_tabla, text=nombre).grid(row=0, column=col, padx=5)

        self.tabla = [[tk.StringVar() for _ in columnas] for _ in range(2 ** len(self.entradas))]
        for idx_fila, fila_vars in enumerate(self.tabla):
            valores_binarios = format(idx_fila, f"0{len(self.entradas)}b")
            for idx_col, var in enumerate(fila_vars):
                if idx_col < len(self.entradas):
                    var.set(valores_binarios[idx_col])
                ttk.Entry(self.marco_tabla, textvariable=var, width=5).grid(row=idx_fila + 1, column=idx_col, padx=2)

    def generar_exp_booleana(self):
        if not self.entradas or not self.salidas:
            messagebox.showerror("Error", "Debe agregar al menos una entrada y una salida.")
            return

        try:
            datos = []
            for fila_vars in self.tabla:
                datos.append([var.get() for var in fila_vars])

            diccionario_simbolos = {nombre: symbols(nombre) for nombre in self.entradas}
            self.expresiones = []
            for idx, nombre_salida in enumerate(self.salidas):
                mintermios = []
                for fila in datos:
                    if fila[len(self.entradas) + idx] == "1":
                        termino = And(*[diccionario_simbolos[col] if bit == "1" else Not(diccionario_simbolos[col])
                                        for col, bit in zip(self.entradas, fila[:len(self.entradas)])])
                        mintermios.append(termino)
                expresion = Or(*mintermios)
                expresion_simplificada = simplify_logic(expresion)
                self.expresiones.append(expresion_simplificada)

            self.etiqueta_expr.config(text=f"Expresión simplificada: {', '.join(map(str, self.expresiones))}")
        except Exception as e:
            messagebox.showerror("Error", f"Error al generar la tabla: {e}")

    def generar_diagrama(self):
        if not self.expresiones:
            messagebox.showerror("Error", "Primero genere la expresión simplificada.")
            return

        try:
            generador_diagrama = GeneradorDiagramaLogico()
            generador_diagrama.generar_diagrama_completo(self.entradas, self.salidas, self.expresiones)
        except Exception as e:
            messagebox.showerror("Error", f"Error al generar el diagrama: {e}")

    def resetear(self):
        self.entradas.clear()
        self.salidas.clear()
        self.tabla = []
        self.expresiones.clear()
        self.var_entrada.set("")
        self.var_salida.set("")
        self.etiqueta_expr.config(text="Expresión simplificada:")
        for widget in self.marco_tabla.winfo_children():
            widget.destroy()


class GeneradorDiagramaLogico:
    def __init__(self):
        self.dot = Digraph(format="png")
        self.dot.attr(rankdir="LR", splines="line", ranksep="1.0", nodesep="0.7")
        self.contador = 0
        self.conexiones = set()
        self.ids_entradas = {}

    def _generar_id_unico(self):
        self.contador += 1
        return f"node{self.contador}"

    def _procesar_expresion(self, expr, nodo_padre=None):
        if isinstance(expr, And):
            id_nodo = self._generar_id_unico()
            self.dot.node(id_nodo, label="AND", shape="box")
            for arg in expr.args:
                id_hijo = self._procesar_expresion(arg, id_nodo)
                self._agregar_arista(id_hijo, id_nodo)
            if nodo_padre:
                self._agregar_arista(id_nodo, nodo_padre)
            return id_nodo

        elif isinstance(expr, Or):
            id_nodo = self._generar_id_unico()
            self.dot.node(id_nodo, label="OR", shape="box")
            for arg in expr.args:
                id_hijo = self._procesar_expresion(arg, id_nodo)
                self._agregar_arista(id_hijo, id_nodo)
            if nodo_padre:
                self._agregar_arista(id_nodo, nodo_padre)
            return id_nodo

        elif isinstance(expr, Not):
            id_nodo = self._generar_id_unico()
            self.dot.node(id_nodo, label="NOT", shape="box")
            id_hijo = self._procesar_expresion(expr.args[0], id_nodo)
            self._agregar_arista(id_hijo, id_nodo)
            if nodo_padre:
                self._agregar_arista(id_nodo, nodo_padre)
            return id_nodo

        else:
            if expr not in self.ids_entradas:
                id_nodo = self._generar_id_unico()
                self.dot.node(id_nodo, label=str(expr), shape="ellipse")
                self.ids_entradas[expr] = id_nodo
            if nodo_padre:
                self._agregar
