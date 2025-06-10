from comparacion import ComparadorImagenes

# Inicializar el comparador con la imagen original, que se usará como punto de comparación
comparator = ComparadorImagenes("/home/lucas/proyecto/web/Criptografia-IDSL/original.webp")

# Comparar la imagen original con dos imágenes (test1.png y test2.png) usando pHash
pHash_results = comparator.compare_pHash(["/home/lucas/proyecto/web/Criptografia-IDSL/test1.png", "/home/lucas/proyecto/web/Criptografia-IDSL/mujeres.webp"])
print("Resultados con pHash:", pHash_results)

# Comparar la imagen original con dos imágenes (test1.png y test2.png) usando ORB, con guardado de los resultados
<<<<<<< HEAD
ORB_results = comparator.compare_ORB(["test1.png", "test2.png"], saveOutput=True)
=======
ORB_results = comparator.compare_ORB(["/home/lucas/proyecto/web/Criptografia-IDSL/test1.png", "/home/lucas/proyecto/web/Criptografia-IDSL/mujeres.webp"], saveOutput=True)
>>>>>>> 50e46d1 (interfaz)
print("Resultados con ORB:", ORB_results)