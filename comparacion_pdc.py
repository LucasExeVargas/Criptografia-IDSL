import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import hashlib
import io
import numpy as np
from skimage.metrics import structural_similarity as ssim

class VerificadorIntegridadImagenes(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Verificador de Integridad de Imágenes")
        self.geometry("800x600")
        self.configure(bg="#f0f0f0")

        self.ruta_imagen_referencia = None
        self.ruta_imagen_prueba = None
        self.hash_referencia = None
        self.hash_prueba = None

        self.marco_principal = tk.Frame(self, bg="#f0f0f0")
        self.marco_principal.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        self.marco_ref = tk.LabelFrame(self.marco_principal, text="Imagen de Referencia", bg="#f0f0f0", font=("Arial", 12))
        self.marco_ref.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        self.marco_prueba = tk.LabelFrame(self.marco_principal, text="Imagen de Prueba", bg="#f0f0f0", font=("Arial", 12))
        self.marco_prueba.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

        self.marco_principal.grid_columnconfigure(0, weight=1)
        self.marco_principal.grid_columnconfigure(1, weight=1)
        self.marco_principal.grid_rowconfigure(0, weight=1)
        self.marco_principal.grid_rowconfigure(1, weight=0)

        self.etiqueta_imagen_ref = tk.Label(self.marco_ref, bg="white", width=40, height=15)
        self.etiqueta_imagen_ref.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.etiqueta_imagen_prueba = tk.Label(self.marco_prueba, bg="white", width=40, height=15)
        self.etiqueta_imagen_prueba.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.marco_botones = tk.Frame(self.marco_principal, bg="#f0f0f0")
        self.marco_botones.grid(row=1, column=0, columnspan=2, pady=10)

        self.boton_cargar_ref = tk.Button(
            self.marco_botones,
            text="Cargar Imagen de Referencia",
            command=self.cargar_imagen_referencia,
            bg="#4CAF50",
            fg="white",
            font=("Arial", 10, "bold"),
            padx=10,
            pady=5
        )
        self.boton_cargar_ref.grid(row=0, column=0, padx=10)

        self.boton_cargar_prueba = tk.Button(
            self.marco_botones,
            text="Cargar Imagen de Prueba",
            command=self.cargar_imagen_prueba,
            bg="#2196F3",
            fg="white",
            font=("Arial", 10, "bold"),
            padx=10,
            pady=5
        )
        self.boton_cargar_prueba.grid(row=0, column=1, padx=10)

        self.boton_verificar = tk.Button(
            self.marco_botones,
            text="Verificar Integridad",
            command=self.verificar_integridad,
            bg="#FF9800",
            fg="white",
            font=("Arial", 10, "bold"),
            padx=10,
            pady=5
        )
        self.boton_verificar.grid(row=0, column=2, padx=10)

        self.marco_resultados = tk.LabelFrame(self.marco_principal, text="Resultado de Verificación", bg="#f0f0f0", font=("Arial", 12))
        self.marco_resultados.grid(row=2, column=0, columnspan=2, padx=10, pady=10, sticky="ew")

        self.etiqueta_resultado = tk.Label(
            self.marco_resultados,
            text="Cargue ambas imágenes y haga clic en 'Verificar Integridad'",
            bg="#f0f0f0",
            font=("Arial", 12),
            padx=10,
            pady=10
        )
        self.etiqueta_resultado.pack(fill=tk.X)

        self.marco_hash = tk.Frame(self.marco_principal, bg="#f0f0f0")
        self.marco_hash.grid(row=3, column=0, columnspan=2, padx=10, pady=5, sticky="ew")

        self.etiqueta_hash_ref = tk.Label(self.marco_hash, text="Hash de Referencia: Ninguno", bg="#f0f0f0", font=("Courier", 10))
        self.etiqueta_hash_ref.pack(anchor="w")

        self.etiqueta_hash_prueba = tk.Label(self.marco_hash, text="Hash de Prueba: Ninguno", bg="#f0f0f0", font=("Courier", 10))
        self.etiqueta_hash_prueba.pack(anchor="w")

    def cargar_imagen_referencia(self):
        ruta_archivo = filedialog.askopenfilename(
            title="Seleccionar Imagen de Referencia",
            filetypes=[("Archivos de imagen", "*.png *.jpg *.jpeg *.bmp *.gif")]
        )
        if ruta_archivo:
            self.ruta_imagen_referencia = ruta_archivo
            self.mostrar_imagen(ruta_archivo, self.etiqueta_imagen_ref)
            self.hash_referencia = self.calcular_hash_imagen(ruta_archivo)
            self.etiqueta_hash_ref.config(text=f"Hash de Referencia: {self.hash_referencia[:16]}...")
            self.etiqueta_resultado.config(text="Cargue ambas imágenes y haga clic en 'Verificar Integridad'")

    def cargar_imagen_prueba(self):
        ruta_archivo = filedialog.askopenfilename(
            title="Seleccionar Imagen de Prueba",
            filetypes=[("Archivos de imagen", "*.png *.jpg *.jpeg *.bmp *.gif")]
        )
        if ruta_archivo:
            self.ruta_imagen_prueba = ruta_archivo
            self.mostrar_imagen(ruta_archivo, self.etiqueta_imagen_prueba)
            self.hash_prueba = self.calcular_hash_imagen(ruta_archivo)
            self.etiqueta_hash_prueba.config(text=f"Hash de Prueba: {self.hash_prueba[:16]}...")
            self.etiqueta_resultado.config(text="Cargue ambas imágenes y haga clic en 'Verificar Integridad'")

    def mostrar_imagen(self, ruta_archivo, etiqueta):
        try:
            imagen = Image.open(ruta_archivo)
            ancho_etiqueta = etiqueta.winfo_width() or 300
            alto_etiqueta = etiqueta.winfo_height() or 200
            ancho_img, alto_img = imagen.size
            ratio = min(ancho_etiqueta / ancho_img, alto_etiqueta / alto_img)
            nuevo_ancho = int(ancho_img * ratio)
            nuevo_alto = int(alto_img * ratio)
            imagen = imagen.resize((nuevo_ancho, nuevo_alto), Image.LANCZOS)
            foto = ImageTk.PhotoImage(imagen)
            etiqueta.config(image=foto)
            etiqueta.image = foto
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar la imagen: {str(e)}")

    def calcular_hash_imagen(self, ruta_archivo):
        try:
            with Image.open(ruta_archivo) as img:
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                buffer_bytes_img = io.BytesIO()
                img.save(buffer_bytes_img, format='PNG')
                bytes_img = buffer_bytes_img.getvalue()
                objeto_hash = hashlib.sha256(bytes_img)
                return objeto_hash.hexdigest()
        except Exception as e:
            messagebox.showerror("Error", f"Error al calcular el hash: {str(e)}")
            return None

    def comparar_similitud_visual(self, ruta1, ruta2):
        try:
            img1 = Image.open(ruta1).convert('L')
            img2 = Image.open(ruta2).convert('L')
            img2 = img2.resize(img1.size, Image.LANCZOS)
            arr1 = np.array(img1)
            arr2 = np.array(img2)
            score, _ = ssim(arr1, arr2, full=True)
            return score
        except Exception as e:
            messagebox.showerror("Error", f"Error al comparar imágenes: {str(e)}")
            return None

    def verificar_integridad(self):
        if not self.ruta_imagen_referencia or not self.ruta_imagen_prueba:
            messagebox.showwarning("Advertencia", "Por favor, cargue ambas imágenes primero.")
            return

        if self.hash_referencia == self.hash_prueba:
            self.etiqueta_resultado.config(
                text="✅ IMÁGENES IDÉNTICAS (hashes coinciden)",
                fg="green",
                font=("Arial", 14, "bold")
            )
        else:
            score = self.comparar_similitud_visual(self.ruta_imagen_referencia, self.ruta_imagen_prueba)
            if score is not None:
                if score > 0.95:
                    texto = f"🟡 Muy similares visualmente (SSIM={score:.2f})"
                    color = "orange"
                elif score > 0.75:
                    texto = f"🟠 Similares, pero con diferencias (SSIM={score:.2f})"
                    color = "darkorange"
                else:
                    texto = f"❌ Diferentes visualmente (SSIM={score:.2f})"
                    color = "red"

                self.etiqueta_resultado.config(
                    text=texto,
                    fg=color,
                    font=("Arial", 14, "bold")
                )

if __name__ == "__main__":
    app = VerificadorIntegridadImagenes()
    app.mainloop()
