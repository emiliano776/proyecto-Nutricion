"""
NUTRICALC - Calculadora nutricional educativa
Requisitos: Python 3.10+ (usa tkinter, incluido habitualmente con Python).
Ejecución: python nutricalc.py

IMPORTANTE:
- Herramienta educativa/prototipo; no sustituye el juicio profesional.
- El gasto energético es una estimación mediante Mifflin-St Jeor y factor de actividad.
- Los ajustes energéticos y macros son parámetros iniciales editables, no prescripciones universales.
- Los valores de alimentos son aproximados por 100 g de porción comestible y deben verificarse
  contra una base de composición de alimentos confiable antes de uso clínico.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from itertools import product
from datetime import datetime

# Valores aproximados por 100 g de alimento; leche expresada por 100 ml.
# Verificar y reemplazar con una base de composición de alimentos validada.
ALIMENTOS = {
    "Avena seca":              {"kcal": 389, "proteinas": 16.9, "carbohidratos": 66.3, "grasas": 6.9},
    "Arroz blanco cocido":     {"kcal": 130, "proteinas": 2.7,  "carbohidratos": 28.2, "grasas": 0.3},
    "Fideos cocidos":          {"kcal": 157, "proteinas": 5.8,  "carbohidratos": 30.9, "grasas": 0.9},
    "Pan blanco":              {"kcal": 266, "proteinas": 8.9,  "carbohidratos": 49.4, "grasas": 3.2},
    "Papa hervida":            {"kcal": 87,  "proteinas": 1.9,  "carbohidratos": 20.1, "grasas": 0.1},
    "Batata hervida":          {"kcal": 76,  "proteinas": 1.4,  "carbohidratos": 17.7, "grasas": 0.1},
    "Lentejas cocidas":        {"kcal": 116, "proteinas": 9.0,  "carbohidratos": 20.1, "grasas": 0.4},
    "Garbanzos cocidos":       {"kcal": 164, "proteinas": 8.9,  "carbohidratos": 27.4, "grasas": 2.6},
    "Pollo cocido sin piel":   {"kcal": 165, "proteinas": 31.0, "carbohidratos": 0.0,  "grasas": 3.6},
    "Carne vacuna magra cocida":{"kcal": 217,"proteinas": 26.0, "carbohidratos": 0.0,  "grasas": 12.0},
    "Merluza cocida":          {"kcal": 110, "proteinas": 23.0, "carbohidratos": 0.0,  "grasas": 1.5},
    "Huevo entero":            {"kcal": 143, "proteinas": 12.6, "carbohidratos": 0.7,  "grasas": 9.5},
    "Leche entera (100 ml)":   {"kcal": 61,  "proteinas": 3.2,  "carbohidratos": 4.8,  "grasas": 3.3},
    "Yogur natural entero":    {"kcal": 61,  "proteinas": 3.5,  "carbohidratos": 4.7,  "grasas": 3.3},
    "Queso fresco":            {"kcal": 264, "proteinas": 18.0, "carbohidratos": 3.1,  "grasas": 20.0},
    "Manzana":                 {"kcal": 52,  "proteinas": 0.3,  "carbohidratos": 13.8, "grasas": 0.2},
    "Banana":                  {"kcal": 89,  "proteinas": 1.1,  "carbohidratos": 22.8, "grasas": 0.3},
    "Naranja":                 {"kcal": 47,  "proteinas": 0.9,  "carbohidratos": 11.8, "grasas": 0.1},
    "Palta":                   {"kcal": 160, "proteinas": 2.0,  "carbohidratos": 8.5,  "grasas": 14.7},
    "Almendras":               {"kcal": 579, "proteinas": 21.2, "carbohidratos": 21.6, "grasas": 49.9},
    "Aceite de oliva":         {"kcal": 884, "proteinas": 0.0,  "carbohidratos": 0.0,  "grasas": 100.0},
    "Tomate":                  {"kcal": 18,  "proteinas": 0.9,  "carbohidratos": 3.9,  "grasas": 0.2},
    "Zanahoria":               {"kcal": 41,  "proteinas": 0.9,  "carbohidratos": 9.6,  "grasas": 0.2},
    "Zapallo":                 {"kcal": 26,  "proteinas": 1.0,  "carbohidratos": 6.5,  "grasas": 0.1},
}

FACTORES_ACTIVIDAD = {
    "Sedentaria (1,20)": 1.20,
    "Ligera (1,375)": 1.375,
    "Moderada (1,55)": 1.55,
    "Alta (1,725)": 1.725,
    "Muy alta (1,90)": 1.90,
}

AJUSTES_OBJETIVO = {
    "Bajar de peso (-15%)": -0.15,
    "Mantener peso (0%)": 0.0,
    "Subir de peso (+10%)": 0.10,
    "Mejorar hábitos (mantenimiento inicial)": 0.0,
}


def numero_positivo(texto, nombre, permitir_cero=False):
    try:
        valor = float(texto.strip().replace(",", "."))
    except (ValueError, AttributeError):
        raise ValueError(f"{nombre}: ingresá un número válido.")
    if valor < 0 or (valor == 0 and not permitir_cero):
        comparacion = "mayor o igual a cero" if permitir_cero else "mayor que cero"
        raise ValueError(f"{nombre}: el valor debe ser {comparacion}.")
    return valor


class NutriCalc:
    def __init__(self, root):
        self.root = root
        self.root.title("NutriCalc | Calculadora nutricional")
        self.root.geometry("1180x820")
        self.root.minsize(900, 650)
        self.alimentos_seleccionados = []
        self.ultimo_informe = ""
        self._crear_interfaz()

    def _crear_interfaz(self):
        contenedor = ttk.Frame(self.root, padding=12)
        contenedor.pack(fill="both", expand=True)

        titulo = ttk.Label(contenedor, text="NUTRICALC", font=("Arial", 20, "bold"))
        titulo.pack(anchor="w")
        ttk.Label(
            contenedor,
            text="Entrevista, evaluación antropométrica, estimación energética y tabla de alimentos",
        ).pack(anchor="w", pady=(0, 10))

        notebook = ttk.Notebook(contenedor)
        notebook.pack(fill="both", expand=True)

        self.tab_datos = ttk.Frame(notebook, padding=12)
        self.tab_resultados = ttk.Frame(notebook, padding=12)
        self.tab_alimentos = ttk.Frame(notebook, padding=12)
        self.tab_matematica = ttk.Frame(notebook, padding=12)
        notebook.add(self.tab_datos, text="1. Entrevista y cálculo")
        notebook.add(self.tab_resultados, text="2. Informe y fórmulas")
        notebook.add(self.tab_alimentos, text="3. Tabla de alimentos")
        notebook.add(self.tab_matematica, text="4. Matemática UTN")

        self._crear_tab_datos()
        self._crear_tab_resultados()
        self._crear_tab_alimentos()
        self._crear_tab_matematica()

        aviso = (
            "Prototipo educativo: los cálculos y la base alimentaria requieren revisión profesional. "
            "No usar como prescripción automática."
        )
        ttk.Label(contenedor, text=aviso, foreground="#8a3b12", wraplength=1100).pack(
            anchor="w", pady=(8, 0)
        )

    def _crear_tab_datos(self):
        frame = self.tab_datos
        frame.columnconfigure(1, weight=1)
        frame.columnconfigure(3, weight=1)

        campos = [
            ("Nombre", "nombre"),
            ("Edad (años)", "edad"),
            ("Peso (kg)", "peso"),
            ("Talla (cm)", "talla"),
            ("Grasa corporal (%) — opcional", "grasa"),
            ("Cintura (cm) — opcional", "cintura"),
            ("Perímetro de brazo (cm) — opcional", "brazo"),
        ]
        self.vars = {}
        for idx, (etiqueta, clave) in enumerate(campos):
            fila = idx // 2
            col = (idx % 2) * 2
            ttk.Label(frame, text=etiqueta).grid(row=fila, column=col, sticky="w", padx=5, pady=7)
            var = tk.StringVar()
            self.vars[clave] = var
            ttk.Entry(frame, textvariable=var, width=27).grid(
                row=fila, column=col + 1, sticky="ew", padx=5, pady=7
            )

        fila = (len(campos) + 1) // 2
        ttk.Label(frame, text="Sexo para ecuación Mifflin-St Jeor").grid(
            row=fila, column=0, sticky="w", padx=5, pady=7
        )
        self.sexo = tk.StringVar(value="Femenino")
        ttk.Combobox(
            frame, textvariable=self.sexo, values=["Femenino", "Masculino"],
            state="readonly", width=24
        ).grid(row=fila, column=1, sticky="ew", padx=5, pady=7)

        ttk.Label(frame, text="Actividad física").grid(
            row=fila, column=2, sticky="w", padx=5, pady=7
        )
        self.actividad = tk.StringVar(value="Sedentaria (1,20)")
        ttk.Combobox(
            frame, textvariable=self.actividad, values=list(FACTORES_ACTIVIDAD),
            state="readonly", width=27
        ).grid(row=fila, column=3, sticky="ew", padx=5, pady=7)

        fila += 1
        ttk.Label(frame, text="Objetivo").grid(row=fila, column=0, sticky="w", padx=5, pady=7)
        self.objetivo = tk.StringVar(value="Mantener peso (0%)")
        ttk.Combobox(
            frame, textvariable=self.objetivo, values=list(AJUSTES_OBJETIVO),
            state="readonly", width=27
        ).grid(row=fila, column=1, sticky="ew", padx=5, pady=7)

        ttk.Label(frame, text="Factor proteico (g/kg) — editable").grid(
            row=fila, column=2, sticky="w", padx=5, pady=7
        )
        self.factor_proteina = tk.StringVar(value="1.6")
        ttk.Entry(frame, textvariable=self.factor_proteina, width=27).grid(
            row=fila, column=3, sticky="ew", padx=5, pady=7
        )

        fila += 1
        ttk.Label(frame, text="Antecedentes / observaciones (opcional)").grid(
            row=fila, column=0, sticky="nw", padx=5, pady=7
        )
        self.antecedentes = tk.Text(frame, height=4, width=50, wrap="word")
        self.antecedentes.grid(row=fila, column=1, columnspan=3, sticky="nsew", padx=5, pady=7)

        fila += 1
        botones = ttk.Frame(frame)
        botones.grid(row=fila, column=0, columnspan=4, sticky="w", pady=12)
        ttk.Button(botones, text="Calcular e informar", command=self.calcular).pack(side="left", padx=(0, 8))
        ttk.Button(botones, text="Limpiar formulario", command=self.limpiar).pack(side="left", padx=8)
        ttk.Label(
            frame,
            text=("La ecuación Mifflin-St Jeor se usa aquí como estimación para adultos. "
                  "Los ajustes de objetivo (-15%, 0%, +10%) son valores iniciales editables en el código."),
            wraplength=1000,
        ).grid(row=fila + 1, column=0, columnspan=4, sticky="w", padx=5, pady=8)

    def _crear_tab_resultados(self):
        barra = ttk.Frame(self.tab_resultados)
        barra.pack(fill="x", pady=(0, 8))
        ttk.Button(barra, text="Guardar informe TXT", command=self.guardar_informe).pack(side="left")
        self.texto_informe = tk.Text(self.tab_resultados, wrap="word", font=("Consolas", 10))
        self.texto_informe.pack(fill="both", expand=True)

    def _crear_tab_alimentos(self):
        frame = self.tab_alimentos
        controles = ttk.Frame(frame)
        controles.pack(fill="x", pady=(0, 10))
        ttk.Label(controles, text="Alimento").pack(side="left")
        self.alimento_var = tk.StringVar(value=next(iter(ALIMENTOS)))
        ttk.Combobox(
            controles, textvariable=self.alimento_var, values=list(ALIMENTOS),
            state="readonly", width=30
        ).pack(side="left", padx=6)
        ttk.Label(controles, text="Cantidad (g o ml)").pack(side="left", padx=(10, 0))
        self.cantidad_var = tk.StringVar(value="100")
        ttk.Entry(controles, textvariable=self.cantidad_var, width=10).pack(side="left", padx=6)
        ttk.Button(controles, text="Agregar alimento", command=self.agregar_alimento).pack(side="left", padx=6)
        ttk.Button(controles, text="Quitar seleccionado", command=self.quitar_alimento).pack(side="left", padx=6)
        ttk.Button(controles, text="Vaciar tabla", command=self.vaciar_alimentos).pack(side="left", padx=6)

        columnas = ("alimento", "cantidad", "kcal", "proteinas", "carbohidratos", "grasas")
        self.tabla = ttk.Treeview(frame, columns=columnas, show="headings", height=14)
        titulos = {
            "alimento": "Alimento", "cantidad": "Cantidad (g/ml)", "kcal": "kcal",
            "proteinas": "Proteínas (g)", "carbohidratos": "Carbohidratos (g)", "grasas": "Grasas (g)"
        }
        anchos = {"alimento": 230, "cantidad": 120, "kcal": 90, "proteinas": 120,
                  "carbohidratos": 150, "grasas": 100}
        for col in columnas:
            self.tabla.heading(col, text=titulos[col])
            self.tabla.column(col, width=anchos[col], anchor="center")
        self.tabla.pack(fill="both", expand=True)

        self.totales_label = ttk.Label(frame, text="Totales: 0 kcal | Proteínas: 0 g | Carbohidratos: 0 g | Grasas: 0 g")
        self.totales_label.pack(anchor="w", pady=10)
        self.comparacion_label = ttk.Label(frame, text="Calculá primero el objetivo diario para comparar los alimentos.", wraplength=1000)
        self.comparacion_label.pack(anchor="w", pady=(0, 8))
        ttk.Label(
            frame,
            text="Base de ejemplo con valores aproximados por 100 g (leche por 100 ml). Confirmar datos, estado crudo/cocido y porción comestible.",
            wraplength=1000,
        ).pack(anchor="w")

    def _crear_tab_matematica(self):
        ttk.Label(
            self.tab_matematica,
            text="Aplicaciones matemáticas incluidas",
            font=("Arial", 13, "bold")
        ).pack(anchor="w", pady=(0, 8))
        texto = tk.Text(self.tab_matematica, wrap="word", font=("Consolas", 10))
        texto.pack(fill="both", expand=True)
        contenido = [
            "1) Álgebra de Boole: validar datos con condiciones como peso > 0 AND talla > 0.",
            "",
            "Tabla de verdad para V = P AND T:",
            "P  T  | V",
            "0  0  | 0",
            "0  1  | 0",
            "1  0  | 0",
            "1  1  | 1",
            "",
            "2) Sistema binario: el programa convierte el gasto energético redondeado a binario.",
            "Ejemplo: 2200 en decimal = 100010011100 en binario.",
            "",
            "3) Cálculos aritméticos: IMC, ecuación predictiva, factor de actividad, ajustes energéticos",
            "y distribución de macronutrientes.",
            "",
            "4) Conversión energética aproximada:",
            "Proteínas: 4 kcal/g; carbohidratos: 4 kcal/g; grasas: 9 kcal/g.",
            "",
            "5) Limitación: el módulo de alimentos suma nutrientes de una base demostrativa; no diseña",
            "automáticamente una dieta clínica ni verifica adecuación de micronutrientes, fibra, sodio,",
            "alergias, interacciones, preferencias, textura o indicaciones médicas.",
        ]
        texto.insert("1.0", "\n".join(contenido))
        texto.configure(state="disabled")

    def calcular(self):
        try:
            nombre = self.vars["nombre"].get().strip()
            if not nombre:
                raise ValueError("Ingresá el nombre del paciente.")
            edad = numero_positivo(self.vars["edad"].get(), "Edad")
            peso = numero_positivo(self.vars["peso"].get(), "Peso")
            talla_cm = numero_positivo(self.vars["talla"].get(), "Talla")
            if edad < 18 or edad > 120:
                raise ValueError("Esta versión está orientada a adultos de 18 a 120 años.")
            if peso < 25 or peso > 350:
                raise ValueError("Revisá el peso ingresado (rango de control del programa: 25 a 350 kg).")
            if talla_cm < 100 or talla_cm > 230:
                raise ValueError("Revisá la talla ingresada (rango de control: 100 a 230 cm).")
            talla_m = talla_cm / 100

            grasa_txt = self.vars["grasa"].get().strip()
            cintura_txt = self.vars["cintura"].get().strip()
            brazo_txt = self.vars["brazo"].get().strip()
            grasa = numero_positivo(grasa_txt, "Grasa corporal", permitir_cero=True) if grasa_txt else None
            if grasa is not None and grasa > 75:
                raise ValueError("Revisá el porcentaje de grasa corporal (máximo de control: 75%).")
            cintura = numero_positivo(cintura_txt, "Cintura", permitir_cero=True) if cintura_txt else None
            brazo = numero_positivo(brazo_txt, "Perímetro de brazo", permitir_cero=True) if brazo_txt else None

            factor_proteina = numero_positivo(self.factor_proteina.get(), "Factor proteico")
            if factor_proteina > 3.5:
                raise ValueError("Revisá el factor proteico: debe ser menor o igual a 3,5 g/kg en este prototipo.")

            imc = peso / (talla_m ** 2)
            if imc < 18.5:
                clasificacion = "Bajo peso (punto de corte orientativo para adultos)"
            elif imc < 25:
                clasificacion = "Intervalo de peso normal (punto de corte orientativo para adultos)"
            elif imc < 30:
                clasificacion = "Sobrepeso (punto de corte orientativo para adultos)"
            elif imc < 35:
                clasificacion = "Obesidad grado I (punto de corte orientativo para adultos)"
            elif imc < 40:
                clasificacion = "Obesidad grado II (punto de corte orientativo para adultos)"
            else:
                clasificacion = "Obesidad grado III (punto de corte orientativo para adultos)"

            edad_int = int(round(edad))
            if self.sexo.get() == "Masculino":
                bmr = 10 * peso + 6.25 * talla_cm - 5 * edad_int + 5
                ecuacion_sexo = "+ 5 (constante masculina)"
            else:
                bmr = 10 * peso + 6.25 * talla_cm - 5 * edad_int - 161
                ecuacion_sexo = "- 161 (constante femenina)"

            factor_actividad = FACTORES_ACTIVIDAD[self.actividad.get()]
            gasto_estimado = bmr * factor_actividad
            ajuste = AJUSTES_OBJETIVO[self.objetivo.get()]
            energia_objetivo = gasto_estimado * (1 + ajuste)

            proteinas_g = peso * factor_proteina
            grasas_g = energia_objetivo * 0.25 / 9
            carbohidratos_g = (energia_objetivo - proteinas_g * 4 - grasas_g * 9) / 4
            if carbohidratos_g < 0:
                raise ValueError(
                    "Con este factor proteico, la energía no alcanza para calcular carbohidratos positivos. "
                    "Reducí el factor proteico o revisá el objetivo energético."
                )

            kcal_proteinas = proteinas_g * 4
            kcal_carbohidratos = carbohidratos_g * 4
            kcal_grasas = grasas_g * 9
            kcal_macros = kcal_proteinas + kcal_carbohidratos + kcal_grasas
            binario = format(int(round(energia_objetivo)), "b")

            self.resultados = {
                "nombre": nombre, "edad": edad_int, "peso": peso, "talla_cm": talla_cm,
                "talla_m": talla_m, "grasa": grasa, "cintura": cintura, "brazo": brazo,
                "imc": imc, "clasificacion": clasificacion, "bmr": bmr,
                "factor_actividad": factor_actividad, "gasto_estimado": gasto_estimado,
                "ajuste": ajuste, "energia_objetivo": energia_objetivo,
                "factor_proteina": factor_proteina, "proteinas_g": proteinas_g,
                "carbohidratos_g": carbohidratos_g, "grasas_g": grasas_g,
                "kcal_proteinas": kcal_proteinas, "kcal_carbohidratos": kcal_carbohidratos,
                "kcal_grasas": kcal_grasas, "kcal_macros": kcal_macros, "binario": binario,
                "objetivo": self.objetivo.get(), "actividad": self.actividad.get(),
                "sexo": self.sexo.get(), "antecedentes": self.antecedentes.get("1.0", "end").strip(),
                "ecuacion_sexo": ecuacion_sexo,
            }
            self.ultimo_informe = self._generar_informe()
            self.texto_informe.configure(state="normal")
            self.texto_informe.delete("1.0", "end")
            self.texto_informe.insert("1.0", self.ultimo_informe)
            self.texto_informe.configure(state="disabled")
            self.comparar_alimentos()
            messagebox.showinfo("Cálculo finalizado", "Se generó el informe. Revisá la pestaña 'Informe y fórmulas'.")
        except ValueError as error:
            messagebox.showerror("Revisar datos", str(error))

    def _generar_informe(self):
        r = self.resultados
        lineas = [
            "=" * 68,
            "NUTRICALC - INFORME NUTRICIONAL EDUCATIVO",
            "=" * 68,
            f"Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M')}",
            f"Paciente: {r['nombre']}",
            f"Edad: {r['edad']} años | Sexo de ecuación: {r['sexo']}",
            f"Peso: {r['peso']:.2f} kg | Talla: {r['talla_cm']:.1f} cm ({r['talla_m']:.2f} m)",
            f"Objetivo seleccionado: {r['objetivo']}",
            f"Actividad: {r['actividad']} (factor {r['factor_actividad']:.3f})",
            "",
            "1. EVALUACIÓN ANTROPOMÉTRICA",
            f"IMC = peso (kg) / talla (m)^2",
            f"IMC = {r['peso']:.2f} / ({r['talla_m']:.2f}^2)",
            f"IMC = {r['imc']:.2f} kg/m²",
            f"Clasificación orientativa: {r['clasificacion']}",
        ]
        if r["grasa"] is not None:
            lineas.append(f"Grasa corporal informada: {r['grasa']:.1f}%")
        if r["cintura"] is not None:
            lineas.append(f"Perímetro de cintura informado: {r['cintura']:.1f} cm")
        if r["brazo"] is not None:
            lineas.append(f"Perímetro de brazo informado: {r['brazo']:.1f} cm")

        lineas += [
            "",
            "2. ESTIMACIÓN ENERGÉTICA (Mifflin-St Jeor, adultos)",
            "Hombre: GER = 10 × peso + 6,25 × talla(cm) − 5 × edad + 5",
            "Mujer:  GER = 10 × peso + 6,25 × talla(cm) − 5 × edad − 161",
            f"GER = 10 × {r['peso']:.2f} + 6,25 × {r['talla_cm']:.1f} − 5 × {r['edad']} {r['ecuacion_sexo']}",
            f"GER estimado = {r['bmr']:.1f} kcal/día",
            f"Gasto estimado = GER × factor de actividad",
            f"Gasto estimado = {r['bmr']:.1f} × {r['factor_actividad']:.3f} = {r['gasto_estimado']:.1f} kcal/día",
            f"Ajuste inicial por objetivo = {r['ajuste'] * 100:+.0f}%",
            f"Energía objetivo = {r['gasto_estimado']:.1f} × (1 {r['ajuste']:+.2f}) = {r['energia_objetivo']:.1f} kcal/día",
            "",
            "3. DISTRIBUCIÓN DE MACRONUTRIENTES",
            f"Proteínas = peso × factor proteico = {r['peso']:.2f} × {r['factor_proteina']:.2f} = {r['proteinas_g']:.1f} g/día",
            f"Energía de proteínas = {r['proteinas_g']:.1f} × 4 = {r['kcal_proteinas']:.1f} kcal",
            f"Grasas = 25% de energía / 9 = ({r['energia_objetivo']:.1f} × 0.25) / 9 = {r['grasas_g']:.1f} g/día",
            f"Energía de grasas = {r['grasas_g']:.1f} × 9 = {r['kcal_grasas']:.1f} kcal",
            f"Carbohidratos = (energía objetivo − kcal proteínas − kcal grasas) / 4",
            f"Carbohidratos = ({r['energia_objetivo']:.1f} − {r['kcal_proteinas']:.1f} − {r['kcal_grasas']:.1f}) / 4 = {r['carbohidratos_g']:.1f} g/día",
            f"Energía de carbohidratos = {r['carbohidratos_g']:.1f} × 4 = {r['kcal_carbohidratos']:.1f} kcal",
            f"Comprobación: energía de macros = {r['kcal_macros']:.1f} kcal/día",
            "",
            "4. SISTEMA BINARIO (contenido complementario de Matemática)",
            f"Energía objetivo redondeada: {int(round(r['energia_objetivo']))} en decimal = {r['binario']} en binario",
            "",
            "5. ANTECEDENTES / OBSERVACIONES",
            r["antecedentes"] if r["antecedentes"] else "No se registraron observaciones.",
            "",
            "NOTAS Y LIMITACIONES",
            "- Los resultados son estimaciones y deben ser evaluados por un profesional.",
            "- El ajuste energético inicial y la distribución de macros son parámetros simplificados y editables.",
            "- No se aplica automáticamente un protocolo para diabetes, enfermedad renal, embarazo, deportistas, etc.",
            "- El IMC no es un diagnóstico por sí solo; interpretar junto con historia clínica y otras medidas.",
            "- La base de alimentos es ilustrativa. Verificar composición, preparación y porción antes de uso clínico.",
        ]
        return "\n".join(lineas)

    def guardar_informe(self):
        contenido = self.ultimo_informe
        if not contenido:
            messagebox.showwarning("Sin informe", "Primero calculá los datos del paciente.")
            return
        ruta = filedialog.asksaveasfilename(
            title="Guardar informe",
            defaultextension=".txt",
            filetypes=[("Archivo de texto", "*.txt")],
            initialfile="informe_nutricalc.txt",
        )
        if ruta:
            try:
                with open(ruta, "w", encoding="utf-8") as archivo:
                    archivo.write(contenido)
                messagebox.showinfo("Guardado", f"Informe guardado en:\n{ruta}")
            except OSError as error:
                messagebox.showerror("Error al guardar", str(error))

    def agregar_alimento(self):
        try:
            nombre = self.alimento_var.get()
            if nombre not in ALIMENTOS:
                raise ValueError("Seleccioná un alimento de la lista.")
            cantidad = numero_positivo(self.cantidad_var.get(), "Cantidad")
            datos = ALIMENTOS[nombre]
            factor = cantidad / 100
            fila = {
                "nombre": nombre, "cantidad": cantidad,
                "kcal": datos["kcal"] * factor,
                "proteinas": datos["proteinas"] * factor,
                "carbohidratos": datos["carbohidratos"] * factor,
                "grasas": datos["grasas"] * factor,
            }
            self.alimentos_seleccionados.append(fila)
            self.tabla.insert(
                "", "end",
                values=(
                    fila["nombre"], f"{fila['cantidad']:.1f}",
                    f"{fila['kcal']:.1f}", f"{fila['proteinas']:.1f}",
                    f"{fila['carbohidratos']:.1f}", f"{fila['grasas']:.1f}"
                )
            )
            self.actualizar_totales()
        except ValueError as error:
            messagebox.showerror("Revisar alimento", str(error))

    def quitar_alimento(self):
        seleccion = self.tabla.selection()
        if not seleccion:
            messagebox.showwarning("Seleccioná una fila", "Elegí el alimento que querés quitar.")
            return
        indices = sorted((self.tabla.index(item) for item in seleccion), reverse=True)
        for item in seleccion:
            self.tabla.delete(item)
        for indice in indices:
            if 0 <= indice < len(self.alimentos_seleccionados):
                self.alimentos_seleccionados.pop(indice)
        self.actualizar_totales()

    def vaciar_alimentos(self):
        self.alimentos_seleccionados.clear()
        for item in self.tabla.get_children():
            self.tabla.delete(item)
        self.actualizar_totales()

    def actualizar_totales(self):
        totales = {clave: sum(f[clave] for f in self.alimentos_seleccionados)
                   for clave in ("kcal", "proteinas", "carbohidratos", "grasas")}
        self.totales_label.config(
            text=(f"Totales: {totales['kcal']:.1f} kcal | "
                  f"Proteínas: {totales['proteinas']:.1f} g | "
                  f"Carbohidratos: {totales['carbohidratos']:.1f} g | "
                  f"Grasas: {totales['grasas']:.1f} g")
        )
        self.comparar_alimentos(totales)

    def comparar_alimentos(self, totales=None):
        if not hasattr(self, "comparacion_label"):
            return
        if not hasattr(self, "resultados") or self.resultados is None:
            self.comparacion_label.config(text="Calculá primero el objetivo diario para comparar los alimentos.")
            return
        if totales is None:
            totales = {clave: sum(f[clave] for f in self.alimentos_seleccionados)
                       for clave in ("kcal", "proteinas", "carbohidratos", "grasas")}
        r = self.resultados
        self.comparacion_label.config(
            text=(
                f"Objetivos diarios estimados: {r['energia_objetivo']:.0f} kcal; "
                f"proteínas {r['proteinas_g']:.1f} g; carbohidratos {r['carbohidratos_g']:.1f} g; "
                f"grasas {r['grasas_g']:.1f} g.  |  "
                f"Alimentos ingresados: {totales['kcal']:.0f} kcal; "
                f"proteínas {totales['proteinas']:.1f} g; carbohidratos {totales['carbohidratos']:.1f} g; "
                f"grasas {totales['grasas']:.1f} g."
            )
        )

    def limpiar(self):
        for var in self.vars.values():
            var.set("")
        self.sexo.set("Femenino")
        self.actividad.set("Sedentaria (1,20)")
        self.objetivo.set("Mantener peso (0%)")
        self.factor_proteina.set("1.6")
        self.antecedentes.delete("1.0", "end")
        self.resultados = None if hasattr(self, "resultados") else None
        self.ultimo_informe = ""
        self.texto_informe.configure(state="normal")
        self.texto_informe.delete("1.0", "end")
        self.texto_informe.configure(state="disabled")
        self.vaciar_alimentos()
        messagebox.showinfo("Formulario limpio", "Se borraron los datos ingresados.")


def main():
    root = tk.Tk()
    NutriCalc(root)
    root.mainloop()


if __name__ == "__main__":
    main()
