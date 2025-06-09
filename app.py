from comparacion import ComparadorImagenes

# Inicializar el comparador con la imagen original, que se usará como punto de comparación
comparator = ComparadorImagenes("original.png")

# Comparar la imagen original con dos imágenes (test1.png y test2.png) usando pHash
pHash_results = comparator.compare_pHash(["test1.png", "test2.png"])
print("Resultados con pHash:", pHash_results)

# Comparar la imagen original con dos imágenes (test1.png y test2.png) usando ORB, con guardado de los resultados
ORB_results = comparator.compare_ORB(["test1.png", "test2.png"], saveOutput=True)
print("Resultados con ORB:", ORB_results)