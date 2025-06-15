import os
from datetime import datetime 
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
            - "fecha_modificacion": Indica la ultima vez que se modifico el archivo
        """
        original = Image.open(self.pathOriginal)
        pHashOriginal = imagehash.phash(original)
        resultados = []

        for path in pathsComparaciones:
            imagenTest = Image.open(path)
            diferenciapHash = pHashOriginal - imagehash.phash(imagenTest)
            print(f"HASH DE LA IMAGEN ORIGINAL: {pHashOriginal}")
            print(f"HASH DE LA IMAGEN COMPARADA: {imagehash.phash(imagenTest)}")
            timeStamp = os.path.getmtime(path)
            fechaMod = datetime.fromtimestamp(timeStamp).strftime("%Y-%m-%d %H:%M:%S")
            resultados.append({
                "imagen": path,
                "diferencia": int(diferenciapHash),
                "hash_original": str(pHashOriginal),
                "hash_comparada": str(imagehash.phash(imagenTest)),
                "fecha_modificacion": fechaMod,
                "son_similares": diferenciapHash <= limite
            })
        return resultados

    def compare_ORB(self, pathsComparaciones: List[str], limiteCaracteristicas: int = 10000, saveOutput: bool = False, dirOutput: str = "resultados_ORB") -> List[Dict[str, Union[int, str]]]:
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
            - "total_keypoints_original": Total de puntos clave en la imagen original.
            - "total_keypoints_comparada": Total de puntos clave en la imagen comparada.
            - "porcentaje_coincidencias": Porcentaje de coincidencias respecto al total de puntos clave.
            - "fecha_modificacion": Indica la ultima vez que se modifico el archivo
            - "pathOutput": Ruta donde se guardó la imagen con las coincidencias (si saveOutput es True).
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
            #Obtenemos los datos de la ultima modificacion
            timeStamp = os.path.getmtime(path)
            fechaMod = datetime.fromtimestamp(timeStamp).strftime("%Y-%m-%d %H:%M:%S")
            coincidencias_total = len(coincidencias)
            # porcentaje_coincidencias = round((coincidencias_total / limiteCaracteristicas) * 100, 2)
            total_kp1 = len(kp1)
            total_kp2 = len(kp2)
            total_kp = min(total_kp1, total_kp2)
            porcentaje_coincidencias = round((coincidencias_total / total_kp) * 100, 2) if total_kp > 0 else 0

            results.append({
                "imagen": path,
                "coincidencias": coincidencias_total,
                "total_keypoints_original": total_kp1,
                "total_keypoints_comparada": total_kp2,
                "porcentaje_coincidencias": f"{porcentaje_coincidencias}%",
                "fecha_modificacion": fechaMod,
                "pathOutput": pathOutput
            })
        return results
    
    #Compara el color de las imagenes, obtiene el histograma de cada imagen donde ve cuántos píxeles hay de cada color o intensidad
    def compare_histogramas(self, pathsComparaciones: List[str], metodo=cv2.HISTCMP_CORREL, umbral: float = 0.8) -> List[Dict[str, Union[str, float, bool]]]:
        """"
        Compara imágenes usando histogramas de color (en espacio HSV).
        :param pathsComparaciones: Lista de rutas de imágenes a comparar con la imagen original.
        :param metodo: Método de comparación (ej: cv2.HISTCMP_CORREL, cv2.HISTCMP_CHISQR, etc.)
        :param umbral: Valor mínimo para considerar que las imágenes son similares.
        :return: Lista de diccionarios con los resultados.
        Cada diccionario contiene:
            - "imagen": Ruta de la imagen comparada.
            - "similitud": Valor de similitud entre 0 y 1 (1.0: identicas, 0.8-0.99: muy similiares, 0.5-0.9: parecidas, < 0.5: distintas).
            - "son_similares": Booleano indicando si la imagen es similar a la original según el umbral.
        """
        resultados = []

        # Cargar y convertir imagen original
        imgOriginal = cv2.imread(self.pathOriginal)
        hsvOriginal = cv2.cvtColor(imgOriginal, cv2.COLOR_BGR2HSV)
        histOriginal = cv2.calcHist([hsvOriginal], [0, 1], None, [50, 60], [0, 180, 0, 256])
        cv2.normalize(histOriginal, histOriginal, alpha=0, beta=1, norm_type=cv2.NORM_MINMAX)

        for path in pathsComparaciones:
            img = cv2.imread(path)
            hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
            hist = cv2.calcHist([hsv], [0, 1], None, [50, 60], [0, 180, 0, 256])
            cv2.normalize(hist, hist, alpha=0, beta=1, norm_type=cv2.NORM_MINMAX)

            similitud = cv2.compareHist(histOriginal, hist, metodo)

            es_similar = False
            if metodo == cv2.HISTCMP_CORREL:
                es_similar = similitud >= umbral
            elif metodo in [cv2.HISTCMP_CHISQR, cv2.HISTCMP_BHATTACHARYYA]:
                es_similar = similitud <= umbral
            elif metodo == cv2.HISTCMP_INTERSECT:
                es_similar = similitud >= umbral  # A mayor intersección, más parecido

            resultados.append({
                "imagen": path,
                "similitud": round(similitud, 4), #1.0: identicas, 0.8-0.99: muy similiares, 0.5-0.9: parecidas, < 0.5: distintas
                "son_similares": es_similar  
            })

        return resultados