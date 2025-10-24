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

    nodo_hijo = Nodo(nodo, (nuevo_x, nuevo_y), mapa_nuevo, nave_nueva, muestras_nuevas, coste_nuevo)
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

def buscar_menor_costo(arbol: Arbol):
    lista = arbol.arbol
    menor_costo = float('inf')
    indice_menor_costo = 0

    for i, nodo in enumerate(lista):
        costo_actual = nodo.getCosto()
        if costo_actual < menor_costo:
            menor_costo = costo_actual
            indice_menor_costo = i
        elif costo_actual == menor_costo:
            # Si los costos son iguales, preferir el nodo con más muestras
            if nodo.getMuestras() > lista[indice_menor_costo].getMuestras():
                indice_menor_costo = i

    return indice_menor_costo

def coste_uniforme(mapa: list[list[int]]):
    start_time = time.perf_counter()
    arbol = Arbol(mapa, movimientos)

    while True:
        i = buscar_menor_costo(arbol)
        exito = arbol.expandir_nodo(i)
        if exito is not None:
            exito["Reporte"]["Costo"] = arbol.arbol[i].getCosto()
            exito["Reporte"]["Tiempo"] = time.perf_counter() - start_time
            return exito