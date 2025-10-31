import sys
import os
import time
from pathlib import Path

sys.path.append(str(Path(os.path.abspath(__file__)).parent.parent))
from definiciones import Arbol, Nodo


"""Busqueda avara (greedy best-first) para el problema del mapa.

Este módulo implementa una estrategia avara que expande en cada
iteración el nodo de la frontera con la mejor heurística.

Conceptos básicos:
- `Arbol`: estructura que contiene la frontera en `arbol.arbol` y
    métodos para expandir nodos.
- `Nodo`: representa un estado en el mapa con métodos como
    `getMapa()`, `getUbicacion()`, `getCosto()`, `getMuestras()`,
    `getNave()`, `getCombustible()`, `getPadre()`, `estado()` y `es_meta()`.

Variables importantes (en este archivo):
- `mapa`: lista 2D (grid) con valores que codifican el terreno:
    0=libre, 1=obstáculo, 3=rocoso, 4=volcánico, 5=nave, 6=muestra
- `arbol.arbol`: lista que actúa como frontera (lista de `Nodo`).
- `estados_visitados`: set de representaciones hashables de estados
    para evitar re-expansiones.

Nota: este archivo añade documentación y comentarios para facilitar
la comprensión; no cambia la lógica original.
"""

def mover(nodo: Nodo, dx: int, dy: int) -> Nodo | None:
    """Intentar mover desde `nodo` en la dirección (dx, dy).

    Parámetros:
    - nodo: Nodo actual desde el que se intenta mover.
    - dx, dy: desplazamiento de fila (x) y columna (y).

    Comportamiento y variables internas:
    - mapa: grid actual del nodo (lista 2D).
    - alto, ancho: dimensiones del mapa.
    - (x,y): posición actual del nodo.
    - nuevo_x, nuevo_y: posición objetivo tras el movimiento.
    - dentro_del_mapa: bool, si la nueva posición está dentro de límites.
    - no_es_obstaculo: bool, si la celda objetivo no es un obstáculo (valor 1).
    - mapa_nuevo: copia del mapa que se usará para crear el nodo hijo.
      Nota: se usa `mapa.copy()` (copia superficial). Si `mapa` es una
      lista de listas, es recomendable usar `copy.deepcopy(mapa)` para
      evitar aliasing entre nodos (véase TODO abajo).
    - padre: referencia al nodo padre para evitar devolver el padre
      inmediato como hijo (retroceso simple).
    - terreno_rocoso / terreno_volcanico / llego_a_la_nave / llego_a_una_muestra:
      booleanos que describen el tipo de la celda destino.
    - nave_nueva: estado de la nave en el hijo -> [tiene_nave: bool, combustible: int].
    - muestras_nuevas: contador de muestras recogidas hasta el hijo.
    - coste_nuevo: coste acumulado en el hijo (según reglas de combustible y terreno).

    Devuelve:
    - Nodo hijo con heurística calculada, o None si el movimiento no es válido
      (fuera del mapa, obstáculo) o si el hijo es igual al padre (retroceso).
    """

    mapa = nodo.getMapa()
    alto, ancho = nodo.dimensiones_mapa()
    (x, y) = nodo.getUbicacion()
    nuevo_x, nuevo_y = x + dx, y + dy

    # Verificar límites
    dentro_del_mapa = (0 <= nuevo_x < alto and 0 <= nuevo_y < ancho)
    if not dentro_del_mapa:
        return None
    
    # Verificar obstáculo (1 significa obstáculo)
    no_es_obstaculo = (mapa[nuevo_x][nuevo_y] != 1)
    if not no_es_obstaculo:
        return None

    # Copia superficial del mapa (ATENCIÓN: podría requerir deepcopy si es 2D)
    mapa_nuevo = mapa.copy()
    padre = nodo.getPadre()

    # Detectar tipo de terreno o elementos en la celda destino
    terreno_rocoso = (mapa[nuevo_x][nuevo_y] == 3) 
    terreno_volcanico = (mapa[nuevo_x][nuevo_y] == 4)
    llego_a_la_nave = (mapa[nuevo_x][nuevo_y] == 5) 
    llego_a_una_muestra = (mapa[nuevo_x][nuevo_y] == 6) 
        
    # Estado por defecto heredado del nodo actual
    nave_nueva = (nodo.getNave(), nodo.getCombustible())
    muestras_nuevas = nodo.getMuestras()

    # Si llega a la nave: recarga combustible y marca la celda como libre
    if llego_a_la_nave:
        nave_nueva = (True, 20)
        mapa_nuevo[nuevo_x][nuevo_y] = 0   

    # Si llega a una muestra: incrementa contador y borra la muestra del mapa
    if llego_a_una_muestra:
        muestras_nuevas = nodo.getMuestras() + 1
        mapa_nuevo[nuevo_x][nuevo_y] = 0   

    # Calcular coste del movimiento según reglas: consumo de combustible
    # si tiene la nave y combustible > 0, o coste según terreno si no.
    if (nodo.getNave() and nodo.getCombustible() > 0):
        coste_nuevo = nodo.getCosto() + 0.5
        nave_nueva = (True, nodo.getCombustible() - 1)
    else:
        if terreno_rocoso:
            coste_nuevo = nodo.getCosto() + 3
        elif terreno_volcanico:
            coste_nuevo = nodo.getCosto() + 5
        else:
            coste_nuevo = nodo.getCosto() + 1

    # Calcular heurística del nuevo nodo (función externa)
    heuristica = calcular_heuristica(nuevo_x, nuevo_y, mapa_nuevo, muestras_nuevas)
    nodo_hijo = Nodo(nodo, (nuevo_x, nuevo_y), mapa_nuevo, nave_nueva, muestras_nuevas, coste_nuevo, heuristica)

    # Evitar devolver el nodo padre como hijo inmediato (retroceso simple)
    no_se_devuelve = (padre.estado() != nodo_hijo.estado()) if padre is not None else True

    return nodo_hijo if no_se_devuelve else None

def calcular_heuristica(x: int, y: int, mapa: list, muestras_recolectadas: int) -> float:
    """Calcular heurística desde la posición (x,y).

    La heurística guía la búsqueda hacia la muestra más cercana (Manhattan).

    Parámetros:
    - x,y: coordenadas del nodo actual.
    - mapa: grid 2D donde 6 indica una muestra por recoger.
    - muestras_recolectadas: contador de muestras ya recogidas.

    Retorna un float: menor valor = más prometedor.

    Reglas:
    - Si ya se han recogido 3 muestras, devuelve 0 (estado final relativo).
    - Si no hay muestras en el mapa devuelve 0.
    - Si hay muestras, calcula la distancia Manhattan mínima a la
      muestra más cercana y añade dos factores:
      - factor_progreso: 0.1 por muestra faltante (favorece estados que
        hayan recogido más muestras).
      - factor_desempate: (x+y)*0.01 para romper empates de forma determinista.
    """

    # Si ya se ha alcanzado la cantidad objetivo de muestras
    if muestras_recolectadas >= 3:
        return 0
    
    # Buscar posiciones de muestras (valor 6 en el mapa)
    muestras_restantes = []
    alto, ancho = len(mapa), len(mapa[0])
    
    for i in range(alto):
        for j in range(ancho):
            if mapa[i][j] == 6:  
                muestras_restantes.append((i, j))
    
    if not muestras_restantes:
        return 0
    
    # Distancia Manhattan mínima a alguna muestra
    distancia_minima = float('inf')
    for muestra_x, muestra_y in muestras_restantes:
        distancia = abs(x - muestra_x) + abs(y - muestra_y)
        distancia_minima = min(distancia_minima, distancia)
    
    muestras_faltantes = 3 - muestras_recolectadas
    
    # Pequeños factores para guiar el progreso y desempates
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

def buscar_mejor_heuristica(arbol: Arbol):
    """Selecciona el índice del nodo en `arbol.arbol` con la mejor heurística.

    Criterios:
    1. Menor `heuristica`.
    2. Si empate, preferir más `getMuestras()` (fomenta progreso).
    3. Si empate, preferir menor `getProfundidad()` (nodo más cercano a la raíz).

    Retorna el índice (int) dentro de `arbol.arbol`.
    """

    lista = arbol.arbol
    mejor_heuristica = float('inf')
    indice_mejor = 0

    for i, nodo in enumerate(lista):
        heuristica_actual = nodo.heuristica
        
        if heuristica_actual < mejor_heuristica:
            mejor_heuristica = heuristica_actual
            indice_mejor = i
        elif heuristica_actual == mejor_heuristica:
            # Desempates: primero por muestras recolectadas, luego por profundidad
            nodo_actual = lista[i]
            nodo_mejor = lista[indice_mejor]
            
            if nodo_actual.getMuestras() > nodo_mejor.getMuestras():
                indice_mejor = i
            elif (nodo_actual.getMuestras() == nodo_mejor.getMuestras() and 
                  nodo_actual.getProfundidad() < nodo_mejor.getProfundidad()):
                indice_mejor = i

    return indice_mejor

def avara(mapa: list[list[int]]):
    """Ejecución principal de la búsqueda avara.

    Parámetros:
    - mapa: grid 2D (lista de listas) con la codificación del terreno.

    Flujo general:
    1. Crear `Arbol` a partir del mapa y obtener el nodo inicial.
    2. Calcular la heurística inicial y asignarla al nodo raíz.
    3. Mantener un set `estados_visitados` para evitar re-expansiones.
    4. En cada iteración: seleccionar el mejor nodo por heurística,
       si ya fue visitado eliminarlo de la frontera; si no, expandirlo.
    5. Si `arbol.expandir_nodo(i)` retorna `exito` (un dict con resultado),
       finalizar y devolver el reporte con tiempo y coste.
    6. Si se alcanzan `max_iteraciones` o la frontera se vacía, retornar
       un reporte indicando fallo.

    Retorna:
    - Diccionario con la ruta y un sub-dict `Reporte` con estadísticas.
    """

    start_time = time.perf_counter()
    arbol = Arbol(mapa, movimientos)
    
    # Inicializar heurística del nodo raíz
    nodo_inicial = arbol.arbol[0]
    x_inicial, y_inicial = nodo_inicial.getUbicacion()
    heuristica_inicial = calcular_heuristica(x_inicial, y_inicial, nodo_inicial.getMapa(), nodo_inicial.getMuestras())
    nodo_inicial.heuristica = heuristica_inicial
    
    # Conjunto para evitar expandir estados ya procesados
    estados_visitados = set()
    max_iteraciones = 10000 

    iteracion = 0
    while arbol.arbol and iteracion < max_iteraciones:
        iteracion += 1
       
        # seleccionar índice del mejor nodo por heurística
        i = buscar_mejor_heuristica(arbol)
        
        nodo_actual = arbol.arbol[i]
        estado_actual = nodo_actual.estado()
        
        # Si ya procesamos este estado, eliminar el nodo duplicado de la frontera
        if estado_actual in estados_visitados:
            arbol.arbol.pop(i)
            continue
            
        # Marcar como visitado y expandir
        estados_visitados.add(estado_actual)

        exito = arbol.expandir_nodo(i)
        
        if exito is not None:
            # Si se detectó meta, buscar nodo meta en la frontera para extraer su coste
            nodo_meta = None
            for nodo in arbol.arbol:
                if nodo.es_meta():
                    nodo_meta = nodo
                    break
            
            if nodo_meta:
                exito["Reporte"]["Costo"] = nodo_meta.getCosto()
            exito["Reporte"]["Tiempo"] = time.perf_counter() - start_time
            
            return exito
    
    # Si no se encontró solución dentro del límite, retornar reporte de error
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


