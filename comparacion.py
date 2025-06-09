import cv2
import imagehash
from PIL import Image
from typing import List, Dict, Union

class ComparadorImagenes:
    """
    Clase para comparar imágenes usando pHash y ORB.
    Permite comparar una imagen original con múltiples imágenes de prueba.
    """
    
    def __init__(self, pathOriginal: str):
        self.pathOriginal = pathOriginal

    def compare_pHash(self, pathsComparaciones: List[str], limite: int = 10) -> List[Dict[str, Union[str, int, bool]]]:
        """
        Compara imágenes usando pHash (Perceptual Hashing).
        
        El algoritmo pHash, o perceptual hash, es una técnica diseñada para obtener una "firma digital" que representa la apariencia visual de una imagen. Su funcionamiento se basa en transformar la imagen para extraer sus componentes más significativos. Para ello, se reduce la imagen a un tamaño pequeño y la convierte a escala de grises. Luego, aplica una Transformada Discreta del Coseno (DCT), que permite capturar las frecuencias principales de la imagen. A partir de los coeficientes más importantes de esta transformación, se calcula una mediana y genera un hash binario comparando cada valor con esa mediana. El resultado es una cadena binaria o hexadecimal que puede ser utilizada para comparar imágenes mediante una métrica como la distancia de Hamming (el número de posiciones en las que dos cadenas de igual longitud tienen símbolos diferentes). De esta forma, pHash permite detectar imágenes similares incluso si han sido redimensionadas, comprimidas o ligeramente modificadas.
        
        :param pathsComparaciones: Lista de rutas de imágenes a comparar con la imagen original.
        :param limite: Límite de diferencia para considerar dos imágenes similares.
        :return: Lista de diccionarios con resultados de comparación.
        Cada diccionario contiene:
            - "imagen": Ruta de la imagen comparada.
            - "diferencia": Diferencia de pHash entre la imagen original y la comparada.
            - "son_similares": Booleano indicando si la imagen es similar a la original.
        """
        original = Image.open(self.pathOriginal)
        pHashOriginal = imagehash.phash(original)
        resultados = []

        for path in pathsComparaciones:
            imagenTest = Image.open(path)
            diferenciapHash = pHashOriginal - imagehash.phash(imagenTest)
            print(f"HASH DE LA IMAGEN ORIGINAL: {pHashOriginal}")
            print(f"HASH DE LA IMAGEN COMPARADA: {imagehash.phash(imagenTest)}")
            resultados.append({
                "imagen": path,
                "diferencia": int(diferenciapHash),
                "son_similares": diferenciapHash <= limite
            })
        return resultados

    def compare_ORB(self, pathsComparaciones: List[str], limiteCaracteristicas: int = 50000, saveOutput: bool = False, dirOutput: str = "resultados_ORB") -> List[Dict[str, Union[int, str]]]:
        """
        Compara imágenes usando ORB (Oriented FAST and Rotated BRIEF).
        
        El algoritmo ORB (Oriented FAST and Rotated BRIEF) trabaja con el objetivo es identificar puntos clave dentro de una imagen (regiones distintivas que pueden ser comparadas con otras imágenes para encontrar correspondencias). ORB comienza detectando estos puntos clave mediante el algoritmo FAST (un método extremadamente rápido que consiste en analizar un ixel y compararlo con los pixeles ubicados en un círculo a su alrededor), y luego les asigna una orientación para lograr invariancia a la rotación. Posteriormente, describe estos puntos usando una versión modificada de BRIEF (un descriptor binario eficiente y robusto). El resultado de ORB es un conjunto de puntos clave junto con descriptores binarios que pueden ser comparados entre imágenes para determinar coincidencias locales. En nuestro caso, retornamos imágenes donde se pueden ver las similitudes entre la imagen original y las imágenes comparadas, además de un conteo de coincidencias.
        
        :param pathsComparaciones: Lista de rutas de imágenes a comparar con la imagen original.
        :param limiteCaracteristicas: Número máximo de características a detectar.
        :param saveOutput: Si es True, guarda las imágenes con las coincidencias visualizadas.
        :param dirOutput: Directorio donde se guardarán las imágenes de salida si saveOutput es True.
        :return: Lista de diccionarios con resultados de comparación.
        Cada diccionario contiene:
            - "imagen": Ruta de la imagen comparada.
            - "coincidencias": Número de coincidencias encontradas.
            - "pathOutput": Ruta del archivo guardado si saveOutput es True, de lo contrario None.
        """
        imagenOriginal = cv2.imread(self.pathOriginal, cv2.IMREAD_GRAYSCALE)
        orb = cv2.ORB_create(limiteCaracteristicas)
        kp1, des1 = orb.detectAndCompute(imagenOriginal, None)
        results = []

        if saveOutput:
            import os
            os.makedirs(dirOutput, exist_ok=True)

        for path in pathsComparaciones:
            imagenTest = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
            kp2, des2 = orb.detectAndCompute(imagenTest, None)

            # Analizamos las coincidencias entre las características detectadas
            bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
            coincidencias = bf.match(des1, des2)
            coincidencias = sorted(coincidencias, key=lambda x: x.distance)

            # Guardamos la imagen con las coincidencias dibujadas si saveOutput es True
            pathOutput = None
            if saveOutput:
                pathOutput = f"{dirOutput}/diferencia_orb_{os.path.basename(path)}"
                imagenConComparaciones = cv2.drawMatches(
                    imagenOriginal, kp1, imagenTest, kp2, coincidencias[:limiteCaracteristicas], None,
                    flags=cv2.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS
                )
                cv2.imwrite(pathOutput, imagenConComparaciones)

            results.append({
                "imagen": path,
                "coincidencias": len(coincidencias),
                "pathOutput": pathOutput
            })
        return results