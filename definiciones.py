import numpy as np

class Nodo:
    def __init__(self, padre: "Nodo", ubicacion: tuple, combustible_nave: int, muestras: int, costo: int = None, heuristica = None):
        self.padre = padre
        self.ubicacion = ubicacion
        self.combustible_nave = combustible_nave
        self.muestras = muestras
        self.costo = costo if costo is not None else 0 # g(n)
        self.heuristica = heuristica # h(n)
        self.f = costo + heuristica if costo is not None and heuristica is not None else 0 # f(n) = g(n) + h(n)
        self.profundidad = 0 if padre is None else padre.profundidad + 1
    
    def getPadre(self):
        return self.padre
    
    def getUbicacion(self):
        return self.ubicacion
    
    def getCombustible(self):
        return self.combustible_nave

    def getMuestras(self):
        return self.muestras

    def getCosto(self):
        return self.costo
    
    def getProfundidad(self):
        return self.profundidad
    
    def estado(self):
        return (self.ubicacion, self.combustible_nave, self.muestras)

    def es_meta(self):
        if self.muestras == 3:
            return True
        return False
    
    def camino(self):
        nodo, resultado = self, [self.ubicacion]
        while nodo.padre is not None:
            resultado.append(nodo.padre.ubicacion)
            nodo = nodo.padre
        return list(reversed(resultado))

class Arbol:
    def __init__(self, mapa: list[list[int]], movimientos: list):
        
        self.mapa = mapa
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
                    self.arbol = [Nodo(None, (x, y), False, 0)]
                    break
            if encontrado:
                break
    
    def reporte(self):
        return {"Nodos expandidos": self.nodos_expandidos, 
                "Profundidad": self.profundidad,
                "Costo": self.costo}
    
    def actualizar_reporte(self, nodo: Nodo):
        self.nodos_expandidos = self.nodos_expandidos + 1
        if nodo.getProfundidad() > self.profundidad:
            self.profundidad = nodo.getProfundidad()

    def expandir_nodo(self, indice: int):
        arbol = self.arbol
        nodo = arbol[indice]
        
        if nodo.es_meta():
            return {"Camino": nodo.camino(), "Reporte": self.reporte()}

        for movimiento in self.movimientos:
            nodo_expandido = movimiento(nodo, self.mapa)
            if nodo_expandido is not None:
                arbol.append(nodo_expandido)
                self.actualizar_reporte(nodo_expandido)

        arbol.pop(indice)
        self.arbol = arbol
        
        return None

def mover(nodo: Nodo, mapa: list[list[int]], dx: int, dy: int) -> Nodo | None:
    alto = len(mapa)
    ancho = len(mapa[0])
    (x, y) = nodo.getUbicacion()
    padre = nodo.getPadre()

    nx, ny = x + dx, y + dy  # Nueva ubicación

    dentro_del_mapa = (0 <= nx < alto and 0 <= ny < ancho)
    
    if (dentro_del_mapa):
        no_es_obstaculo = (mapa[nx][ny] != 1)
        llego_a_la_nave = (mapa[nx][ny] == 5) 
        llego_a_una_muestra = (mapa[nx][ny] == 6)

    if(dentro_del_mapa and no_es_obstaculo): # Validar que el movimiento sea valido

        nodo_hijo = Nodo(nodo, (nx, ny), nodo.getCombustible(), nodo.getMuestras())

        if (llego_a_la_nave):
            nodo_hijo = Nodo(nodo, (nx, ny), 20, nodo.getMuestras())
        if (llego_a_una_muestra): 
            nodo_hijo = Nodo(nodo, (nx, ny), nodo.getCombustible(), nodo.getMuestras()+1) 

        no_se_devuelve = (padre.estado() != nodo_hijo.estado()) if padre is not None else True

        if no_se_devuelve:
            return nodo_hijo

    return None

def mover_arriba(nodo: Nodo, mapa: list[list[int]]) -> Nodo | None:
    return mover(nodo, mapa, -1, 0)

def mover_abajo(nodo: Nodo, mapa: list[list[int]]) -> Nodo | None:
    return mover(nodo, mapa, 1, 0)

def mover_izquierda(nodo: Nodo, mapa: list[list[int]]) -> Nodo | None:
    return mover(nodo, mapa, 0, -1)

def mover_derecha(nodo: Nodo, mapa: list[list[int]]) -> Nodo | None:
    return mover(nodo, mapa, 0, 1)

mapa1 = np.loadtxt("Prueba1.txt", dtype=int)    

movimientos = [lambda n, mapa: mover_izquierda(n, mapa), 
               lambda n, mapa: mover_derecha(n, mapa), 
               lambda n, mapa: mover_arriba(n, mapa), 
               lambda n, mapa: mover_abajo(n, mapa)]

arbol = Arbol(mapa1, movimientos)

while True:
    exito = arbol.expandir_nodo(0)
    if exito is not None:
        print(exito)
        break