import matplotlib.pyplot as plt
from skimage import io, img_as_ubyte, morphology, measure, color
import numpy as np
import cv2
from glob import glob
import os
import interfaz as interfaz
from celda import Celda
from tratamiento import Tratamiento
from tkinter import simpledialog, filedialog, messagebox
import tifffile
import csv
import json
from sklearn.metrics import r2_score

def obtener_imagen_celda(img, i, j, alto_celda, ancho_celda): # fila, columna (empieza en 1)
    """
    Obtiene una sub-imagen de la imagen principal según las coordenadas (i, j) en la grilla.
    
    :param img: La imagen principal de la que se quiere extraer una celda/sub-imagen.
    :param i: Coordenada de fila en la grilla.
    :param j: Coordenada de columna en la grilla.
    :param alto_celda: Altura de una celda en píxeles.
    :param ancho_celda: Ancho de una celda en píxeles.
    :return: new_img: La sub-imagen extraída.
    """
    if len(img.shape) == 3:
        new_img = img[int(alto_celda*(i-1)):int(alto_celda*i), int(ancho_celda*(j-1)):int(ancho_celda*j), :]
    elif len(img.shape) == 2:
        new_img = img[int(alto_celda*(i-1)):int(alto_celda*i), int(ancho_celda*(j-1)):int(ancho_celda*j)]
    #plt.imshow(new_img)
    #plt.show()        
    return new_img

# Función que detecta los círculos en la imagen. Se deben tunear param1 y param2 para reducir FN y/o FP. 
# Así mismo, minRadius y maxRadius se tunean dependiendo del tamaño de la grilla y muestras utilizadas. 
#def obtener_circulos(imagen, param1=100, param2=8, minRadius=10, maxRadius=16, plotear=False):
#def obtener_circulos(imagen, param1=100, param2=8, minRadius=5, maxRadius=8, plotear=False): #originalmente
def obtener_circulos(imagen, tipo, threshold_binarization, param1=100, param2=8, minRadius=5, maxRadius=8, plotear=False):    
    """
    Detecta un círculo usando segmentación por umbral y centroides (Momentos), y luego se aplica HoughCircles.
    Sustituye a HoughCircles para mayor robustez.
    
    :param imagen: La imagen en la que se quiere detectar los círculos.
    :param param1: Parámetro 1 para la detección de círculos.
    :param param2: Parámetro 2 para la detección de círculos.
    :param minRadius: Radio mínimo para los círculos detectados.
    :param maxRadius: Radio máximo para los círculos detectados.
    :param plotear: Booleano para decidir si mostrar o no la imagen con círculos detectados.
    :return: circulos[0,0]: Retorna las coordenadas del círculo detectado.
    """
    
    # se copia para no alterar la imagen original
    #imagen = imagen.copy()
    #imagen = img_as_ubyte(imagen)
    # se copia para no alterar la imagen original

    process= imagen.copy()
    process = cv2.medianBlur(process, 9) #preprocesamiento, eliminación ruido puntual

    #process=cv2.bilateralFilter(process, d=9, sigmaColor=75, sigmaSpace=75)#preprocesamiento
    #circulos = cv2.HoughCircles(imagen, cv2.HOUGH_GRADIENT, 1, 20, 
                       #         param1=param1, param2=param2, minRadius=minRadius, maxRadius=maxRadius)
    # CLAHE (Contrast Limited Adaptive Histogram Equalization)
    # clipLimit: cuánto contraste quieres añadir (2.0 a 4.0 es normal)
    # tileGridSize: tamaño del bloque de análisis
    #clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    #process = clahe.apply(process)#image realzada
    #kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3,3))
    # El gradiente es la diferencia entre la dilatación y la erosión
    #process = cv2.morphologyEx(process, cv2.MORPH_GRADIENT, kernel)# imagen bordes
    
    # 3. Binarización Manual, para este test funcionó 16
    _, thresh = cv2.threshold(process, threshold_binarization, 255, cv2.THRESH_BINARY)

    #limpieza morphologica, eliminación de objetos pequeños

    thresh_clean = morphology.remove_small_objects(thresh.astype(bool), min_size=10)

    #circulos = cv2.HoughCircles(process, cv2.HOUGH_GRADIENT, 1, 20, 
    #                            param1=param1, param2=param2, minRadius=minRadius, maxRadius=maxRadius)
    # 5. Etiquetado y Propiedades
    labels = measure.label(thresh_clean)
    props = measure.regionprops(labels)
    #print('props', props[0].eccentricity, props[0].solidity, props[0].equivalent_diameter)
    
    #print(circulos)
    encontrados = [] #almacenar los posibles circulos
    
    for p in props:
        y0, x0 = p.centroid
        radio_eq = np.sqrt(p.area / np.pi)
        
        # Filtro de tamaño
        if minRadius <= radio_eq <= maxRadius:
            # Guardamos en formato (x, y, r) para compatibilidad
            encontrados.append([int(x0), int(y0), int(radio_eq)])

    # Si se detectan circulos..
    if len(encontrados) == 0 and tipo=='Control Negativo':
        print("Warning: No aparecen circulos en el control negativo, se calculará la intensidad promedio del fondo")
        x,y=thresh_clean.shape
        x=x//2
        y=y//2#saca centro de la imagen total
        if x<y:#condicion para elegir r sin que salga error, basicamente elgir radio que no se salga del tamaño de la imagen
            r=x
        else:
            r=y
        encontrados.append([int(x), int(y), int(r)])
    if len(encontrados) == 0 and tipo!='Control Negativo':
        #print(tipo)#temporal
        raise Exception(f'No se detectaron círculos con el umbral actual. Verifique si fluorescen en las imágenes y/o ajuste el umbral')
    
    if len(encontrados) > 1:
        # Si detecta varios, se puede elegir el más cercano al centro o el más grande
        # Aquí lanzamos excepción, pero no deberia pasar esto dado a que ahora es basado en centroides
        raise Exception(f'Se detectaron {len(encontrados)} objetos. Ajuste el umbral o el tamaño de elminación de artefactos.')

    # El círculo detectado
    circulo_final = encontrados[0]
    #print(circulo_final, type(circulo_final), ';', encontrados)#temporal

    if plotear:
        #temp_img = cv2.cvtColor(process, cv2.COLOR_GRAY2BGR)
        #cv2.circle(temp_img, (circulo_final[0], circulo_final[1]), circulo_final[2], (0, 0, 255), 1)
        #plt.imshow(temp_img)
        #plt.title(f"Centroide detectado: {circulo_final[:2]}")
        #plt.show()
        
        cv2.circle(process, (circulo_final[0], circulo_final[1]), circulo_final[2], (0, 0, 255), 1)
        plt.imshow(process)
        plt.title(f"Centroide detectado: {circulo_final[:2]}")
        plt.show()

    # Retornamos [x, y, r]
    return circulo_final
    #termina modificacion

def plot(img):
    """
    Muestra una imagen dada.
    
    :param img: Imagen a mostrar.
    """
    plt.imshow(img)
    plt.axis('off') 
    plt.show()

def calcular_intensidad(img, circulo, metodo = None):
    """
    Calcula la intensidad de un círculo en una imagen.
    
    :param img: Imagen que contiene el círculo.
    :param circulo: Coordenadas del círculo en la imagen.
    :param metodo: Método a usar para calcular la intensidad (media, maximo, minimo, mediana).
    :return: intensidad: Valor de la intensidad calculada.
    """
        
    i, j, r = circulo
    if i-r<0:
        r=r-(i-r)
    elif j-r<0:
        r=r-(j-r)
    # se toma la ventana de interes (el cuadrado que enmarca el circulo detectado):
    #print('j-r j+r i-r i+r',max(0,j-r), j-r, j+r, max(0,i-r), i-r, i+r, 'img shape', img.shape)
    if len(img.shape)==3:
        #ventana = img[max(0,j-r):max(img.shape[0],j+r), max(0,i-r):max(img.shape[1],i+r), 1] # solo se toman las intensidades del canal G (verde)
        ventana = img[max(0,j-r):j+r, max(0,i-r):i+r, 1]
    if len(img.shape)==2:
        #ventana = img[max(0,j-r):max(img.shape[0],j+r), max(0,i-r):max(img.shape[1],i+r)]
        ventana = img[max(0,j-r):j+r, max(0,i-r):i+r]
    intensidades_ordenadas = np.sort(ventana.flatten())
    intensidad = 0  
    
    if metodo == 'media':    
        intensidad = np.mean(intensidades_ordenadas)
    elif metodo == 'maximo':
        intensidad = intensidades_ordenadas[-1]
    elif metodo == 'minimo':
        intensidad = intensidades_ordenadas[0]
    elif metodo == 'mediana':
        intensidad = intensidades_ordenadas[len(intensidades_ordenadas)//2]
    else:
        # se toma el promedio de la mitad mayor de las intensidades ordenadas
        #print('intensidades', intensidades_ordenadas)
        intensidad = np.mean(intensidades_ordenadas[len(intensidades_ordenadas)//2:])

    return intensidad

def graficar_intensidad_tiempo_tratamientos(tratamientos, intervalo_tiempo=1.0, porcentaje=None):
    """
    Grafica la intensidad de cada celda en función del tiempo.
    
    :param celdas: Lista de celdas con sus respectivas intensidades a lo largo del tiempo.
    :param numero_tratamientos: Número de tratamientos.
    """
    
    numero_tratamientos = len(tratamientos)

    if numero_tratamientos not in [1, 2]:
        print("Número de tratamientos no soportado.")
        return
    
    for tratamiento in tratamientos:
        plt.figure(figsize=(12, 8))
        
        for celda in tratamiento.muestras:
            intensidades = celda.intensidades
            eje_x= np.arange(len(intensidades))*intervalo_tiempo #Scale according to the interval time

            plt.plot(eje_x,intensidades, label=f"Celda {celda.coordenada_alfanumerica}, {celda.tipo}, {celda.estado}")

        #for celda in [tratamiento.control_positivo, tratamiento.control_negativo]:
        #    if celda is not None:
        #        intensidades = celda.intensidades
        #        plt.plot(intensidades, label=f"Celda {celda.coordenada_alfanumerica}, {celda.tipo}")

        for celda in tratamiento.controles_positivos:
            if celda is not None:
                intensidades = celda.intensidades
                eje_x= np.arange(len(intensidades))*intervalo_tiempo
                plt.plot(eje_x,intensidades, label=f"Celda {celda.coordenada_alfanumerica}, {celda.tipo}")
        for celda in tratamiento.controles_negativos:
            if celda is not None:
                intensidades = celda.intensidades
                eje_x= np.arange(len(intensidades))*intervalo_tiempo
                plt.plot(eje_x, intensidades, label=f"Celda {celda.coordenada_alfanumerica}, {celda.tipo}")


        threshold = tratamiento.calcular_threshold()
        if threshold is not None:
            plt.axhline(threshold, color='r', linestyle='--', label='Threshold')

        #plt.title(f"Resultados {tratamiento.nombre}", fontsize=16)
        plt.title(f"Resultados DiDePT", fontsize=16)
        plt.xlabel("Tiempo (Minutos)", fontsize=14)
        plt.ylabel("Intensidad", fontsize=14)
        plt.xticks(rotation=0, fontsize=15) 
        plt.yticks(fontsize=15)
        plt.legend(loc="best")
        plt.grid(True)

        plt.savefig(f"resultados_{tratamiento.nombre}.png")
        plt.show()

def graficar_intensidad_tiempo_tratamiento(tratamiento, porcentaje=None):
    """
    Grafica la intensidad de cada celda en función del tiempo.
    
    :param celdas: Lista de celdas con sus respectivas intensidades a lo largo del tiempo.
    :param numero_tratamientos: Número de tratamientos.
    """

    # Si se especifica un porcentaje, se vuelve a concluír el tratamiento con el nuevo threshold
    if porcentaje is not None:
        threshold = tratamiento.concluir_tratamiento(porcentaje)
    else:
        threshold = tratamiento.threshold

    plt.figure(figsize=(12, 8))
    
    for celda in tratamiento.muestras:
        intensidades = celda.intensidades
        plt.plot(intensidades, label=f"Celda {celda.coordenada}, {celda.tipo}")

    for celda in tratamiento.obtener_controles():
        intensidades = celda.intensidades
        plt.plot(intensidades, label=f"Celda {celda.coordenada}, {celda.tipo}")

    if threshold is not None:
        plt.axhline(threshold, color='r', linestyle='--', label='Threshold')

    #plt.title(f"Resultados {tratamiento.nombre}")
    plt.title(f"Resultados DiDePT")
    plt.xlabel("Tiempo")
    plt.ylabel("Intensidad")
    plt.legend(loc="best")
    plt.grid(True)
    plt.show()

##Inicia codigo de ajuste sigmoidal
from scipy.optimize import curve_fit

# --- Definición de función sigmoidal ---
def sigmoid(x, L, x0, k, b):
    """
    Función logística general para modelar crecimiento o intensificación.
    L: amplitud
    x0: punto de inflexión
    k: pendiente (empinamiento)
    b: desplazamiento vertical
    """
    return L / (1 + np.exp(-k * (x - x0))) + b


# --- Ajuste sigmoidal y cálculo de pendiente máxima ---
def ajustar_sigmoide(x, y, intervalo_tiempo=1.0):
    """
    Ajusta una sigmoide a los datos (x, y) y calcula la pendiente máxima (en x0).
    
    Devuelve:
      popt: parámetros [L, x0, k, b]
      pendiente_max: (L * k) / 4
      y_fit: curva ajustada
    """
    #print('entra')
    # Estimaciones iniciales razonables
    L0 = np.max(y) - np.min(y)
    x0_0 = x[np.argmax(np.gradient(y))] if np.any(np.gradient(y)) else np.median(x)
    k0 = 1.0
    b0 = np.min(y)
    p0 = [L0, x0_0, k0, b0]

    try:
        popt, _ = curve_fit(sigmoid, x, y, p0=p0, maxfev=10000)
        L, x0, k, b = popt
        pendiente_max = (L * k) / 4
        y_fit = sigmoid(x, *popt)
        r_squared = r2_score(y, y_fit)
        print('r', r_squared)
        ##usar otro medidor de pendientes
        #y_diff=np.diff(y_fit)
        #x_diff=np.diff(x)
        #pendientes=y_diff/x_diff
        #pendiente_max=np.max(pendientes)

        x = np.arange(len(y_fit))*intervalo_tiempo
        pendiente_y = np.gradient(y_fit, x[1] - x[0])
        pendiente_max=np.max(pendiente_y)

        return popt, pendiente_max, y_fit, k
        
    except RuntimeError:
        # Ajuste fallido
        return None, None, None, None
    

# --- Gráfica del tratamiento con ajuste sigmoidal ---
def graficar_intensidad_tiempo_tratamiento(tratamiento, intervalo_tiempo=1.0, porcentaje=None):
    """
    Grafica la intensidad de cada celda en función del tiempo con su ajuste sigmoidal.
    También muestra la pendiente máxima (derivada en el punto de inflexión).
    """
    if porcentaje is not None:
        threshold = tratamiento.concluir_tratamiento(porcentaje)
    else:
        threshold = tratamiento.threshold

    plt.figure(figsize=(12, 8))
    pendientes = []  # [(celda, pendiente_max)]
    b_list=[]
    for celda in tratamiento.muestras:
        intensidades = np.array(celda.intensidades)
        x = np.arange(len(intensidades))*intervalo_tiempo# To scale X in funcion of time interval
        linea, = plt.plot(x, intensidades, 'o', alpha=0.5, label=f"{celda.coordenada}, {celda.tipo}")
        color_asig = linea.get_color() # Extraemos el color de la línea
        popt, pendiente_max, y_fit, b = ajustar_sigmoide(x, intensidades)
        if y_fit is not None:
            plt.plot(x, y_fit, '--', linewidth=2, color=color_asig) # Now the slope is in units of intensity/actual minute
            pendientes.append((celda.coordenada, pendiente_max, b))
            b_list.append((celda.coordenada, b))



    for celda in tratamiento.obtener_controles():
        intensidades = np.array(celda.intensidades)
        x = np.arange(len(intensidades))*intervalo_tiempo # To scale X in funcion of time interval
        linea, = plt.plot(x, intensidades, 'o', label=f"{celda.coordenada}, {celda.tipo}", alpha=0.5)
        color_asig= linea.get_color()
        popt, pendiente_max, y_fit, b = ajustar_sigmoide(x, intensidades)
        #print(len(y_fit), celda.coordenada)
        if y_fit is not None:
            plt.plot(x, y_fit, '--', linewidth=2, color=color_asig)
            pendientes.append((celda.coordenada, pendiente_max, b))
            b_list.append((celda.coordenada, b))

    if threshold is not None:
        plt.axhline(threshold, color='r', linestyle='--', label='Threshold')

    #plt.title(f"Resultados Ajuste Sigmoidal {tratamiento.nombre}")
    plt.title(f"Resultados Ajuste Sigmoidal", fontsize=16)
    plt.xlabel("Tiempo (min)", fontsize=14)
    plt.ylabel("Intensidad", fontsize=14)
    plt.xticks(rotation=0, fontsize=17) 
    plt.yticks(fontsize=17)
    plt.legend(loc="best")
    plt.grid(True)
    plt.show()

    print(f"\nPendientes máximas del tratamiento {tratamiento.nombre}:")
    for coord, p, b in pendientes:
        print(f"  Celda {coord}: pendiente máxima = {p:.4f}, factor exponencial = {b:.4f}")
    print(f"\nResultados del tratamiento {tratamiento.nombre}:")
        
    return pendientes, b_list

def graficar_pendientes_tiempo_tratamiento(tratamiento, intervalo_tiempo=1.0, porcentaje=None):
    """
    Grafica la intensidad de cada celda en función del tiempo con su ajuste sigmoidal.
    También muestra la pendiente máxima (derivada en el punto de inflexión).
    """
    #if porcentaje is not None:
    #    threshold = tratamiento.concluir_tratamiento(porcentaje)
    #else:
    #    threshold = tratamiento.threshold

    plt.figure(figsize=(12, 8))
    #pendientes = []  # [(celda, pendiente_max)]
    #b_list=[]
    for celda in tratamiento.muestras:
        intensidades = np.array(celda.intensidades)
        x = np.arange(len(intensidades))*intervalo_tiempo
        #plt.plot(x, intensidades, 'o', alpha=0.5, label=f"{celda.coordenada}, {celda.tipo}")
        popt, pendiente_max, y_fit, b = ajustar_sigmoide(x, intensidades)
        #pendientes.append(pendiente_max)
        #b_list.append(b)
        if y_fit is not None:
            pendiente_y = np.gradient(y_fit, x[1] - x[0])
            plt.plot(x, pendiente_y, '--', label=f"{celda.coordenada}, {celda.tipo}", linewidth=2)
            

    for celda in tratamiento.obtener_controles():
        intensidades = np.array(celda.intensidades)
        x = np.arange(len(intensidades))*intervalo_tiempo
        #plt.plot(x, intensidades, 'o', alpha=0.5, label=f"{celda.coordenada}, {celda.tipo}")
        popt, pendiente_max, y_fit, b = ajustar_sigmoide(x, intensidades)
        #pendientes.append(pendiente_max)
        #b_list.append(b)
        if y_fit is not None:
            pendiente_y = np.gradient(y_fit, x[1] - x[0])
            plt.plot(x, pendiente_y, '--', label=f"{celda.coordenada}, {celda.tipo}", linewidth=2)

    #if threshold is not None:
     #   plt.axhline(threshold, color='r', linestyle='--', label='Threshold')

    #plt.title(f"Resultados Pendientes {tratamiento.nombre}")
    plt.title(f"Resultados Pendientes", fontsize=16)
    plt.xlabel("Tiempo (min)", fontsize=14)
    plt.ylabel("Intensidad", fontsize=14)
    plt.xticks(rotation=0, fontsize=17) 
    plt.yticks(fontsize=17)
    plt.legend(loc="best")
    plt.grid(True)
    plt.show()

##Termina cambios de ajuste sigmoidal
    ##Empieza cambios gráfica boxplot

    plt.figure(figsize=(12, 8))
    
    valores_pos = []
    valores_neg = []

    # Unificamos el recorrido para asegurar que pase por TODO
    todas_las_celdas = tratamiento.muestras + tratamiento.obtener_controles()

    for celda in todas_las_celdas:
        intensidades = np.array(celda.intensidades)
        x = np.arange(len(intensidades)) * intervalo_tiempo
        
        popt, pendiente_max, y_fit, b = ajustar_sigmoide(x, intensidades)
        
        # --- LOGICA DE CAPTURA ---
        # Si no hubo ajuste (típico en negativos), usamos la pendiente del gradiente crudo
        if pendiente_max is None or np.isnan(pendiente_max):
            derivada_cruda = np.gradient(intensidades, x[1] - x[0])
            valor_a_graficar = np.max(derivada_cruda)
        else:
            valor_a_graficar = pendiente_max

        # --- CLASIFICACIÓN (DEBUG) ---
        tipo_str = str(celda.tipo).lower()
        if "neg" in tipo_str:
            valores_neg.append(valor_a_graficar)
        else:
            valores_pos.append(valor_a_graficar)

        # Graficar la curva de la derivada si existe el ajuste
        if y_fit is not None:
            pendiente_y = np.gradient(y_fit, x[1] - x[0])
            plt.plot(x, pendiente_y, '--', label=f"{celda.coordenada}, {celda.tipo}")

    plt.title(f"Derivadas de Fluorescencia - {tratamiento.nombre}")
    plt.legend(loc="upper left", bbox_to_anchor=(1, 1), fontsize='x-small')
    plt.tight_layout()
    plt.show()

    # --- BOXPLOT ROBUSTO ---
    if len(valores_pos) > 0 or len(valores_neg) > 0:
        plt.figure(figsize=(6, 5))
        
        # Aseguramos que las listas no estén vacías para evitar errores de Matplotlib
        data = [valores_pos if valores_pos else [0], 
                valores_neg if valores_neg else [0]]
        
        #plt.boxplot(data, labels=['Controles Positivos', 'Controles Neg'], patch_artist=True,
        #            boxprops=dict(facecolor='lightgreen', color='green'),
        #            medianprops=dict(color='black'))
        plt.boxplot(data, labels=['Controles Positivos', 'Controles Negativos'], patch_artist=True,
                    boxprops=dict(facecolor='lightgreen', color='green'),
                    medianprops=dict(color='black'),
                    showfliers=False)
        
        
        ### DIBUJAR LOS PUNTOS INDIVIDUALES EN CADA COLUMNA
        # Columna 1 (Controles Positivos) - Posición X = 1
        if valores_pos:
            # Agregamos un pequeño "jitter" (desviación aleatoria en X) para que los puntos no se encimen en una línea recta
            #x_pos = np.random.normal(1, 0.1, size=len(valores_pos))
            x_pos= np.ones(len(valores_pos))*0.9
            plt.scatter(x_pos, valores_pos, color='darkgreen', alpha=0.3, edgecolors='black', label='Muestras Pos')

        # Columna 2 (Controles Neg) - Posición X = 2
        if valores_neg:
            x_neg = np.random.normal(2, 0.1, size=len(valores_neg))
            plt.scatter(x_neg, valores_neg, color='darkred', alpha=0.3, edgecolors='black', label='Muestras Neg')
        
        plt.title("Comparación de Pendientes Máximas")
        plt.ylabel("Pendiente Máxima")
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        plt.show()
        
        print(f"DEBUG: Cantidad Positivos: {len(valores_pos)}, Negativos: {len(valores_neg)}")
        print(f"valor positivo {valores_pos}, valor negativo {valores_neg}, Z-prime: {1 - (3 * (np.std(valores_pos, ddof=1) + np.std(valores_neg, ddof=1)) / abs(np.mean(valores_pos) - np.mean(valores_neg))):.4f}")
        print()

def sort_key_func(item):
    """
    Función auxiliar para ordenar imágenes basadas en su número ascendentemente.
    
    :param item: Nombre del archivo de imagen.
    :return: Orden de la imagen.
    """
    return int(item.split('_')[-1].split('.png')[0])

def cargar_celdas_tratamientos(datos_interfaz):
    """
    Carga las celdas seleccionadas por el usuario.
    
    :param datos_interfaz: Datos de las celdas seleccionadas por el usuario.
    :return: celdas: Lista de celdas seleccionadas.
    """
    
    celdas = []
    tratamientos = []

    for nombre_tratamiento, coordenadas_seleccionadas in datos_interfaz.items():
        nuevo_tratamiento = Tratamiento(nombre_tratamiento)
        for tipo, coordenadas in coordenadas_seleccionadas.items():
            if coordenadas is not None:
                #if type(coordenadas) == list:
                #    for coordenada in coordenadas:
                #        nueva_celda = Celda(tipo, coordenada, nuevo_tratamiento)
                #        celdas.append(nueva_celda)
                #        nuevo_tratamiento.agregar_muestra(nueva_celda)
                # para el control positivo y negativo (solo una celda)
                if type(coordenadas) == list:
                    for coordenada in coordenadas:
                        if tipo ==  'Control Positivo':
                            nueva_celda = Celda(tipo, coordenada, nuevo_tratamiento)
                            celdas.append(nueva_celda)
                            nuevo_tratamiento.agregar_control_positivo(nueva_celda)
                        elif tipo == 'Control Negativo':
                            nueva_celda = Celda(tipo, coordenada, nuevo_tratamiento)
                            celdas.append(nueva_celda)
                            nuevo_tratamiento.agregar_control_negativo(nueva_celda)
                        else:                            
                            nueva_celda = Celda(tipo, coordenada, nuevo_tratamiento)
                            celdas.append(nueva_celda)
                            nuevo_tratamiento.agregar_muestra(nueva_celda)
                elif tipo == 'Control Positivo':
                    nueva_celda = Celda(tipo, coordenadas, nuevo_tratamiento)
                    celdas.append(nueva_celda)
                    nuevo_tratamiento.agregar_control_positivo(nueva_celda)
                elif tipo == 'Control Negativo':
                    nueva_celda = Celda(tipo, coordenadas, nuevo_tratamiento)
                    celdas.append(nueva_celda)
                    nuevo_tratamiento.agregar_control_negativo(nueva_celda)
                
        tratamientos.append(nuevo_tratamiento)

    return celdas, tratamientos

def segmentar_y_encontrar_centroides_multiples(imagen, radio_min_px=4, radio_max_px=8, threshold_binarization=16):
    """
    Segmenta la imagen para encontrar múltiples objetos de alta intensidad verde
    dentro de un rango de radio específico y devuelve la imagen con un marcador
    en el centroide de cada objeto.

    Args:
        imagen (np.array): La imagen a procesar en formato BGR.
        radio_min_px (int): Radio mínimo estimado en píxeles.
        radio_max_px (int): Radio máximo estimado en píxeles.

    Returns:
        np.array: La imagen con los centroides marcados.
        list: Una lista de tuplas (x, y) de los centroides encontrados.
    """
    '''
    # 1. Convertir a espacio de color HSV y crear la máscara
    hsv = cv2.cvtColor(imagen, cv2.COLOR_BGR2HSV)
    verde_bajo = np.array([35, 100, 100])
    verde_alto = np.array([85, 255, 255])
    mascara = cv2.inRange(hsv, verde_bajo, verde_alto)
    
    # 2. Aplicar un filtro para suavizar y eliminar ruido
    mascara_suavizada = cv2.GaussianBlur(mascara, (5, 5), 0)
    
    # 3. Encontrar contornos
    contornos, _ = cv2.findContours(mascara_suavizada, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    imagen_con_objetos = imagen.copy()
    centroides_encontrados = []
    
    # Convertir radios a áreas aproximadas para el filtro
    area_min = np.pi * (radio_min_px**2)
    area_max = np.pi * (radio_max_px**2)
    
    # 4. Iterar sobre todos los contornos y filtrar por área
    for contorno in contornos:
        area_contorno = cv2.contourArea(contorno)
        
        # Filtrar contornos que están dentro del rango de área deseado
        if area_min < area_contorno < area_max:
            # 5. Calcular el centroide del contorno
            M = cv2.moments(contorno)
            if M["m00"] != 0:
                centro_x = int(M["m10"] / M["m00"])
                centro_y = int(M["m01"] / M["m00"])
                
                # 6. Dibujar un círculo rojo en el centroide y agregar a la lista
                cv2.circle(imagen_con_objetos, (centro_x, centro_y), 15, (0, 0, 255), -1)  # Círculo rojo relleno
                centroides_encontrados.append((centro_x, centro_y))'''
    
    imagen_allchannels = imagen.copy()
    imagen_con_objetos=imagen_allchannels.copy()
    imagen_con_objetos = cv2.medianBlur(imagen_con_objetos, 9)
    #img = imagen_con_objetos
    green = imagen_con_objetos[:,:,1]
    #print(green.shape)
    cv2.imshow("green", green)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    # 2. Binarizar (umbral automático Otsu)
    #val_otsu, thresh = cv2.threshold(green, 30, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    #Binarizar manual
    val_otsu, thresh = cv2.threshold(green, threshold_binarization, 255, cv2.THRESH_BINARY)
    
    # --- BLOQUE DE VISUALIZACIÓN ---
    fig, ax = plt.subplots(1, 3, figsize=(15, 5))
    
    # Imagen original (Canal Verde)
    ax[0].imshow(green)
    ax[0].set_title('Filtro Median Blur')
    ax[0].axis('off')

    # Histograma y Umbral
    ax[1].hist(green.ravel(), bins=256, color='green', alpha=0.85)
    ax[1].axvline(val_otsu, color='red', linestyle='--', label=f'Umbral: {val_otsu}')
    ax[1].set_title('Histograma y Umbral')
    ax[1].legend()

    # Resultado de la Binarización
    ax[2].imshow(thresh) #cmap='gray')
    ax[2].set_title('Resultado Umbral Binario Manual')
    ax[2].axis('off')

    plt.tight_layout()
    plt.show() 
    # --- FIN BLOQUE DE VISUALIZACIÓN ---



    # 3. Limpiar objetos pequeños
    thresh_clean = morphology.remove_small_objects(thresh.astype(bool), min_size=3)

    # 4. Etiquetar objetos conexos
    labels = measure.label(thresh_clean)

    # 5. Obtener propiedades
    props = measure.regionprops(labels)

    # 6. Convertir imagen a RGB si es escala de grises (para dibujar color)
    #img_rgb = img.copy()#color.gray2rgb(green) if img.shape[2] == 1 else img.copy()

    centroides_encontrados=[]
    # 7. Dibujar círculos para cada objeto
    '''
    for p in props:
        y, x = p.centroid           # centro del objeto (en coordenadas y,x)
        #print(p.centroid)
        r = np.sqrt(p.area / np.pi) # radio equivalente al área
        if (r>=radio_min_px and r<=radio_max_px):
            #print(p.centroid,r)
            cv2.circle(imagen_con_objetos, (int(x), int(y)), int(r), (0, 0, 255), 2)  # círculo rojo
            cv2.circle(imagen_con_objetos, (int(x), int(y)), 2, (0, 0, 255), -1)  # punto en el centro
            centroides_encontrados.append((int(x),int(y)))
    '''
    for p in props:
        y, x = p.centroid           # centro del objeto (en coordenadas y,x)
        #print(p.centroid)
        r = np.sqrt(p.area / np.pi) # radio equivalente al área
        if (r>=radio_min_px and r<=radio_max_px):
            #print(p.centroid,r)
            cv2.circle(imagen_allchannels, (int(x), int(y)), int(r), (0, 0, 255), 2)  # círculo rojo
            cv2.circle(imagen_allchannels, (int(x), int(y)), 2, (0, 0, 255), -1)  # punto en el centro
            centroides_encontrados.append((int(x),int(y)))

    # 8. Mostrar resultado
    cv2.imshow("Objetos con circulos", imagen_allchannels)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    imagen_con_objetos=green
        
    return imagen_allchannels, centroides_encontrados




def main():
    """
    Función principal que ejecuta el proceso de detección de celdas, recolección de datos y gráfica de intensidades.
    """
    ##Originalmente solo pidiendo intervalo de tiempo
    #t_interval = simpledialog.askfloat("Definir tiempo", "¿Cada cuántos minutos se tomó cada imagen?", minvalue=0.1, initialvalue=1.0)
    #if t_interval is None: t_interval = 1.0 # Valor por defecto si cancela    
    #I need to try to sum/combine the initial image and final image, or maybe let the user decide what time use for the detection

    #PARAMETROS MANUALES (tambien los de la funcion obtener_circulos)
    # se obtienen por medio de experimentacion con el dispositivo final
    
    pixel_x_1, pixel_y_1 = 70, 90 # esquina superior izquierda de la imagen recortada
    pixel_x_2, pixel_y_2 = 570, 428 # esquina inferior derecha de la imagen recortada
    dimension_x, dimension_y = 12, 8 # dimensiones de la grilla de muestras (9 columnas y 5 filas)
    ## Start modifications for .ome.tiff files

    # coords = get_crop_coordinates("ruta/de_tu/imagen.jpg")
    # print("Coordenadas seleccionadas:", coords) # Output: (x1, y1, x2, y2
    name_csv="datos_temperatura"
    t_interval=1
    threshold_transform=16
    threshold_graphs=20
    time_choose_image=-1
    folder_name=os.path.join('photos_treatments_06052026', '06052026_test_in_OneFile')
    try:
        t_interval, threshold_transform, file_name_csv, threshold_graphs, folder_name, time_choose_image=interfaz.initial_settings().values()
        print(f"t {t_interval}, {threshold_transform}, {file_name_csv}, {threshold_graphs}, , {folder_name}, {time_choose_image}")
        print(f"t {type(t_interval)}, {type(threshold_transform)}, {type(file_name_csv)}, {type(threshold_graphs)}, {type(folder_name)}, {type(time_choose_image)}")
        #path_data = os.path.join('data', 'data-img_44', 'img*.png')
        #data = sorted(glob(path_data), key=sort_key_func)[1:]
        #if len(data) == 0:
         #   raise Exception(f"No se encontraron imágenes en el directorio especificado: '{path_data}'." \
          #                  " Revise que el directorio sea correcto y que las imágenes tengan el formato adecuado")
        #end modification
        #path_data_tif = os.path.join('photos_treatments_16122025', '16122025_test_in_OneFile', '16122025_test_in_OneFile_MMStack_Pos0.ome.tif')
        #path_data_tif = os.path.join('photos_treatments_06052026', '06052026_test_in_OneFile', '06052026_0102pm_MMStack_Pos0.ome.tif')
        #path_data_tif = os.path.join('photos_treatments_06052026', '06052026_test_in_OneFile', '*.ome.tif')
        name_csv=file_name_csv
        path_data_tif = os.path.join(folder_name, '*.ome.tif')
        print(path_data_tif, name_csv)
        image_tif = tifffile.imread(path_data_tif)

        #start modification
        coords = interfaz.get_crop_coordinates(image_tif, pixel_x_1, pixel_y_1, pixel_x_2, pixel_y_2)
        pixel_x_1, pixel_y_1, pixel_x_2, pixel_y_2= coords
        print("Coordenadas seleccionadas:", coords, type(coords), type(pixel_x_1), pixel_x_1, pixel_y_1, pixel_x_2, pixel_y_2)

        # Separar por canales para mayor claridad
        # Estructura: [Tiempo, Canal, Y, X, RGB]
        canal_0 = image_tif[:, 0, :, :, :] # Todos los tiempos del Canal 1
        canal_1 = image_tif[:, 1, :, :, :] # Todos los tiempos del Canal 2

        ## Ejemplo: Acceder a la imagen del Tiempo 0, Canal 1
        #foto = image_tif[0, 0, :, :, :] 

        #print(f"Forma de una sola foto: {foto.shape}") # Debería ser (480, 640, 3)
        #time_idx = 0 # from 0 to the final time, originally
        time_idx_start=1
        time_idx_end=-1
        fig, axes = plt.subplots(2,2 , figsize=(16, 8))

        axes[0,0].imshow(image_tif[time_idx_start, 0, :, :, :])
        axes[0,0].set_title(f'Canal 1 - Tiempo {time_idx_start}')
        axes[0,0].axis('off')

        axes[0,1].imshow(image_tif[time_idx_start, 1, :, :, :])
        axes[0,1].set_title(f'Canal 2 - Tiempo {time_idx_start}')
        axes[0,1].axis('off')

        axes[1,0].imshow(image_tif[time_idx_end, 0, :, :, :])
        axes[1,0].set_title(f'Canal 1 - Tiempo {time_idx_end}')
        axes[1,0].axis('off')

        axes[1,1].imshow(image_tif[time_idx_end, 1, :, :, :])
        axes[1,1].set_title(f'Canal 2 - Tiempo {time_idx_end}')
        axes[1,1].axis('off')

        plt.tight_layout()
        plt.show()

        # 1. Cargar el archivo de metadata
        #path_metadata = os.path.join('photos_treatments_06052026', '06052026_test_in_OneFile', '06052026_0102pm_MMStack_Pos0_metadata.txt')
        path_metadata = os.path.join('photos_treatments_06052026', '06052026_test_in_OneFile', '*_metadata.txt')#Search any file that has metadata.txt in the name
        matching_files = glob(path_metadata)#stack matching files, it is supposed to be only one
        for path_metadata in matching_files:
            with open(path_metadata, 'r') as f:
                data_tif = json.load(f)

        data = [image_tif[i, 1, :, :, :] for i in range(image_tif.shape[0])][1:]
        # 2. Extraer los datos del Canal 2 (índice 1 en Micro-Manager)
        result_temp = []

        for key in data_tif:
            if key.startswith("FrameKey"):
                # La estructura es FrameKey-Tiempo-Canal-Z
                partes = key.split("-")
                canal = partes[2]
                tiempo = partes[1]
                
                # Filtramos solo el Canal 2 (índice 1)
                if canal == "1":
                    valor_arduino = data_tif[key].get("Arduino-Input-AnalogInput0")
                    result_temp.append({
                        "Tiempo": int(tiempo)*t_interval,
                        "Temperatura": valor_arduino
                    })

        # 3. Ordenar por tiempo para que el CSV sea cronológico
        result_temp.sort(key=lambda x: x["Tiempo"])

        # 4. Guardar en CSV
        with open(name_csv+".csv", "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["Tiempo", "Temperatura"])
            writer.writeheader()
            writer.writerows(result_temp)

        print(f"Archivo guardado. Se procesaron {len(result_temp)} puntos de datos.")

    ## End modification for ome.tif

    except Exception as e: 
        print(f'ERROR: {e}')
        return

    # ETAPA 1: DETECCION DE CELDAS
    # pedir al usuario las celdas seleccionadas
    datos_interfaz = interfaz.main((dimension_x, dimension_y))
    #print(datos_interfaz)
    celdas, tratamientos = cargar_celdas_tratamientos(datos_interfaz)

    # se obtiene la imagen inicial en gris para la detección de circulos
    #img_inicial_gris = io.imread(data[0], as_gray=True)
    #img_inicial_gris = img_inicial_gris[pixel_y_1:pixel_y_2, pixel_x_1:pixel_x_2] # imagen recortada
    #alto_img, ancho_img = img_inicial_gris.shape[0], img_inicial_gris.shape[1] # ancho y alto (en pixeles) de la imagen recortada
    

    #Start green channel modifications
    #img_inicial_color = io.imread(data[0])
    #img_inicial_color= data[0] #original
    #img_inicial_color= data[-1] #change because of darkness
    time_choose_image=int(time_choose_image)
    img_inicial_color= data[time_choose_image]
    plt.figure()
    plt.imshow(img_inicial_color)
    plt.show()
    img_inicial_verde = img_inicial_color[:,:,1]
    plt.figure()
    plt.imshow(img_inicial_verde)
    plt.title('Imagen Inicial Canal Verde')
    plt.show()
    img_inicial_verde = img_inicial_verde[pixel_y_1:pixel_y_2, pixel_x_1:pixel_x_2]
    alto_img, ancho_img = img_inicial_verde.shape[0], img_inicial_verde.shape[1]
    print(alto_img, ancho_img, 'alto y ancho', img_inicial_verde.shape)
    #Finish green channel modifications

    ## Deteccion centroides
    imagen_con_puntos, centroides = segmentar_y_encontrar_centroides_multiples(img_inicial_color,radio_min_px=5,radio_max_px=8, threshold_binarization=threshold_transform)

    if centroides:
        print(f"Se encontraron {len(centroides)} objetos principales en:")
        for centroide in centroides:
            print(f"  - {centroide}")
        
        #plt.imshow(cv2.cvtColor(imagen_con_puntos, cv2.COLOR_BGR2RGB))
        plt.imshow(imagen_con_puntos)
        plt.title("Objetos de alta intensidad verde encontrados")
        plt.axis('off')
        plt.show()
    else:
        print("No se encontró ningún objeto dentro del rango de tamaño especificado.")
        plt.imshow(cv2.cvtColor(img_inicial_verde, cv2.COLOR_BGR2RGB))
        plt.title("No se encontraron objetos")
        plt.axis('off')
        plt.show()

    ## Termina deteccion centroides
    alto_celda, ancho_celda = (alto_img//dimension_y), (ancho_img//dimension_x)
    
    # para cada celda seleccionada, detectar el circulo correspondiente
    for celda in celdas:
        i, j = celda.coordenada
        #img_celda = obtener_imagen_celda(img_inicial_gris, i, j, alto_celda, ancho_celda)
        img_celda = obtener_imagen_celda(img_inicial_verde, i, j, alto_celda, ancho_celda)
        try:
            circulo = obtener_circulos(img_celda, celda.tipo, threshold_transform, plotear=True)
        except Exception as e:
            print(f'ERROR: {e} en la celda {celda.coordenada_alfanumerica}')
            print('celda ', celda.tipo, celda.tipo=='Control Negativo')#temporal
            celda.establecer_estado_error()
        else:
            celda.circulo = circulo
    
    # ETAPA 2: RECOLECCION DE DATOS 
    #for t, ruta_imagen in enumerate(data): # útil en caso de necesitar el tiempo (discreto empezando en 0) de cada imagen en el dataset
    for ruta_imagen in data:
        #im = io.imread(ruta_imagen)
        im=ruta_imagen
        im = im[pixel_y_1:pixel_y_2, pixel_x_1:pixel_x_2, :] # se recorta la imagen     
        for celda in celdas:
            if celda.estado != 'error':
                # obtener los valores de la imagen consultando el circulo. Si no se detectó un único círculo, no se calcula la intensidad
                circulo = celda.circulo
                i, j = celda.coordenada
                img_celda = obtener_imagen_celda(im, i, j, alto_celda, ancho_celda)
                valor = calcular_intensidad(img_celda, circulo)
                celda.agregar_intensidad(valor)

    # Por ultimo, se calcula el threshold  y se determinan los resultados de cada muestra para cada tratamiento
    for tratamiento in tratamientos:
        tratamiento.concluir_tratamiento()
    
    # ETAPA 3: GRAFICAR CADA CELDA EN FUNCIÓN DEL TIEMPO
    graficar_intensidad_tiempo_tratamientos(tratamientos, intervalo_tiempo=t_interval)

    #grafica sigmoidal
    # ETAPA 4: AJUSTE SIGMOIDAL Y GRÁFICA DE INTENSIDAD POR TRATAMIENTO
    for tratamiento in tratamientos:
        pendientes, b = graficar_intensidad_tiempo_tratamiento(tratamiento, intervalo_tiempo=t_interval)
    print(pendientes, b)
    for tratamiento in tratamientos:
        graficar_pendientes_tiempo_tratamiento(tratamiento, intervalo_tiempo=t_interval)

if __name__ == "__main__":
    main()