import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from AnalizadorLexico import lexer  # Tu analizador léxico con PLY

class AnalizadorLexicoApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("COMPILADORES - Analizador Léxico")
        self.geometry("1000x650")
        self.config(bg="#ffffff")
        self.ruta_archivo = None
        self.resultados_tokens = []
        self.font_size = 12

        self.crear_widgets()

    def crear_widgets(self):
        # Configuración de la cuadrícula principal
        self.grid_rowconfigure(0, weight=0)  # Fila para botones (no se expande)
        self.grid_rowconfigure(1, weight=3)  # Fila para editor (se expande más)
        self.grid_rowconfigure(2, weight=1)   # Fila para consola (se expande menos)
        self.grid_columnconfigure(0, weight=4)  # Columna izquierda (editor)
        self.grid_columnconfigure(1, weight=1)  # Columna derecha (opcional)

        # Frame para los botones en la parte superior
        frame_botones = tk.Frame(self, bg="#ffffff")
        frame_botones.grid(row=0, column=0, columnspan=2, sticky="nsew", padx=10, pady=(10, 5))
        
        # Configurar grid interno para los botones
        for i in range(7):  # 7 columnas para los botones
            frame_botones.grid_columnconfigure(i, weight=1)

        estilo_btn = {"bg": "#e0e0e0", "fg": "#000000", "font": ("Segoe UI", 10, "bold"),
                     "relief": tk.RAISED, "bd": 1, "padx": 10, "pady": 5}

        # Botones
        tk.Button(frame_botones, text="Abrir Archivo", command=self.abrir_archivo, **estilo_btn).grid(row=0, column=0, sticky="ew", padx=2)
        tk.Button(frame_botones, text="Guardar", command=self.guardar_archivo, **estilo_btn).grid(row=0, column=1, sticky="ew", padx=2)
        tk.Button(frame_botones, text="Guardar como", command=self.guardar_como, **estilo_btn).grid(row=0, column=2, sticky="ew", padx=2)
        tk.Button(frame_botones, text="Analizar Léxico", command=self.analizar_lexico, 
                 bg="#4CAF50", fg="white", font=("Segoe UI", 10, "bold")).grid(row=0, column=3, sticky="ew", padx=2)
        tk.Button(frame_botones, text="Ver Tokens", command=self.ver_tokens, 
                 bg="#2196F3", fg="white", font=("Segoe UI", 10, "bold")).grid(row=0, column=4, sticky="ew", padx=2)
        tk.Button(frame_botones, text="+ Zoom", command=self.zoom_in, **estilo_btn).grid(row=0, column=5, sticky="ew", padx=2)
        tk.Button(frame_botones, text="- Zoom", command=self.zoom_out, **estilo_btn).grid(row=0, column=6, sticky="ew", padx=2)

        # Frame principal para el editor (ocupa la columna 0)
        frame_editor_principal = tk.Frame(self, bg="#f0f0f0")
        frame_editor_principal.grid(row=1, column=0, sticky="nsew", padx=(10, 5), pady=(0, 10))
        frame_editor_principal.grid_rowconfigure(0, weight=1)
        frame_editor_principal.grid_columnconfigure(0, weight=1)

        # Frame interno para el editor con números de línea
        frame_editor = tk.Frame(frame_editor_principal)
        frame_editor.grid(row=0, column=0, sticky="nsew")
        frame_editor.grid_rowconfigure(0, weight=1)
        frame_editor.grid_columnconfigure(1, weight=1)  # Columna del editor principal

        # Números de línea
        self.lineas = tk.Text(frame_editor, width=4, padx=5, takefocus=0, border=0,
                            background="#eeeeee", foreground="gray", state='disabled',
                            font=("Consolas", self.font_size))
        self.lineas.grid(row=0, column=0, sticky="ns")

        # Editor de texto principal
        self.texto = tk.Text(frame_editor, wrap=tk.NONE, font=("Consolas", self.font_size), undo=True)
        self.texto.grid(row=0, column=1, sticky="nsew")

        # Scroll vertical
        scroll_y = ttk.Scrollbar(frame_editor, orient=tk.VERTICAL, command=self._scroll_both)
        scroll_y.grid(row=0, column=2, sticky="ns")

        self.texto.config(bg="#1e1e1e", fg="#d4d4d4", insertbackground="white",
                         yscrollcommand=self._yscroll)
        self.lineas.config(yscrollcommand=self._yscroll)

        # Frame para la consola (ocupa la fila 2 y ambas columnas)
        frame_consola = tk.Frame(self, bg="#f0f0f0")
        frame_consola.grid(row=2, column=0, columnspan=2, sticky="nsew", padx=10, pady=(0, 10))
        frame_consola.grid_rowconfigure(0, weight=1)
        frame_consola.grid_columnconfigure(0, weight=1)

        # Consola
        self.consola = tk.Text(frame_consola, height=10, bg="#f4f4f4", fg="#222222", 
                              font=("Consolas", 11), wrap=tk.WORD)
        self.consola.grid(row=0, column=0, sticky="nsew")
        self.consola.insert(tk.END, "Esperando análisis léxico...\n")
        self.consola.config(state='disabled')

        # Scroll para la consola
        scroll_consola = ttk.Scrollbar(frame_consola, orient=tk.VERTICAL, command=self.consola.yview)
        scroll_consola.grid(row=0, column=1, sticky="ns")
        self.consola.config(yscrollcommand=scroll_consola.set)

        # Eventos para actualizar números de línea
        self.texto.bind("<KeyRelease>", self.actualizar_numeros_linea)
        self.texto.bind("<MouseWheel>", self.actualizar_numeros_linea)
        self.texto.bind("<Button-1>", self.actualizar_numeros_linea)
        self.texto.bind("<Configure>", self.actualizar_numeros_linea)

        self.actualizar_numeros_linea()

    # Resto de los métodos permanecen igual...
    def _yscroll(self, *args):
        try:
            self.texto.yview(*args)
            self.lineas.yview(*args)
        except tk.TclError:
            pass

    def _scroll_both(self, *args):
        self.texto.yview(*args)
        self.lineas.yview(*args)

    def actualizar_numeros_linea(self, event=None):
        self.lineas.config(state='normal')
        self.lineas.delete("1.0", tk.END)
        total_lineas = int(self.texto.index('end-1c').split('.')[0])
        lineas = "\n".join(str(i) for i in range(1, total_lineas + 1))
        self.lineas.insert("1.0", lineas)
        self.lineas.config(state='disabled')

    def abrir_archivo(self):
        ruta = filedialog.askopenfilename(filetypes=[("Todos los archivos", "*.*")])
        if ruta:
            with open(ruta, "r", encoding="utf-8") as f:
                self.texto.delete(1.0, tk.END)
                self.texto.insert(tk.END, f.read())
            self.ruta_archivo = ruta
            self.mostrar_en_consola(f"Archivo cargado: {ruta}")
            self.actualizar_numeros_linea()
        self.texto.tag_remove("error", "1.0", tk.END)

    def guardar_archivo(self):
        if not self.ruta_archivo:
            self.ruta_archivo = filedialog.asksaveasfilename(defaultextension=".txt")
        if self.ruta_archivo:
            with open(self.ruta_archivo, "w", encoding="utf-8") as f:
                f.write(self.texto.get(1.0, tk.END))
            self.mostrar_en_consola(f"Archivo guardado: {self.ruta_archivo}")
        self.texto.tag_remove("error", "1.0", tk.END)

    def guardar_como(self):
        ruta = filedialog.asksaveasfilename(defaultextension=".txt")
        if ruta:
            with open(ruta, "w", encoding="utf-8") as f:
                f.write(self.texto.get(1.0, tk.END))
            self.mostrar_en_consola(f"Archivo guardado como: {ruta}")

    def zoom_in(self):
        self.font_size += 2
        self.actualizar_fuente()

    def zoom_out(self):
        if self.font_size > 6:
            self.font_size -= 2
        self.actualizar_fuente()

    def actualizar_fuente(self):
        self.texto.config(font=("Consolas", self.font_size))
        self.lineas.config(font=("Consolas", self.font_size))

    def obtener_columna(self, codigo, lexpos):
        last_newline = codigo.rfind('\n', 0, lexpos)
        return lexpos - last_newline

    def analizar_lexico(self):
        from AnalizadorLexico import lexer, errores_lexicos, limpiar_errores
        
        # Obtener el código ingresado en el área de texto
        codigo = self.texto.get("1.0", tk.END)

        # Limpiar la consola antes de mostrar nuevos resultados
        self.consola.config(state='normal')  # Asegúrate de que la consola esté en modo 'normal'
        self.consola.delete("1.0", tk.END)  # Limpiar todo el contenido de la consola

        # Resetear el contador de líneas a 1
        lexer.lineno = 1

        # Ejecutar el lexer sobre el código
        lexer.input(codigo)
        self.resultados_tokens = []

        # Realizar el análisis léxico
        while True:
            tok = lexer.token()
            if not tok:
                break
            if tok.type != 'ERROR':  # Si no es un error, procesar el token
                columna = self.obtener_columna(codigo, tok.lexpos)
                self.resultados_tokens.append((tok.value, tok.type, tok.lineno, columna))

        # Mostrar los errores léxicos en la consola si los hay
        self.texto.tag_remove("error", "1.0", tk.END)
        self.texto.tag_config("error", background="#ffcccc", foreground="red")

        for error in errores_lexicos:
            if hasattr(error, 'lineno') and hasattr(error, 'lexpos'):
                linea = int(error.lineno)
                col = self.obtener_columna(codigo, error.lexpos)
                inicio = f"{linea}.{col - 1}"
                fin = f"{linea}.{col}"
                self.texto.tag_add("error", inicio, fin)

        # Si no se encontraron tokens válidos
        if not self.resultados_tokens:
            self.mostrar_en_consola("No se encontraron tokens válidos.")
        else:
            self.mostrar_en_consola("Tokens encontrados: Análisis léxico completado.")

        # Deshabilitar la consola para evitar ediciones
        self.consola.config(state='disabled')
        limpiar_errores()

    def ver_tokens(self):
        if self.resultados_tokens:
            VentanaToken(self, self.resultados_tokens)
        else:
            messagebox.showinfo("Sin análisis", "Primero debes ejecutar el análisis léxico.")

    def mostrar_en_consola(self, mensaje):
        self.consola.config(state='normal')
        self.consola.insert(tk.END, mensaje + "\n")
        self.consola.see(tk.END)
        self.consola.config(state='disabled')


class VentanaToken(tk.Toplevel):
    def __init__(self, master, resultados):
        super().__init__(master)
        self.title("Tokens Reconocidos")
        self.config(bg="#f9f9f9")
        self.resultados = resultados
        self.centrar_ventana(500, 400)
        self.style = ttk.Style(self)
        self.style.theme_use("default")
        self.style.configure("Treeview", font=("Segoe UI", 10), rowheight=25)
        self.style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"), background="#cccccc")
        self.crear_widgets()

    def crear_widgets(self):
        frame_editor = tk.Frame(self)
        frame_editor.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Tabla de tokens
        self.treeview = ttk.Treeview(frame_editor, columns=("Valor", "Tipo", "Línea", "Columna"), show="headings")
        self.treeview.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)

        self.treeview.heading("Valor", text="Valor")
        self.treeview.heading("Tipo", text="Tipo")
        self.treeview.heading("Línea", text="Línea")
        self.treeview.heading("Columna", text="Columna")

        for token in self.resultados:
            self.treeview.insert("", "end", values=token)

        # Scroll vertical
        scroll_y = ttk.Scrollbar(frame_editor, orient=tk.VERTICAL)
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        scroll_y.config(command=self.treeview.yview)

        self.treeview.config(yscrollcommand=scroll_y.set)

    def centrar_ventana(self, ancho, alto):
        pantalla_ancho = self.winfo_screenwidth()
        pantalla_alto = self.winfo_screenheight()
        x = (pantalla_ancho - ancho) // 2
        y = (pantalla_alto - alto) // 2
        self.geometry(f"{ancho}x{alto}+{x}+{y}")
        
if __name__ == "__main__":
    app = AnalizadorLexicoApp()
    app.mainloop()