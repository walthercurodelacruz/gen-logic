import tkinter as tk
from tkinter import ttk
from sympy.logic.boolalg import And, Or, Not
from sympy import symbols
from graphviz import Digraph
import os


class AplicacionLogica:
    def __init__(self, raiz):
        self.raiz = raiz
        self.raiz.title("Generador de Diagramas Lógicos")
        self.raiz.geometry("500x300")

        ttk.Label(raiz, text="Entradas (separadas por comas):").pack(pady=5)
        self.entradas_entry = ttk.Entry(raiz, width=50)
        self.entradas_entry.pack(pady=5)

        ttk.Label(raiz, text="Salidas (separadas por comas):").pack(pady=5)
        self.salidas_entry = ttk.Entry(raiz, width=50)
        self.salidas_entry.pack(pady=5)

        ttk.Label(raiz, text="Expresiones Lógicas (una por salida):").pack(pady=5)
        self.expresiones_entry = ttk.Entry(raiz, width=50)
        self.expresiones_entry.pack(pady=5)

        ttk.Button(raiz, text="Generar Diagrama", command=self.generar_diagrama).pack(pady=10)

    def generar_diagrama(self):
        entradas = [entrada.strip() for entrada in self.entradas_entry.get().split(",")]
        salidas = [salida.strip() for salida in self.salidas_entry.get().split(",")]
        expresiones = [eval(expr.strip()) for expr in self.expresiones_entry.get().split(",")]

        generador = GeneradorDiagramaLogico()
        generador.generar_diagrama_completo(entradas, salidas, expresiones)
        os.system("diagrama_logico.png")


class GeneradorDiagramaLogico:
    def __init__(self):
        self.dot = Digraph("Diagrama Lógico", format="png")
        self.dot.attr(rankdir="LR")
        self.dot.attr(dpi="300")
        self.ids_entradas = {}
        self.ids_unicos = 0
        self.conexiones = set()

    def _generar_id_unico(self):
        self.ids_unicos += 1
        return f"nodo_{self.ids_unicos}"

    def _procesar_expresion(self, expr, nodo_padre):
        if expr in self.ids_entradas:  # Si ya existe, conecta directamente
            self._agregar_arista(self.ids_entradas[expr], nodo_padre)
            return

        if isinstance(expr, symbols):
            if expr.name not in self.ids_entradas:  # Evita duplicados
                id_nodo = self._generar_id_unico()
                self.dot.node(id_nodo, label=expr.name, shape="ellipse")
                self.ids_entradas[expr.name] = id_nodo
            self._agregar_arista(self.ids_entradas[expr.name], nodo_padre)
        elif isinstance(expr, Not):
            id_nodo = self._generar_id_unico()
            self.dot.node(id_nodo, label="", image="not_gate.png", shape="none", labelloc="b")
            self._procesar_expresion(expr.args[0], id_nodo)
            self._agregar_arista(id_nodo, nodo_padre)
        elif isinstance(expr, And):
            id_nodo = self._generar_id_unico()
            self.dot.node(id_nodo, label="", image="and_gate.png", shape="none", labelloc="b")
            for subexpr in expr.args:
                self._procesar_expresion(subexpr, id_nodo)
            self._agregar_arista(id_nodo, nodo_padre)
        elif isinstance(expr, Or):
            id_nodo = self._generar_id_unico()
            self.dot.node(id_nodo, label="", image="or_gate.png", shape="none", labelloc="b")
            for subexpr in expr.args:
                self._procesar_expresion(subexpr, id_nodo)
            self._agregar_arista(id_nodo, nodo_padre)

    def _agregar_arista(self, nodo_origen, nodo_destino):
        conexion = (nodo_origen, nodo_destino)
        if conexion not in self.conexiones:
            self.conexiones.add(conexion)
            self.dot.edge(nodo_origen, nodo_destino)

    def generar_diagrama_completo(self, entradas, salidas, expresiones):
        for entrada in entradas:
            if entrada not in self.ids_entradas:  # Evita duplicados
                id_nodo = self._generar_id_unico()
                self.dot.node(id_nodo, label=entrada, shape="ellipse")
                self.ids_entradas[entrada] = id_nodo

        for salida, expresion in zip(salidas, expresiones):
            id_salida = self._generar_id_unico()
            self.dot.node(id_salida, label=salida, shape="doublecircle")
            self._procesar_expresion(expresion, id_salida)

        self.dot.render("diagrama_logico", format="png", cleanup=True)


if __name__ == "__main__":
    raiz = tk.Tk()
    app = AplicacionLogica(raiz)
    raiz.mainloop()
