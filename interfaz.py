import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
from PIL import Image, ImageTk
from comparacion import ComparadorImagenes
import sys


class Button(tk.Canvas):
    def __init__(self, parent, text, command=None, bg_color="#7289DA", hover_color="#5B6EAE", 
                 text_color="white", width=120, height=40, corner_radius=8):
        super().__init__(parent, width=width, height=height, highlightthickness=0)
        
        self.command = command
        self.bg_color = bg_color
        self.hover_color = hover_color
        self.text_color = text_color
        self.corner_radius = corner_radius
        self.text = text
        self.path_output = None
        
        self.draw_button()
        self.bind("<Button-1>", self.on_click)
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)
        
        self.config(cursor="hand2")
        
    def draw_button(self, color=None):
        self.delete("all")
        if color is None:
            color = self.bg_color
            
        self.create_rounded_rect(2, 2, self.winfo_reqwidth()-2, self.winfo_reqheight()-2, 
                               self.corner_radius, fill=color, outline="")
        
        self.create_text(self.winfo_reqwidth()//2, self.winfo_reqheight()//2, 
                        text=self.text, fill=self.text_color, font=("Segoe UI", 10, "bold"))
    
    def create_rounded_rect(self, x1, y1, x2, y2, radius, **kwargs):
        points = []
        for x, y in [(x1, y1 + radius), (x1, y1), (x1 + radius, y1),
                     (x2 - radius, y1), (x2, y1), (x2, y1 + radius),
                     (x2, y2 - radius), (x2, y2), (x2 - radius, y2),
                     (x1 + radius, y2), (x1, y2), (x1, y2 - radius)]:
            points.extend([x, y])
        return self.create_polygon(points, smooth=True, **kwargs)
    
    def on_click(self, event):
        if self.command:
            self.command()
    
    def on_enter(self, event):
        self.draw_button(self.hover_color)
    
    def on_leave(self, event):
        self.draw_button(self.bg_color)

class Frame(tk.Frame):
    def __init__(self, parent, bg_color="#23272A", border_color="#99AAB5", corner_radius=12, **kwargs):
        super().__init__(parent, bg=bg_color, **kwargs)
        self.bg_color = bg_color
        self.border_color = border_color
        self.corner_radius = corner_radius

class ImageHashComparator:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Comparador de Imagenes")
        self.root.geometry("1000x800")
      


        self.root.configure(bg="#2C2F33")

        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        self.style.configure("Modern.TCombobox",
                           fieldbackground="#23272A",
                           background="#23272A",
                           foreground="white",
                           borderwidth=1,
                           relief="solid",
                           arrowcolor="#7289DA")
        
        self.original_image = None
        self.compare_images = []
        self.current_compare_index = 0
        self.original_photo = None
        self.compare_photo = None
        
        # Referencias a los widgets de imagen
        self.original_image_label = None
        self.compare_image_label = None
        self.original_info_label = None
        self.compare_info_label = None
        
        self.setup_ui()
        
    def setup_ui(self):
        main_container = tk.Frame(self.root, bg="#2C2F33")
        main_container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Header
        header_frame = tk.Frame(main_container, bg="#2C2F33")
        header_frame.pack(fill="x", pady=(0, 20))
        
        title_label = tk.Label(header_frame, text="Algoritmo Hash", 
                              font=("Segoe UI", 18, "bold"), 
                              bg="#2C2F33", fg="#FFFFFF")
        title_label.pack(side="left")
        
        algo_frame = tk.Frame(header_frame, bg="#2C2F33")
        algo_frame.pack(side="right")
        
        self.algorithm_var = tk.StringVar(value="ORB")
        algorithm_combo = ttk.Combobox(algo_frame, textvariable=self.algorithm_var,
                                     values=["ORB", "pHash", "Histograma"],
                                     style="Modern.TCombobox",
                                     state="readonly", width=20)
        algorithm_combo.pack()
        
        algorithm_combo.config(cursor="hand2")
        
        # Content frame
        content_frame = tk.Frame(main_container, bg="#2C2F33")
        content_frame.pack(fill="both", expand=True)
        
        # Images container
        images_container = tk.Frame(content_frame, bg="#2C2F33")
        images_container.pack(fill="both", expand=True, pady=(0, 20))
        
        # Original image section
        self.original_section = self.create_original_image_section(images_container)
        self.original_section.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        # Compare images section
        self.compare_section = self.create_compare_image_section(images_container)
        self.compare_section.pack(side="right", fill="both", expand=True, padx=(10, 0))
        
        # Bottom frame
        bottom_frame = tk.Frame(content_frame, bg="#2C2F33")
        bottom_frame.pack(fill="x")
        
        # Navigation frame
        nav_frame = tk.Frame(bottom_frame, bg="#2C2F33")
        nav_frame.pack(pady=(0, 20))
        
        self.prev_btn = Button(nav_frame, "Anterior", self.prev_image, 
                                   bg_color="#99AAB5", hover_color="#7289DA", width=80, height=35)
        self.prev_btn.pack(side="left", padx=5)
        
        self.page_label = tk.Label(nav_frame, text="0 de 0", 
                                  font=("Segoe UI", 10), bg="#2C2F33", fg="#FFFFFF")
        self.page_label.pack(side="left", padx=20)
        
        self.next_btn = Button(nav_frame, "Siguiente", self.next_image,
                                   bg_color="#99AAB5", hover_color="#7289DA", width=80, height=35)
        self.next_btn.pack(side="left", padx=5)
        
        # Compare button
        compare_btn = Button(bottom_frame, "COMPARAR", self.comparar_imagenes_hash,
                                 bg_color="#43B581", hover_color="#3CA374", 
                                 width=200, height=50, corner_radius=10)
        compare_btn.pack()
        
        self.update_navigation()
        
    def create_original_image_section(self, parent):
        section_frame = Frame(parent, bg_color="#23272A", relief="solid", bd=1)
        
        title_label = tk.Label(section_frame, text="Imagen original", 
                              font=("Segoe UI", 12, "bold"), 
                              bg="#23272A", fg="#FFFFFF")
        title_label.pack(pady=10)
        
        # Frame para la imagen
        image_frame = tk.Frame(section_frame, bg="#2C2F33", relief="solid", bd=1)
        image_frame.config(cursor="hand2")
        image_frame.pack(fill="both", expand=True, padx=20, pady=(0, 10))
        
        # Label para mostrar la imagen
        self.original_image_label = tk.Label(image_frame, bg="#2C2F33", fg="#99AAB5",
                                           text="Click para cargar imagen", 
                                           font=("Segoe UI", 10))
        self.original_image_label.pack(expand=True, pady=20)
        
        # Label para información de la imagen
        self.original_info_label = tk.Label(section_frame, bg="#23272A", fg="#99AAB5",
                                          text="", font=("Segoe UI", 8))
        self.original_info_label.pack(pady=(0, 10))
        
        # Bind click events
        image_frame.bind("<Button-1>", lambda e: self.load_original_image())
        self.original_image_label.bind("<Button-1>", lambda e: self.load_original_image())
        
        return section_frame
    
    def create_compare_image_section(self, parent):
        section_frame = Frame(parent, bg_color="#23272A", relief="solid", bd=1)
        
        title_label = tk.Label(section_frame, text="Imágenes a comparar", 
                              font=("Segoe UI", 12, "bold"), 
                              bg="#23272A", fg="#FFFFFF")
        title_label.pack(pady=10)
        
        # Frame para la imagen
        image_frame = tk.Frame(section_frame, bg="#2C2F33", relief="solid", bd=1)
        image_frame.config(cursor="hand2")
        image_frame.pack(fill="both", expand=True, padx=20, pady=(0, 10))
        
        # Label para mostrar la imagen
        self.compare_image_label = tk.Label(image_frame, bg="#2C2F33", fg="#99AAB5",
                                          text="Click para cargar imagen(es)", 
                                          font=("Segoe UI", 10))
        self.compare_image_label.pack(expand=True, pady=20)
        
        # Label para información de la imagen
        self.compare_info_label = tk.Label(section_frame, bg="#23272A", fg="#99AAB5",
                                         text="", font=("Segoe UI", 8))
        self.compare_info_label.pack(pady=(0, 10))
        
        # Bind click events
        image_frame.bind("<Button-1>", lambda e: self.load_compare_images())
        self.compare_image_label.bind("<Button-1>", lambda e: self.load_compare_images())
        
        return section_frame
    
    def resize_image(self, image_path, max_width=500, max_height=400):
        """Redimensiona una imagen manteniendo la proporción"""
        try:
            with Image.open(image_path) as img:
                # Convertir a RGB si es necesario
                if img.mode in ('RGBA', 'LA', 'P'):
                    img = img.convert('RGB')
                
                # Calcular el nuevo tamaño manteniendo la proporción
                img.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
                return ImageTk.PhotoImage(img)
        except Exception as e:
            print(f"Error al redimensionar imagen: {e}")
            return None
    
    def load_original_image(self):
        file_path = filedialog.askopenfilename(
            title="Seleccionar imagen original",
            filetypes=[("Archivos de imagen", "*.jpg *.jpeg *.png *.bmp *.gif *.tiff *.webp")]
        )
        if file_path:
            self.original_image = file_path
            
            # Cargar y mostrar la imagen
            self.original_photo = self.resize_image(file_path)
            if self.original_photo:
                self.original_image_label.configure(image=self.original_photo, text="")
                self.original_info_label.configure(text=f"Archivo: {os.path.basename(file_path)}")
            else:
                self.original_image_label.configure(text="Error al cargar imagen")
                self.original_info_label.configure(text="")
            
            messagebox.showinfo("Éxito", f"Imagen original cargada: {os.path.basename(file_path)}")
    
    def load_compare_images(self):
        file_paths = filedialog.askopenfilenames(
            title="Seleccionar imágenes a comparar",
            filetypes=[("Archivos de imagen", "*.jpg *.jpeg *.png *.bmp *.gif *.tiff *.webp")]
        )
        if file_paths:
            self.compare_images = list(file_paths)
            self.current_compare_index = 0
            self.update_compare_image_display()
            self.update_navigation()
            messagebox.showinfo("Éxito", f"{len(file_paths)} imágenes cargadas para comparar")
    
    def update_compare_image_display(self):
        """Actualiza la visualización de la imagen de comparación actual"""
        if self.compare_images and 0 <= self.current_compare_index < len(self.compare_images):
            current_image_path = self.compare_images[self.current_compare_index]
            
            # Cargar y mostrar la imagen
            self.compare_photo = self.resize_image(current_image_path)
            if self.compare_photo:
                self.compare_image_label.configure(image=self.compare_photo, text="")
                filename = os.path.basename(current_image_path)
                info_text = f"Archivo: {filename}\n({self.current_compare_index + 1} de {len(self.compare_images)})"
                self.compare_info_label.configure(text=info_text)
            else:
                self.compare_image_label.configure(text="Error al cargar imagen")
                self.compare_info_label.configure(text="")
        else:
            self.compare_image_label.configure(image="", text="Click para cargar imagen(es)")
            self.compare_info_label.configure(text="")
    
    def prev_image(self):
        """Navegar a la imagen anterior"""
        if self.compare_images and self.current_compare_index > 0:
            self.current_compare_index -= 1
            self.update_compare_image_display()
            self.update_navigation()
    
    def next_image(self):
        """Navegar a la siguiente imagen"""
        if self.compare_images and self.current_compare_index < len(self.compare_images) - 1:
            self.current_compare_index += 1
            self.update_compare_image_display()
            self.update_navigation()
    
    def update_navigation(self):
        """Actualiza el estado de los botones de navegación y el label"""
        if self.compare_images:
            total = len(self.compare_images)
            current = self.current_compare_index + 1
            self.page_label.config(text=f"{current} de {total}")
            
            # Habilitar/deshabilitar botones
            if hasattr(self, 'prev_btn'):
                if self.current_compare_index <= 0:
                    self.prev_btn.configure(state='disabled')
                else:
                    self.prev_btn.configure(state='normal')
                    
            if hasattr(self, 'next_btn'):
                if self.current_compare_index >= len(self.compare_images) - 1:
                    self.next_btn.configure(state='disabled')
                else:
                    self.next_btn.configure(state='normal')
        else:
            self.page_label.config(text="0 de 0")
    
    def format_results(self, resultados: list[dict]) -> str:
        """
        Recibe una lista de resultados de comparación (pHash, ORB o Histograma) y devuelve un string formateado.
        """
        if not resultados:
            return "⚠️ No se encontraron resultados para mostrar."

        texto = "📊 RESULTADOS DE COMPARACIÓN DE IMÁGENES\n"
        texto += "=" * 60 + "\n"

        for idx, resultado in enumerate(resultados, 1):
            imagen = resultado.get('imagen', 'Desconocida')
            texto += f"🖼️ Imagen {self.current_compare_index +1}:\n"
            texto += f"   📍 Ruta: {imagen}\n"

            # Detectar tipo de resultado: pHash, ORB o Histograma
            if 'diferencia' in resultado:  # Caso pHash
                diferencia = resultado.get('diferencia', 'N/A')
                son_similares = resultado.get('son_similares', False)
                hash_original = resultado.get('hash_original', 'N/A')
                hash_comparada = resultado.get('hash_comparada', 'N/A')
                estado = "✅ Similares" if son_similares else "❌ Diferentes"
                texto += f"   #️⃣ Hash de imagen original: {hash_original}\n"
                texto += f"   #️⃣ Hash de imagen comparada: {hash_comparada}\n"
                texto += f"   🔍 Diferencia pHash: {diferencia}\n"
                texto += f"   📌 Resultado: {estado}\n"
                
            elif 'coincidencias' in resultado:  # Caso ORB
                coincidencias = resultado.get('coincidencias', 'N/A')
                buenas = resultado.get('coincidencias_buenas', 'N/A')
                kp1 = resultado.get('total_keypoints_original', 'N/A')
                kp2 = resultado.get('total_keypoints_comparada', 'N/A')
                porcentaje = resultado.get('porcentaje_coincidencias', 'N/A')
                porcentaje_buenas = resultado.get('porcentaje_buenas', 'N/A')
                path_output = resultado.get('pathOutput', 'No disponible')
                self.path_output = path_output

                texto += f"   🔍 Coincidencias ORB: {coincidencias} totales, {buenas} buenas / {min(kp1, kp2)} puntos clave\n"
                texto += f"   🎯 Porcentaje coincidencias: {porcentaje}, Buenas: {porcentaje_buenas}\n"
                texto += f"   💾 Imagen comparada guardada en: {path_output}\n"
                texto += f"   📌 *Nota: Una coincidencia es buena si el punto clave de una imagen realmente se corresponde con el punto clave de la otra.\n"

            elif 'similitud' in resultado:  # Caso Histograma
                similitud = resultado.get('similitud', 'N/A')
                son_similares = resultado.get('son_similares', False)
                estado = "✅ Similares" if son_similares else "❌ Diferentes"
                texto += f"   🔍 Similitud Histograma: {similitud}\n"
                texto += f"   📌 Resultado: {estado}\n"

            else:
                texto += "   ⚠️ Formato de resultado desconocido.\n"

            texto += "-" * 60 + "\n"

        return texto

    def comparar_imagenes_hash(self):
        if not self.original_image:
            messagebox.showerror("Error", "¡Primero cargue una imagen original!")
            return
        if not self.compare_images:
            messagebox.showerror("Error", "¡Cargue imágenes para comparar!")
            return
    
        # Disable all widgets and set wait cursor
        self._set_procesamiento(True)
        # Programar la comparación para ejecutarse después de un breve retraso
        self.root.after(100, self._comparar_after)
        
    def _comparar_after(self):
        try:
            algorithm = self.algorithm_var.get()
            comparator = ComparadorImagenes(self.original_image)
            current_image = self.compare_images[self.current_compare_index]
            
            if algorithm == "ORB":
                results = comparator.compare_ORB([current_image], saveOutput=True)
            elif algorithm == "pHash":
                results = comparator.compare_pHash([current_image])
            elif algorithm == "Histograma":
                results = comparator.compare_histogramas([current_image])
            else:
                raise ValueError("Algoritmo no reconocido")
            
            # Pasar los resultados directamente
            self.root.after(0, self._mostrar_resultados_reinicia_cursor, results)
        except Exception as e:
            # Pasar el mensaje de error directamente
            self.root.after(0, self._manejar_error_reinicia_cursor, str(e))

    def _set_procesamiento(self, processing):
        """Gestiona el estado de procesamiento (cursor, estado de widgets)"""
        if processing:
            # 1. Guardar cursores originales
            self._original_cursors = {}
            self._guardar_cursores(self.root)
            
            # 2. Deshabilitar todos los widgets (excepto la ventana principal)
            self._deshabilitar_widgets(self.root)
            
            # 3. Cambiar cursor a "wait"
            if sys.platform.startswith('win'):
                self._set_cursores_recursivo(self.root, "wait")
                self.root.config(cursor="wait")
            elif sys.platform.startswith('linux'):
                self._set_cursores_recursivo(self.root, "watch")
                self.root.config(cursor="watch")
        else:
            # 1. Habilitar todos los widgets
            self._habilitar_widgets(self.root)
            
            # 2. Restaurar cursores originales
            self._restablecer_cursores(self.root)
            self.root.config(cursor="")

    def _guardar_cursores(self, widget):
        """Guarda los cursores originales de todos los widgets"""
        try:
            self._original_cursors[widget] = widget.cget("cursor")
        except:
            pass
        
        for child in widget.winfo_children():
            self._guardar_cursores(child)

    def _restablecer_cursores(self, widget):
        """Restaura los cursores originales"""
        if widget in self._original_cursors:
            try:
                widget.config(cursor=self._original_cursors[widget])
            except:
                pass
        
        for child in widget.winfo_children():
            self._restablecer_cursores(child)

    def _set_cursores_recursivo(self, widget, cursor):
        """Establece un cursor recursivamente en todos los widgets"""
        try:
            widget.config(cursor=cursor)
        except:
            pass
        
        for child in widget.winfo_children():
            self._set_cursores_recursivo(child, cursor)

    def _deshabilitar_widgets(self, parent):
        """Deshabilita recursivamente todos los widgets hijos"""
        for child in parent.winfo_children():
            try:
                # Solo deshabilitar widgets que soporten state
                if 'state' in child.keys():
                    child.config(state='disabled')
            except Exception as e:
                print(f"No se pudo deshabilitar widget: {e}")
            
            # Procesar hijos recursivamente
            if hasattr(child, 'winfo_children'):
                self._deshabilitar_widgets(child)

    def _habilitar_widgets(self, parent):
        """Habilita recursivamente todos los widgets hijos"""
        for child in parent.winfo_children():
            try:
                # Solo habilitar widgets que soporten state
                if 'state' in child.keys():
                    child.config(state='normal')
            except Exception as e:
                print(f"No se pudo habilitar widget: {e}")
            
            # Procesar hijos recursivamente
            if hasattr(child, 'winfo_children'):
                self._habilitar_widgets(child)

    def _mostrar_resultados_reinicia_cursor(self, results):
        self.show_results_window(self.format_results(results))
        self._set_procesamiento(False)

    def _manejar_error_reinicia_cursor(self, error_msg):
        messagebox.showerror("Error", f"Ocurrió un error al comparar: {error_msg}")
        self._set_procesamiento(False)
    
    def show_results_window(self, results_text):
        results_window = tk.Toplevel(self.root)
        results_window.title("Resultados de comparación")
        results_window.geometry("600x600")  # Aumenta la altura para mostrar la imagen
        results_window.configure(bg="#2C2F33")

        text_frame = tk.Frame(results_window, bg="#2C2F33")
        text_frame.pack(fill="both", expand=True, padx=20, pady=10)

        text_widget = tk.Text(text_frame, wrap="word", font=("Consolas", 10),
                            bg="#23272A", fg="#FFFFFF", relief="solid", bd=1, height=15)
        text_widget.pack(fill="both", expand=True)



        text_widget.insert("1.0", results_text)
        text_widget.configure(state="disabled")
        algorithm = self.algorithm_var.get()


        if algorithm == "ORB":
            image_frame = tk.Frame(results_window, bg="#2C2F33")
            image_frame.pack(fill="both", expand=True, padx=20, pady=10)

            img = Image.open(self.path_output)
            img = img.resize((500, 300), Image.LANCZOS)  # Redimensiona para encajar en la ventana
            img_tk = ImageTk.PhotoImage(img)

            img_label = tk.Label(image_frame, image=img_tk, bg="#2C2F33")
            img_label.image = img_tk  # Previene garbage collection
            img_label.pack()

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = ImageHashComparator()
    app.run()
