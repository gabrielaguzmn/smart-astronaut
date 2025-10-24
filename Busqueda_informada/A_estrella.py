import sys
import os
import time
from pathlib import Path

sys.path.append(str(Path(os.path.abspath(__file__)).parent.parent))
from definiciones import Arbol, Nodo

def mover(nodo: Nodo, dx: int, dy: int) -> Nodo | None:

    mapa = nodo.getMapa()
    alto, ancho = nodo.dimensiones_mapa()
    (x, y) = nodo.getUbicacion()
    nuevo_x, nuevo_y = x + dx, y + dy

    dentro_del_mapa = (0 <= nuevo_x < alto and 0 <= nuevo_y < ancho)
    if not dentro_del_mapa:
        return None
    
    no_es_obstaculo = (mapa[nuevo_x][nuevo_y] != 1)
    if not no_es_obstaculo:
        return None

    mapa_nuevo = mapa.copy()
    padre = nodo.getPadre()

    terreno_rocoso = (mapa[nuevo_x][nuevo_y] == 3) 
    terreno_volcanico = (mapa[nuevo_x][nuevo_y] == 4)
    llego_a_la_nave = (mapa[nuevo_x][nuevo_y] == 5) 
    llego_a_una_muestra = (mapa[nuevo_x][nuevo_y] == 6) 
        
    nave_nueva = [nodo.getNave(), nodo.getCombustible()]
    muestras_nuevas = nodo.getMuestras()

    if llego_a_la_nave:
        nave_nueva = [True, 20]
        mapa_nuevo[nuevo_x][nuevo_y] = 0   

    if llego_a_una_muestra:
        muestras_nuevas = nodo.getMuestras() + 1
        mapa_nuevo[nuevo_x][nuevo_y] = 0   

    if (nodo.getNave() and nodo.getCombustible() > 0):
        coste_nuevo = nodo.getCosto() + 0.5
        nave_nueva = [True, nodo.getCombustible() - 1]
    else:
        if terreno_rocoso:
            coste_nuevo = nodo.getCosto() + 3
        elif terreno_volcanico:
            coste_nuevo = nodo.getCosto() + 5
        else:
            coste_nuevo = nodo.getCosto() + 1

    heuristica = calcular_heuristica(nuevo_x, nuevo_y, mapa_nuevo, muestras_nuevas)
    nodo_hijo = Nodo(nodo, (nuevo_x, nuevo_y), mapa_nuevo, nave_nueva, muestras_nuevas, coste_nuevo, heuristica)
    no_se_devuelve = (padre.estado() != nodo_hijo.estado()) if padre is not None else True

    return nodo_hijo if no_se_devuelve else None

def calcular_heuristica(x: int, y: int, mapa: list, muestras_recolectadas: int) -> float:

    if muestras_recolectadas >= 3:  
        return 0
    
    muestras_restantes = []
    alto, ancho = len(mapa), len(mapa[0])
    
    for i in range(alto):
        for j in range(ancho):
            if mapa[i][j] == 6:  
                muestras_restantes.append((i, j))
    
    if not muestras_restantes:
        return 0
    
    distancia_minima = float('inf')
    for muestra_x, muestra_y in muestras_restantes:
        distancia = abs(x - muestra_x) + abs(y - muestra_y)
        distancia_minima = min(distancia_minima, distancia)
    
    muestras_faltantes = 3 - muestras_recolectadas
    
    factor_progreso = muestras_faltantes * 0.1 
    factor_desempate = (x + y) * 0.01  
    
    return distancia_minima + factor_progreso + factor_desempate

def mover_izquierda(nodo: Nodo) -> Nodo | None:
    return mover(nodo, 0, -1)

def mover_derecha(nodo: Nodo) -> Nodo | None:
    return mover(nodo, 0, 1)

def mover_arriba(nodo: Nodo) -> Nodo | None:
    return mover(nodo, -1, 0)

def mover_abajo(nodo: Nodo) -> Nodo | None:
    return mover(nodo, 1, 0)

# Lista de movimientos disponibles
movimientos = [lambda n: mover_izquierda(n), 
               lambda n: mover_derecha(n), 
               lambda n: mover_arriba(n), 
               lambda n: mover_abajo(n)]

def buscar_mejor_ruta(arbol: Arbol, mapa: list[list[int]]):
    lista = arbol.arbol
    mejor_f = float('inf')
    indice_mejor = 0

    for i, nodo in enumerate(lista):
        f = nodo.f

        
        if f < mejor_f:
            mejor_f = f
            indice_mejor = i
        elif f == mejor_f:
 
            nodo_actual = lista[i]
            nodo_mejor = lista[indice_mejor]
            
            if nodo_actual.getMuestras() > nodo_mejor.getMuestras():
                indice_mejor = i
            elif (nodo_actual.getMuestras() == nodo_mejor.getMuestras() and 
                  nodo_actual.getProfundidad() < nodo_mejor.getProfundidad()):
                indice_mejor = i

    return indice_mejor


def a_estrella(mapa: list[list[int]]):

    start_time = time.perf_counter()
    arbol = Arbol(mapa, movimientos)
    
    nodo_inicial = arbol.arbol[0]
    x_inicial, y_inicial = nodo_inicial.getUbicacion()
    heuristica_inicial = calcular_heuristica(x_inicial, y_inicial, nodo_inicial.getMapa(), nodo_inicial.getMuestras())
    nodo_inicial.heuristica = heuristica_inicial
    
    estados_visitados = set()
    max_iteraciones = 10000 

    iteracion = 0
    while arbol.arbol and iteracion < max_iteraciones:
        iteracion += 1
       
        i = buscar_mejor_ruta(arbol, mapa)
        
        nodo_actual = arbol.arbol[i]
        estado_actual = nodo_actual.estado()
        
        if estado_actual in estados_visitados:
            arbol.arbol.pop(i)
            continue
            
        estados_visitados.add(estado_actual)

        exito = arbol.expandir_nodo(i)
        
        if exito is not None:
            nodo_meta = None
            for nodo in arbol.arbol:
                if nodo.es_meta():
                    nodo_meta = nodo
                    break
            
            if nodo_meta:
                exito["Reporte"]["Costo"] = nodo_meta.getCosto()
            exito["Reporte"]["Tiempo"] = time.perf_counter() - start_time
            exito["Reporte"]["Iteraciones"] = iteracion
            return exito
    
    return {
        "Camino": [],
        "Reporte": {
            "Nodos expandidos": arbol.nodos_expandidos,
            "Profundidad": arbol.profundidad,
            "Costo": float('inf'),
            "Tiempo": time.perf_counter() - start_time,
            "Iteraciones": iteracion,
            "Error": "No se encontró solución o se alcanzó el límite de iteraciones"
        }
    }


