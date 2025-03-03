import tkinter as tk
from tkinter import messagebox, simpledialog
import csv
import json
import os
import re
from datetime import datetime

def load_corpus_csv(filename):
    """Carga el corpus desde un archivo CSV y lo guarda en un conjunto."""
    corpus_set = set()
    try:
        with open('corpus_rae.csv', "r", encoding="utf-8") as csvfile:
            # Intentar leer el CSV con encabezado
            reader = csv.DictReader(csvfile)
            if reader.fieldnames is not None:
                if 'term' in reader.fieldnames:
                    column_name = 'term'
                elif 'término' in reader.fieldnames:
                    column_name = 'término'
                else:
                    column_name = None
            else:
                column_name = None

            if column_name:
                for row in reader:
                    term = row[column_name].strip()
                    if term:
                        corpus_set.add(term.lower())
            else:
                # Si no se detecta encabezado, leer la primera columna
                csvfile.seek(0)
                reader = csv.reader(csvfile)
                for row in reader:
                    if row:
                        corpus_set.add(row[0].strip().lower())
    except FileNotFoundError:
        messagebox.showerror("Error", f"El archivo del corpus '{filename}' no se encontró.")
    except Exception as e:
        messagebox.showerror("Error", f"Error al leer el corpus: {e}")
    return corpus_set

def save_new_term(term, json_filename, morph_tag):
    """Guarda el término y su etiqueta morfosintáctica en un archivo JSON, evitando duplicados."""
    data = {"términos": []}
    if os.path.exists(json_filename):
        try:
            with open(json_filename, "r", encoding="utf-8") as f:
                data = json.load(f)
        except json.JSONDecodeError:
            data = {"términos": []}
    
    # Verificar si el término ya está guardado
    if not any(item["término"].lower() == term.lower() for item in data["términos"]):
        new_entry = {
            "término": term,
            "fecha": datetime.now().strftime("%Y-%m-%d"),
            "estado": "posible neologismo",
            "etiqueta_morfosintáctica": morph_tag
        }
        data["términos"].append(new_entry)
        with open(json_filename, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

class NeologismoApp:
    def __init__(self, root, corpus_filename="corpus.csv", output_filename="neologismos.json"):
        self.root = root
        self.root.title("Detector de Neologismos")
        
        # Cargar el corpus desde el CSV
        self.corpus = load_corpus_csv(corpus_filename)
        print("Términos cargados del corpus:", self.corpus)  # Para verificar en consola
        self.output_filename = output_filename
        
        # Sección de análisis de término individual
        self.label = tk.Label(root, text="Introduce el término:")
        self.label.pack(pady=5)
        
        self.entry = tk.Entry(root, width=50)
        self.entry.pack(pady=5)
        
        self.button = tk.Button(root, text="Analizar Término", command=self.analizar_termino)
        self.button.pack(pady=5)
        
        self.result_label = tk.Label(root, text="", font=("Arial", 12))
        self.result_label.pack(pady=10)
        
        # Línea separadora
        separator = tk.Frame(root, height=2, bd=1, relief=tk.SUNKEN)
        separator.pack(fill=tk.X, padx=5, pady=10)
        
        # Sección de análisis de texto
        self.label_texto = tk.Label(root, text="Introduce el texto a analizar:")
        self.label_texto.pack(pady=5)
        
        self.text_widget = tk.Text(root, height=10, width=50)
        self.text_widget.pack(pady=5)
        
        self.button_texto = tk.Button(root, text="Analizar Texto", command=self.analizar_texto)
        self.button_texto.pack(pady=5)
    
    def analizar_termino(self):
        term = self.entry.get().strip()
        if not term:
            messagebox.showinfo("Información", "Por favor, introduce un término.")
            return
        
        if term.lower() in self.corpus:
            self.result_label.config(text="Término encontrado en el corpus.", fg="green")
        else:
            self.result_label.config(text="Posible neologismo.", fg="red")
            # Preguntar por la etiqueta morfosintáctica para el término individual
            morph_tag = simpledialog.askstring("Etiqueta morfosintáctica", 
                                                 f"Introduce la etiqueta morfosintáctica para '{term}':")
            if morph_tag is None:
                morph_tag = ""
            save_new_term(term, self.output_filename, morph_tag)
        
        # Limpiar el campo de entrada
        self.entry.delete(0, tk.END)
    
    def analizar_texto(self):
        text = self.text_widget.get("1.0", tk.END).strip()
        if not text:
            messagebox.showinfo("Información", "Por favor, introduce un texto para analizar.")
            return
        
        # Extraer palabras (tokens) del texto
        words = re.findall(r"\b\w+\b", text, re.UNICODE)
        unknown_terms = set()
        for word in words:
            if word.lower() not in self.corpus:
                unknown_terms.add(word)
        
        if not unknown_terms:
            messagebox.showinfo("Información", "Todos los términos están en el corpus.")
            return
        
        # Iterar por cada término desconocido y preguntar si se desea guardar
        for term in sorted(unknown_terms):
            respuesta = messagebox.askyesno("Guardar Término", 
                                            f"El término '{term}' no se encuentra en el corpus. ¿Deseas guardarlo?")
            if respuesta:
                morph_tag = simpledialog.askstring("Etiqueta morfosintáctica", 
                                                    f"Introduce la etiqueta morfosintáctica para '{term}':")
                if morph_tag is None:
                    morph_tag = ""
                save_new_term(term, self.output_filename, morph_tag)
        messagebox.showinfo("Información", "Análisis de texto completado.")

if __name__ == "__main__":
    root = tk.Tk()
    app = NeologismoApp(root)
    root.mainloop()