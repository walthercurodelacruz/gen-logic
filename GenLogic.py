import tkinter as tk
from tkinter import ttk, messagebox
from sympy import symbols, simplify_logic
from sympy.logic.boolalg import And, Or, Not
from graphviz import Digraph

class AplicacionLogica:
    def __init__(self, raiz):
        self.raiz = raiz
        self.raiz.title("Generador de Circuitos Lógicos")
        self.entradas = []
        self.salidas = []
        self.tabla = []
        self.expresiones = []

        # Configuración general
        self.raiz.geometry("600x600")
        self.raiz.resizable(False, False)
        self.estilo = ttk.Style()
        self.estilo.theme_use("clam")
        self.estilo.configure("TButton", font=("Arial", 10, "bold"), padding=5)
        self.estilo.configure("TLabel", font=("Arial", 10))
        self.estilo.configure("TEntry", font=("Arial", 10))

        self.configurar_interfaz()

    def configurar_interfaz(self):
        # Marco principal
        marco_principal = ttk.Frame(self.raiz, padding=10)
        marco_principal.pack(fill=tk.BOTH, expand=True)

        # Entradas
        etiqueta_entrada = ttk.Label(marco_principal, text="Entradas:")
        etiqueta_entrada.grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.var_entrada = tk.StringVar()
        campo_entrada = ttk.Entry(marco_principal, textvariable=self.var_entrada, width=30)
        campo_entrada.grid(row=0, column=1, sticky="w", padx=5, pady=5)
        boton_entrada = ttk.Button(marco_principal, text="Añadir", command=self.agregar_entrada)
        boton_entrada.grid(row=0, column=2, sticky="w", padx=5, pady=5)

        # Salidas
        etiqueta_salida = ttk.Label(marco_principal, text="Salidas:")
        etiqueta_salida.grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.var_salida = tk.StringVar()
        campo_salida = ttk.Entry(marco_principal, textvariable=self.var_salida, width=30)
        campo_salida.grid(row=1, column=1, sticky="w", padx=5, pady=5)
        boton_salida = ttk.Button(marco_principal, text="Añadir", command=self.agregar_salida)
        boton_salida.grid(row=1, column=2, sticky="w", padx=5, pady=5)

        # Tabla de verdad
        self.marco_tabla = ttk.Frame(marco_principal)
        self.marco_tabla.grid(row=2, column=0, columnspan=3, pady=10)

        # Generar expresión y diagrama
        boton_generar_tabla = ttk.Button(marco_principal, text="Expresión Booleana", command=self.generar_exp_booleana)
        boton_generar_tabla.grid(row=3, column=0, pady=10, columnspan=3)

        self.etiqueta_expr = ttk.Label(marco_principal, text="Expresión simplificada:")
        self.etiqueta_expr.grid(row=4, column=0, columnspan=3, sticky="w", pady=10)

        boton_generar_diagrama = ttk.Button(marco_principal, text="Generar Diagrama", command=self.generar_diagrama)
        boton_generar_diagrama.grid(row=5, column=0, pady=10, columnspan=3)

        # Botón de reset
        boton_reset = ttk.Button(marco_principal, text="Resetear", command=self.resetear)
        boton_reset.grid(row=6, column=0, pady=10, columnspan=3)

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
            ttk.Label(self.marco_tabla, text=nombre).grid(row=0, column=col)

        self.tabla = [[tk.StringVar() for _ in columnas] for _ in range(2 ** len(self.entradas))]
        for idx_fila, fila_vars in enumerate(self.tabla):
            valores_binarios = format(idx_fila, f"0{len(self.entradas)}b")
            for idx_col, var in enumerate(fila_vars):
                if idx_col < len(self.entradas):
                    var.set(valores_binarios[idx_col])
                ttk.Entry(self.marco_tabla, textvariable=var, width=5).grid(row=idx_fila + 1, column=idx_col)

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


if __name__ == "__main__":
    raiz = tk.Tk()
    app = AplicacionLogica(raiz)
    raiz.mainloop()
