class Nodo:
    """
    Representa un nodo en el árbol de búsqueda.

    Args:
        padre (Nodo): Nodo padre desde el cual se genera este nodo.
        ubicacion (tuple): Coordenadas (x, y) en el mapa.
        mapa (list[list[int]]): Representación matricial del entorno.
        nave (tuple[bool, int]): (estado de la nave, combustible disponible).
        muestras (int): Cantidad de muestras recolectadas.
        costo (int, opcional): Costo acumulado g(n). Por defecto 0.
        heuristica (int, opcional): Estimación h(n).

    Attributes:
        f (int): Valor de evaluación f(n) = g(n) + h(n).
        profundidad (int): Nivel en el árbol desde la raíz.
    """
    def __init__(self, padre: "Nodo", ubicacion: tuple, mapa: list[list[int]],
                 nave: tuple[bool, int], muestras: int, 
                 costo: int = None, heuristica = None):
        # Para el estado del nodo
        self.padre = padre
        self.ubicacion = ubicacion
        self.mapa = mapa
        self.nave = nave[0]
        self.combustible_nave = nave[1]
        self.muestras = muestras

        # Para algoritmos que usen costo y/o heuristica
        self.costo = costo if costo is not None else 0 # g(n)
        self.heuristica = heuristica # h(n)
        self.f = costo + heuristica if costo is not None and heuristica is not None else 0 # f(n) = g(n) + h(n)

        # Para calcular la profundidad de un arbol
        self.profundidad = 0 if padre is None else padre.profundidad + 1
    
    # ------------------------ METODOS GET ------------------------
    def getPadre(self):
        """Returns: Nodo padre."""
        return self.padre
    
    def getUbicacion(self):
        """Returns: tuple -> posición (x, y)."""
        return self.ubicacion
    
    def getMapa(self):
        """Returns: list[list[int]] -> estado actual del mapa."""
        return self.mapa
    
    def getNave(self):
        """Returns: bool -> True si tiene la nave."""
        return self.nave
    
    def getCombustible(self):
        """Returns: int -> cantidad de combustible disponible."""
        return self.combustible_nave

    def getMuestras(self):
        """Returns: int -> número de muestras recolectadas."""
        return self.muestras

    def getCosto(self):
        """Returns: int -> costo acumulado g(n)."""
        return self.costo
    
    def getProfundidad(self):
        """Returns: int -> nivel de profundidad en el árbol."""
        return self.profundidad
    
    # ------------------------ METODOS SET ------------------------
    def setMapa(self, mapa):
        """Args: mapa (list[list[int]]): nuevo estado del mapa."""
        self.mapa = mapa

    # ---------------------- FUNCIONES EXTRA ----------------------
    def dimensiones_mapa(self):
        """Returns: tuple -> (alto, ancho) del mapa."""
        return (len(self.mapa), len(self.mapa[0]))
    
    def estado(self):
        """Returns: tuple -> estado resumido del nodo."""
        return (self.ubicacion, self.nave, self.muestras)

    def es_meta(self):
        """Returns: bool -> True si se recolectaron todas las muestras."""
        if self.muestras == 3:
            return True
        return False
    
    def camino(self):
        """ Reconstruye el camino desde la raíz hasta este nodo. Returns: list[tuple]: lista de posiciones recorridas. """
        nodo, resultado = self, [self.ubicacion]
        while nodo.padre is not None:
            resultado.append(nodo.padre.ubicacion)
            nodo = nodo.padre
        return list(reversed(resultado))

class Arbol:
    """
    Representa el árbol de búsqueda para algoritmos de pathfinding.

    Args:
        mapa (list[list[int]]): Representación matricial del entorno.
        movimientos (list): Lista de funciones de movimiento disponibles.

    Attributes:
        movimientos (list): Funciones de movimiento que el astronauta puede realizar.
        nodos_expandidos (int): Contador de nodos que han sido expandidos.
        profundidad (int): Máxima profundidad alcanzada en el árbol.
        costo (int): Máximo costo encontrado durante la búsqueda.
        arbol (list[Nodo]): Lista de nodos que conforman el árbol de búsqueda.
    """
    def __init__(self, mapa: list[list[int]], movimientos: list):
        self.movimientos = movimientos
        self.nodos_expandidos = 1
        self.profundidad = 0
        self.costo = 0

        alto = len(mapa)
        ancho = len(mapa[0])
        encontrado = False

        for x in range(0, alto):
            for y in range(0, ancho):
                if mapa[x][y] == 2:
                    encontrado = True
                    self.arbol = [Nodo(None, (x, y), mapa, [False, 0], 0)]
                    break
            if encontrado:
                break
    
    def reporte(self):
        """
        Genera un reporte con las métricas de la búsqueda.
        
        Returns:
            dict: Diccionario con nodos expandidos, profundidad y costo.
        """
        return {"Nodos expandidos": self.nodos_expandidos, 
                "Profundidad": self.profundidad,
                "Costo": self.costo}
    
    def actualizar_reporte(self, nodo: Nodo):
        """
        Actualiza las métricas del reporte con la información de un nuevo nodo.
        
        Args:
            nodo (Nodo): Nodo recién expandido para actualizar estadísticas.
        """
        self.nodos_expandidos = self.nodos_expandidos + 1
        if nodo.getProfundidad() > self.profundidad:
            self.profundidad = nodo.getProfundidad()
        if nodo.getCosto() > self.costo:
            self.costo = nodo.getCosto()

    def expandir_nodo(self, indice: int):
        """
        Expande un nodo específico del árbol generando sus nodos hijos.
        
        Args:
            indice (int): Índice del nodo a expandir en la lista del árbol.
            
        Returns:
            dict | None: Si se alcanza la meta, retorna diccionario con camino y reporte.
                         Si no, retorna None para continuar la búsqueda.
        """
        arbol = self.arbol
        nodo = arbol[indice]
        
        if nodo.es_meta():
            return {"Camino": nodo.camino(), "Reporte": self.reporte()}

        for movimiento in self.movimientos:
            nodo_expandido = movimiento(nodo)
            if nodo_expandido is not None:
                arbol.append(nodo_expandido)
                self.actualizar_reporte(nodo_expandido)

        arbol.pop(indice)
        self.arbol = arbol
        
        return None
    
"""
PLANTILLA DE MOVIMIENTOS

def mover(nodo: Nodo, dx: int, dy: int) -> Nodo | None:
    mapa = nodo.getMapa()
    alto, ancho = nodo.dimensiones_mapa()
    (x, y) = nodo.getUbicacion()
    nuevo_x, nuevo_y = x + dx, y + dy

    # ------------------ VALIDACIONES DEL MOVIMIENTO ------------------
    dentro_del_mapa = (0 <= nuevo_x < alto and 0 <= nuevo_y < ancho)
    if not dentro_del_mapa:
        return None
    
    no_es_obstaculo = (mapa[nuevo_x][nuevo_y] != 1)
    if not no_es_obstaculo:
        return None
    # -----------------------------------------------------------------

    mapa_nuevo = mapa.copy()
    padre = nodo.getPadre()

    llego_a_la_nave = (mapa[nuevo_x][nuevo_y] == 5) 
    llego_a_una_muestra = (mapa[nuevo_x][nuevo_y] == 6)

    if(llego_a_una_muestra or llego_a_la_nave):
        mapa_nuevo[nuevo_x][nuevo_y] = 0

    nodo_hijo = Nodo(nodo, (nuevo_x, nuevo_y), mapa_nuevo, [nodo.getNave(), nodo.getCombustible()], nodo.getMuestras())

    if (llego_a_la_nave):
        nodo_hijo = Nodo(nodo, (nuevo_x, nuevo_y), mapa_nuevo, [True, 20], nodo.getMuestras())
    if (llego_a_una_muestra): 
        nodo_hijo = Nodo(nodo, (nuevo_x, nuevo_y), mapa_nuevo, [nodo.getNave(), nodo.getCombustible()], nodo.getMuestras()+1)

    no_se_devuelve = (padre.estado() != nodo_hijo.estado()) if padre is not None else True

    return nodo_hijo if no_se_devuelve else None

def mover_izquierda(nodo: Nodo) -> Nodo | None:
    return mover(nodo, 0, -1)

def mover_derecha(nodo: Nodo) -> Nodo | None:
    return mover(nodo, 0, 1)

def mover_arriba(nodo: Nodo) -> Nodo | None:
    return mover(nodo, -1, 0)

def mover_abajo(nodo: Nodo) -> Nodo | None:
    return mover(nodo, 1, 0)

movimientos = [lambda n: mover_izquierda(n), 
               lambda n: mover_derecha(n), 
               lambda n: mover_arriba(n), 
               lambda n: mover_abajo(n)]
"""

"""
EJEMPLO

import numpy as np

mapa = np.loadtxt("Prueba1.txt", dtype=int)    

arbol = Arbol(mapa, movimientos)

while True:
    exito = arbol.expandir_nodo(0)
    if exito is not None:
        print(exito)
        break
"""