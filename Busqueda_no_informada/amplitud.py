import sys
import os
import time
from pathlib import Path

sys.path.append(str(Path(os.path.abspath(__file__)).parent.parent))
from definiciones import Arbol, Nodo


"""Búsqueda por amplitud (BFS) - implementación sencilla.

Este módulo define los movimientos y la función `amplitud(mapa)` que
realiza una búsqueda por niveles. La implementación usa `Arbol` para
gestionar la frontera y la expansión de nodos.

Notas importantes:
- `estados_visitados` se usa para evitar re-expansiones; en esta
    versión original la línea de marcado está comentada (mantener así
    para no cambiar la lógica existente).
"""

def mover(nodo: Nodo, dx: int, dy: int) -> Nodo | None:
    """Genera el nodo hijo tras mover (dx,dy) si el movimiento es válido.

    Devuelve `None` si el movimiento sale del mapa o golpea un obstáculo.
    """

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


def amplitud(mapa: list[list[int]]):
    """Ejecuta búsqueda en anchura (BFS) sobre `mapa`.

    Implementación:
    - Crea el `Arbol` con el mapa y las funciones de movimiento.
    - Mantiene un set `estados_visitados` para detectar estados repetidos
      (la línea que añade al set está comentada en la implementación original).
    - En cada ciclo toma el primer nodo de la lista (`i = 0`), lo examina
      y lo expande con `expandir_nodo`.

    Retorna un dict de éxito con camino y reporte cuando `expandir_nodo`
    detecta la meta.
    """

    start_time = time.perf_counter()
    arbol = Arbol(mapa, movimientos)
    
    estados_visitados = set()

    while True:
        i = 0 
        
        nodo_actual = arbol.arbol[i]
        estado_actual = nodo_actual.estado()
        
        # Si el estado ya fue visitado, eliminar el nodo duplicado de la frontera
        if estado_actual in estados_visitados:
            arbol.arbol.pop(i)
            continue
        
        # NOTA: la línea que añade el estado a `estados_visitados` está
        # comentada en la implementación original; la dejamos así para
        # no modificar la lógica existente.
        # estados_visitados.add(estado_actual)
        exito = arbol.expandir_nodo(i)
        
        if exito is not None:
            exito["Reporte"]["Tiempo"] = time.perf_counter() - start_time
            return exito