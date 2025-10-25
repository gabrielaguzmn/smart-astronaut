# 🚀 Smart Astronaut

**Proyecto de Inteligencia Artificial**

## Descripción

Simulador que evalúa algoritmos de búsqueda para ayudar a un astronauta a recolectar 3 muestras científicas en Marte. El escenario modela mediante una cuadrícula de 10x10 que representa el entorno del astronauta, incluyendo obstáculos naturales, terrenos de distinta dificultad y una nave auxiliar con combustible limitado.


## Algoritmos Implementados

### Búsqueda No Informada
- **Amplitud**: Explora nivel por nivel
- **Costo Uniforme**: Encuentra el camino de menor costo
- **Profundidad sin Ciclos**: Explora en profundidad una rama evitando ciclos

### Búsqueda Informada
- **Avara**: Usa heurística de distancia Manhattan
- **A***: Combina costo + heurística para solución óptima

## Requisitos

### Python 3.10+
```bash
python --version
```

### Librerías Necesarias
```bash
pip install numpy pygame Pillow
```

**Nota:** Tkinter viene con Python (no necesita instalación) a menos que use Linux, en ese caso
requiere instalación
```bash
sudo apt-get install python3-tk  # Ubuntu/Debian
```

## Estructura

```
smart-astronaut/
├── assets/                    # Imágenes y música
├── Busqueda_no_informada/     # Avara, A*
├── Busqueda_no_informada/     # Amplitud, Costo uniforme, Profundidad
├── definiciones.py            # Clases Nodo y Arbol
├── gui.py                     # Interfaz gráfica
└── Prueba1.txt               # Mapa de ejemplo
```
## Usabilidad
Para probar todos los algoritmos solo se ejecuta el archivo gui.py

