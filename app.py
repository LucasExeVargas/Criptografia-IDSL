from comparacion import ComparadorImagenes

# Inicializar el comparador con la imagen original, que se usará como punto de comparación
comparator = ComparadorImagenes(r"c:\Users\User\Pictures\asl3.jpg")

# Comparar la imagen original con dos imágenes (test1.png y test2.png) usando pHash
pHash_results = comparator.compare_pHash([r"c:\Users\User\Pictures\asl4.jpg", r"c:\Users\User\Pictures\asl3.jpg"])
print("Resultados con pHash:", pHash_results)

# Comparar la imagen original con dos imágenes (test1.png y test2.png) usando ORB, con guardado de los resultados
ORB_results = comparator.compare_ORB([r"c:\Users\User\Pictures\asl4.jpg", r"c:\Users\User\Pictures\asl3.jpg"], saveOutput=True)
print("Resultados con ORB:", ORB_results)


histogramas_results = comparator.compare_histogramas([r"c:\Users\User\Pictures\Granjero 2pocoeditado.png", r"c:\Users\User\Pictures\Granjero 2 editado2.png"])
print("Resultados con histograma: ", histogramas_results)