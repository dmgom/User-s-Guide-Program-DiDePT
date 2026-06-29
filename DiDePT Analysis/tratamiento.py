class Tratamiento:

    def __init__(self, nombre):
        self.nombre = nombre
        self.muestras = []
        #self.control_positivo = None
        #self.control_negativo = None
        self.controles_negativos=[]
        self.controles_positivos=[]
        self.threshold = None

    def agregar_muestra(self, muestra):
        self.muestras.append(muestra)

    def agregar_control_positivo(self, control_positivo):
        #self.control_positivo = control_positivo
        self.controles_positivos.append(control_positivo)
    def agregar_control_negativo(self, control_negativo):
        #self.control_negativo = control_negativo
        self.controles_negativos.append(control_negativo)

    def calcular_threshold(self, manual_threshold=20, porcentaje=0.5):
        """
        Calcula el threshold para el tratamiento.
        """
        #if self.control_positivo is None or self.control_negativo is None:
        #    print("WARNING: No se puede calcular el threshold sin ambos controles.")
        #    self.threshold = None
        #else:
        #    maximo_control_positivo = max(self.control_positivo.intensidades)
        #    maximo_control_negativo = max(self.control_negativo.intensidades)
        #    self.threshold = abs(maximo_control_positivo-maximo_control_negativo)*porcentaje + maximo_control_negativo
        #return self.threshold
        #print(self.controles_positivos, self.controles_negativos)
        if not self.controles_positivos or not self.controles_negativos:
            print("WARNING: No se puede calcular el threshold sin ambos controles.")
            self.threshold = None

        else:
            import numpy as np
            if manual_threshold=="MaxNegativo":
                # Sacamos el máximo promedio de todos los controles seleccionados
                #max_pos = np.mean([max(c.intensidades) for c in self.controles_positivos])
                #max_neg = np.mean([max(c.intensidades) for c in self.controles_negativos])
                #list_int=[c.intensidades for c in self.controles_positivos][0]
                #abs(max_pos - max_neg) * porcentaje + max_neg
                list_int=[max([c.intensidades for c in self.controles_negativos])]
                self.threshold = list_int[0]
            elif (manual_threshold is str) and manual_threshold!="MaxNegativo":
                #if manual_thresold is string but not one of the predetermined options, it will set the default value 20
                self.threshold = 20
            else:
                self.threshold= manual_threshold
                            
        return self.threshold
    
    def establecer_estado_muestras(self):
        """
        Establece el estado de las muestras del tratamiento.
        """
        for muestra in self.muestras:
            muestra.establecer_estado_final()
    
    def concluir_tratamiento(self, porcentaje=0.5):
        """
        Establece el estado de las muestras del tratamiento.
        """
        self.calcular_threshold(porcentaje)
        if self.threshold is not None:
            self.establecer_estado_muestras()
        return self.threshold

    def obtener_controles(self):
        """
        Devuelve una lista con los controles del tratamiento.
        """
        #return [c for c in [self.controles_positivos, self.controles_negativos] if c is not None]
        print('obtener_controles', self.controles_positivos+self.controles_negativos)
        return self.controles_positivos+self.controles_negativos
    def __str__(self):
        return f"Tratamiento: nombre = {self.nombre}, # muestras = {len(self.muestras)},\
            control_positivo = {self.controles_positivos}, control_negativo = {self.controles_negativos}"