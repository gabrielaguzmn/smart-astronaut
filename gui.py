import tkinter
from tkinter import filedialog, messagebox, ttk
import pygame
from PIL import Image, ImageTk
import numpy as np

from Busqueda_no_informada.coste_uniforme import coste_uniforme
from Busqueda_informada.avara import avara
from Busqueda_informada.A_estrella import a_estrella
# Las siguientes importaciones se activarán cuando se implementen los algoritmos
from Busqueda_no_informada.amplitud import amplitud
from Busqueda_no_informada.profundidad_sin_ciclos import profundidad_sin_ciclos
# from Busqueda_informada.A_estrella import a_estrella

mapa_actual = None
mapa_original = None  # Para mantener el mapa original sin modificaciones
mapa_visual = None    # Para el estado visual actual (con muestras recogidas, etc.)
reporte_texto = None
recuadro_matriz = None  # Referencia al frame que contiene la matriz
animando = False  # Flag para controlar si hay una animación en curso
posicion_astronauta_original = None  # Para recordar dónde empezó el astronauta
tiene_nave = False  # Para saber si el astronauta tiene la nave
combustible_restante = 0  # Combustible restante de la nave
mapa_recorrido = False  # Para saber si ya se recorrió el mapa
posicion_nave_abandonada = None  # Para recordar dónde se dejó la nave
iconos = {
    0: Image.open("assets/libre.png"),
    1: Image.open("assets/obstaculo.png"),
    2: Image.open("assets/astronauta.png"),
    3: Image.open("assets/rocas.png"),
    4: Image.open("assets/volcan.png"),
    5: Image.open("assets/nave.png"),
    6: Image.open("assets/muestras.png")
}

def cargar_fondo(app, ruta_imagen):
    try:
        # Cargar la imagen de fondo
        imagen_fondo = tkinter.PhotoImage(file=ruta_imagen)
        
        # Crear un label para mostrar la imagen de fondo
        label_fondo = tkinter.Label(app, image=imagen_fondo)
        label_fondo.place(x=0, y=0, relwidth=1, relheight=1)
        
        # Mantener la referencia a la imagen para que no se borre
        app.imagen_fondo = imagen_fondo

    except Exception as e:
        print("No se pudo cargar la imagen de fondo:", e)
        # Si no se puede cargar la imagen, usar un color de fondo
        app.configure(bg="#1a1a2e")

def cargar_mapa():
    global mapa_actual, mapa_original, mapa_visual, posicion_astronauta_original, tiene_nave, animando, combustible_restante, mapa_recorrido
    
    # Detener cualquier animación en curso
    animando = False
    
    # Abrir ventana para seleccionar un archivo
    file_path = filedialog.askopenfilename(
        title="Seleccionar archivo de mapa",
        filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
    )
    
    if file_path:  # Si efectivamente se seleccionó un archivo
        try:
            # Cargar el archivo directamente como array usando numpy
            mapa_actual = np.loadtxt(file_path, dtype=int)
            mapa_original = mapa_actual.copy()  # Guardar copia original
            mapa_visual = mapa_actual.copy()    # Copia para modificaciones visuales
            
            # Encontrar la posición inicial del astronauta
            filas, columnas = mapa_actual.shape
            posicion_astronauta_original = None
            for i in range(filas):
                for j in range(columnas):
                    if mapa_actual[i][j] == 2:
                        posicion_astronauta_original = (i, j)
                        break
                if posicion_astronauta_original:
                    break
            
            tiene_nave = False
            combustible_restante = 0
            mapa_recorrido = False  # Resetear el estado de recorrido
            actualizar_pantalla()
            return mapa_actual
            
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar el archivo: {e}")
            mapa_actual = None
            mapa_original = None
            mapa_visual = None
            posicion_astronauta_original = None
            mapa_recorrido = False
            return None
        
def dibujar_matriz(app, mapa):
    global recuadro_matriz
    
    # Crear frame contenedor con tamaño fijo
    recuadro_matriz = tkinter.Frame(app, bg="white", highlightbackground="black", highlightthickness=2,
                             width=600, height=600)
    recuadro_matriz.place(x=40, y=51)
    recuadro_matriz.pack_propagate(False)

    # Calcular tamaños de celdas
    filas, columnas = len(mapa), len(mapa[0])
    ancho_celda = 600 // columnas
    alto_celda = 600 // filas

    # Dibujar celdas
    for x in range(filas):
        for y in range(columnas):
            valor = mapa[x][y]
            celda = tkinter.Label(recuadro_matriz, borderwidth=1, relief="solid")
            
            if valor in iconos and iconos[valor]:
                img_resized = iconos[valor].resize((ancho_celda-2, alto_celda-2), Image.Resampling.LANCZOS)
                tk_img = ImageTk.PhotoImage(img_resized)
                celda.config(image=tk_img)
                celda.image = tk_img
            else:
                celda.config(text=str(valor))

            celda.grid(row=x, column=y, sticky="nsew")

    return recuadro_matriz

def actualizar_celda_mapa(fila, columna, valor_mostrar, valor_terreno_original=None):
    """Actualiza una celda específica del mapa visual"""
    global recuadro_matriz, mapa_visual
    
    if recuadro_matriz is None:
        return
        
    # Calcular tamaños de celdas
    filas, columnas = len(mapa_visual), len(mapa_visual[0])
    ancho_celda = 600 // columnas
    alto_celda = 600 // filas
    
    # Obtener el widget de la celda específica
    for widget in recuadro_matriz.winfo_children():
        info = widget.grid_info()
        if info['row'] == fila and info['column'] == columna:
            # Si hay un terreno de fondo (rocas o volcanes) y queremos mostrar astronauta/nave encima
            if valor_terreno_original in [3, 4] and valor_mostrar in [2, 5]:
                # Crear imagen compuesta (terreno + astronauta/nave)
                try:
                    imagen_fondo = iconos[valor_terreno_original].resize((ancho_celda-2, alto_celda-2), Image.Resampling.LANCZOS)
                    imagen_encima = iconos[valor_mostrar].resize((ancho_celda-2, alto_celda-2), Image.Resampling.LANCZOS)
                    
                    # Crear una nueva imagen combinada
                    imagen_combinada = imagen_fondo.copy()
                    # Para superponer, hacemos el astronauta/nave semi-transparente
                    if imagen_encima.mode != 'RGBA':
                        imagen_encima = imagen_encima.convert('RGBA')
                    
                    # Aplicar transparencia al elemento superpuesto
                    alpha = Image.new('RGBA', imagen_encima.size, (255, 255, 255, 180))  # 180/255 = ~70% opacidad
                    imagen_encima = Image.composite(imagen_encima, alpha, imagen_encima)
                    
                    imagen_combinada.paste(imagen_encima, (0, 0), imagen_encima)
                    
                    tk_img = ImageTk.PhotoImage(imagen_combinada)
                    widget.config(image=tk_img)
                    widget.image = tk_img
                except Exception:
                    # Si falla la composición, mostrar solo el elemento principal
                    if valor_mostrar in iconos and iconos[valor_mostrar]:
                        img_resized = iconos[valor_mostrar].resize((ancho_celda-2, alto_celda-2), Image.Resampling.LANCZOS)
                        tk_img = ImageTk.PhotoImage(img_resized)
                        widget.config(image=tk_img)
                        widget.image = tk_img
            else:
                # Mostrar normalmente
                if valor_mostrar in iconos and iconos[valor_mostrar]:
                    img_resized = iconos[valor_mostrar].resize((ancho_celda-2, alto_celda-2), Image.Resampling.LANCZOS)
                    tk_img = ImageTk.PhotoImage(img_resized)
                    widget.config(image=tk_img)
                    widget.image = tk_img
                else:
                    widget.config(text=str(valor_mostrar), image="")
            break

def animar_movimiento(camino, velocidad=400):
    """Anima el movimiento del astronauta siguiendo el camino encontrado"""
    global mapa_visual, mapa_original, animando, posicion_astronauta_original, tiene_nave, combustible_restante, mapa_recorrido
    
    if not camino or len(camino) < 2:
        messagebox.showinfo("Información", "No hay camino para animar")
        return
    
    animando = True
    tiene_nave = False
    combustible_restante = 0
    pasos_con_nave = 0  # Contador de pasos dados CON la nave
    mapa_recorrido = True  # Marcar que el mapa ha sido recorrido
    posicion_nave_abandonada = None  # Reset de la posición de nave abandonada
    
    # Restaurar el mapa visual al estado original
    mapa_visual = mapa_original.copy()
    
    # Limpiar la posición inicial del astronauta (queda como terreno libre)
    if posicion_astronauta_original:
        mapa_visual[posicion_astronauta_original[0]][posicion_astronauta_original[1]] = 0
        actualizar_celda_mapa(posicion_astronauta_original[0], posicion_astronauta_original[1], 0)
    
    def mover_paso(indice):
        global animando, tiene_nave, combustible_restante, posicion_nave_abandonada
        nonlocal pasos_con_nave
        
        if indice >= len(camino) or not animando:
            animando = False
            return
            
        pos_actual = camino[indice]
        fila, columna = pos_actual[0], pos_actual[1]
        
        # Obtener el terreno original en esta posición
        terreno_original = mapa_original[fila][columna]
        
        # Si no es el primer paso, limpiar la posición anterior
        if indice > 0:
            pos_anterior = camino[indice - 1]
            fila_ant, columna_ant = pos_anterior[0], pos_anterior[1]
            terreno_anterior = mapa_original[fila_ant][columna_ant]
            
            # Si hay una nave abandonada en la posición anterior, mantenerla
            if posicion_nave_abandonada and pos_anterior == posicion_nave_abandonada:
                mapa_visual[fila_ant][columna_ant] = 5  # Mantener la nave abandonada
                actualizar_celda_mapa(fila_ant, columna_ant, 5)
            # Restaurar el terreno original en la posición anterior (sin verificar combustible aquí)
            elif terreno_anterior in [3, 4]:  # Rocas o volcanes se mantienen
                mapa_visual[fila_ant][columna_ant] = terreno_anterior
                actualizar_celda_mapa(fila_ant, columna_ant, terreno_anterior)
            elif terreno_anterior == 5 and not tiene_nave:  # Nave se mantiene si no la ha recogido
                mapa_visual[fila_ant][columna_ant] = 5
                actualizar_celda_mapa(fila_ant, columna_ant, 5)
            else:  # Terreno libre
                mapa_visual[fila_ant][columna_ant] = 0
                actualizar_celda_mapa(fila_ant, columna_ant, 0)
        
        # Manejar eventos especiales en la posición actual
        if terreno_original == 5 and not tiene_nave:  # Recoge la nave (solo si no la tiene)
            tiene_nave = True
            pasos_con_nave = 0  # Resetear contador cuando recoge la nave
            mapa_visual[fila][columna] = 5  # Mostrar nave (el astronauta está dentro)
            actualizar_celda_mapa(fila, columna, 5)
        elif terreno_original == 6:  # Recoge muestra
            mapa_visual[fila][columna] = 2  # La muestra desaparece, queda astronauta
            actualizar_celda_mapa(fila, columna, 2 if not tiene_nave else 5)
        elif terreno_original in [3, 4]:  # Rocas o volcanes
            mapa_visual[fila][columna] = terreno_original  # Mantener el terreno
            # Mostrar astronauta/nave superpuesto sobre el terreno
            actualizar_celda_mapa(fila, columna, 2 if not tiene_nave else 5, terreno_original)
        else:  # Terreno libre
            mapa_visual[fila][columna] = 2 if not tiene_nave else 5
            actualizar_celda_mapa(fila, columna, 2 if not tiene_nave else 5)
        
        # Incrementar contador de pasos con nave DESPUÉS de procesar la posición actual
        # Solo si no es el primer paso (indice 0 es la posición inicial)
        if tiene_nave and indice > 0:
            pasos_con_nave += 1
            
            # Verificar si se agotó el combustible DESPUÉS de este paso
            # Cambiado a >= 20 para que cuente exactamente 20 pasos (1, 2, 3, ..., 20)
            if pasos_con_nave >= 21:
                # Se acabó el combustible, guardar la posición donde se deja la nave
                posicion_nave_abandonada = (fila, columna)
                # Asegurar que la nave se muestre en esta posición
                mapa_visual[fila][columna] = 5
                actualizar_celda_mapa(fila, columna, 5)
                tiene_nave = False
                pasos_con_nave = 0
        
        # Actualizar la interfaz
        app.update()
        
        # Programar el siguiente paso
        if indice < len(camino) - 1:
            app.after(velocidad, lambda: mover_paso(indice + 1))
        else:
            animando = False
            
    # Iniciar la animación
    app.after(100, lambda: mover_paso(0))

def ver_reporte(app):
    global reporte_texto

    tkinter.Label(
        app, 
        text="REPORTE",
        font=("Comic Sans Ms", 22, "bold"),
        bg="white",
        pady=5
    ).pack(pady=10)

    reporte_texto = tkinter.StringVar()
    reporte_texto.set("Nodos expandidos: 0\n" +
                      "Profundidad del árbol: 0\n" +
                      "Tiempo: 0 segundos\n" +
                      "Costo: 0\n" +
                      "Pasos: 0",)

    tkinter.Label(
        app, 
        textvariable=reporte_texto,
        font=("Comic Sans Ms", 13),
        bg="white",
        justify="center",
        pady=5
    ).pack(pady=0)

def seleccionar_algoritmo(app):
    label_font_size = 14

    busquedas_frame = tkinter.Frame(app, bg="white", pady=20)
    busquedas_frame.pack(pady=10)
    busquedas_frame.option_add("*TCombobox*Listbox.font", ("Comic Sans MS", 10))
    
    tkinter.Label(
        busquedas_frame,
        text="Tipo de búsqueda:",
        font=("Comic Sans Ms", label_font_size),
        bg="white"
    ).pack()
    
    tipo_busqueda = ttk.Combobox(
        busquedas_frame,
        state="readonly",
        values=["Búsqueda no informada", "Búsqueda informada"],
        width=30
    )
    tipo_busqueda.pack(pady=5)
    tipo_busqueda.set("Búsqueda no informada")

    tkinter.Label(
        busquedas_frame,
        text="Algoritmo de búsqueda:",
        font=("Comic Sans Ms", label_font_size),
        bg="white"
    ).pack()

    tipo_algoritmo = ttk.Combobox(
        busquedas_frame,
        state="readonly",
        width=30
    )
    tipo_algoritmo.pack(pady=5)

    # función para actualizar los algoritmos
    def actualizar_algoritmos(event=None):
        if tipo_busqueda.get() == "Búsqueda no informada":
            tipo_algoritmo["values"] = ["Amplitud", "Costo uniforme", "Profundidad evitando ciclos"]
            tipo_algoritmo.set("Amplitud")
        else:
            tipo_algoritmo["values"] = ["Avara", "A*"]
            tipo_algoritmo.set("Avara")

    # enlazar el cambio de selección
    tipo_busqueda.bind("<<ComboboxSelected>>", actualizar_algoritmos)

    # inicializar con valores por defecto
    actualizar_algoritmos()

    return busquedas_frame, tipo_algoritmo

def ejecutar_algoritmo(algoritmo):
    global reporte_texto, animando, mapa_recorrido
    
    # No ejecutar si ya hay una animación en curso
    if animando:
        messagebox.showwarning("Advertencia", "Ya hay una animación en curso. Espere a que termine.")
        return
    
    # Verificar que hay un mapa cargado
    if mapa_actual is None:
        messagebox.showerror("Error", "Debe cargar un mapa primero")
        return
    
    # Verificar que el mapa no haya sido recorrido
    if mapa_recorrido:
        messagebox.showwarning("Mapa ya recorrido", "Debe reiniciar el mapa antes de recorrerlo nuevamente.\nUse el botón 'REINICIAR MAPA'.")
        return

    datos = None
    
    if algoritmo == "Amplitud":
        try:
            datos = amplitud(mapa_original)
        except Exception as e:
            messagebox.showerror("Error", f"Error al ejecutar el algoritmo: {e}")
            return
    elif algoritmo == "Costo uniforme":
        try:
            datos = coste_uniforme(mapa_original)
        except Exception as e:
            messagebox.showerror("Error", f"Error al ejecutar el algoritmo: {e}")
            return
    elif algoritmo == "Profundidad evitando ciclos":
        try:
            datos = profundidad_sin_ciclos(mapa_original)
        except Exception as e:
            messagebox.showerror("Error", f"Error al ejecutar el algoritmo: {e}")
            return
    elif algoritmo == "Avara":
        try:
            datos = avara(mapa_original)
        except Exception as e:
            messagebox.showerror("Error", f"Error al ejecutar el algoritmo: {e}")
            return
    elif algoritmo == "A*":
        try:
            datos = a_estrella(mapa_original)
        except Exception as e:
            messagebox.showerror("Error", f"Error al ejecutar el algoritmo: {e}")
            return
    else:
        messagebox.showerror("Error", "Algoritmo no reconocido")
        return

    if datos is None:
        messagebox.showerror("Error", "No se pudo ejecutar el algoritmo")
        return

    camino = datos["Camino"]
    nodos = datos["Reporte"]["Nodos expandidos"]
    profundidad = datos["Reporte"]["Profundidad"]
    costo = datos["Reporte"]["Costo"]
    tiempo = datos["Reporte"]["Tiempo"]

    # Actualizar el reporte
    reporte_texto.set(f"Nodos expandidos: {nodos}\n" + 
                      f"Profundidad del árbol: {profundidad}\n" +
                      f"Tiempo: {tiempo:.6f} segundos\n" +
                      f"Costo: {costo}\n" +
                      f"Pasos: {len(camino)-1}")
    
    # Siempre iniciar la animación del movimiento
    if camino and len(camino) > 0:
        animar_movimiento(camino, velocidad=500)  # Velocidad media
    else:
        messagebox.showwarning("Advertencia", "No se encontró un camino válido")

def btn_recorrer_mapa(app, texto, font_size, algoritmo):
    tkinter.Button(
        app,
        text=texto,
        anchor="center",
        font=("Comic Sans Ms", font_size, "bold"),
        bg="#0dd2e8",
        fg="black",
        pady=5,
        padx=10,
        width=24,
        relief="raised",
        bd=3,
        command=lambda: ejecutar_algoritmo(algoritmo.get())
    ).pack(pady=5)

def btn_cargar_mapa(app, texto, font_size):
    tkinter.Button(
        app,
        text=texto,
        anchor="center",
        font=("Comic Sans Ms", font_size, "bold"),
        bg="#e8c00d",
        fg="black",
        pady=5,
        padx=10,
        width=24,
        relief="raised",
        bd=3,
        command=cargar_mapa
    ).pack(pady=5)

def btn_detener_animacion(app, texto, font_size):
    def detener_animacion():
        global animando
        animando = False
        messagebox.showinfo("Información", "Animación detenida")
    
    tkinter.Button(
        app,
        text=texto,
        anchor="center",
        font=("Comic Sans Ms", font_size, "bold"),
        bg="#e85a0d",
        fg="black",
        pady=5,
        padx=10,
        width=24,
        relief="raised",
        bd=3,
        command=detener_animacion
    ).pack(pady=5)

def btn_reiniciar_mapa(app, texto, font_size):
    def reiniciar_mapa():
        global mapa_visual, mapa_original, animando, tiene_nave, posicion_astronauta_original, combustible_restante, mapa_recorrido, posicion_nave_abandonada
        
        # Detener cualquier animación
        animando = False
        
        if mapa_original is None:
            messagebox.showwarning("Advertencia", "No hay mapa cargado para reiniciar")
            return
        
        # Restaurar el mapa al estado original
        mapa_visual = mapa_original.copy()
        tiene_nave = False
        combustible_restante = 0
        mapa_recorrido = False  # Permitir recorrer el mapa nuevamente
        posicion_nave_abandonada = None  # Limpiar la posición de nave abandonada
        
        # Redibujar la matriz completa
        if recuadro_matriz is not None:
            for widget in recuadro_matriz.winfo_children():
                widget.destroy()
            
            # Calcular tamaños de celdas
            filas, columnas = len(mapa_visual), len(mapa_visual[0])
            ancho_celda = 600 // columnas
            alto_celda = 600 // filas

            # Redibujar todas las celdas
            for x in range(filas):
                for y in range(columnas):
                    valor = mapa_visual[x][y]
                    celda = tkinter.Label(recuadro_matriz, borderwidth=1, relief="solid")
                    
                    if valor in iconos and iconos[valor]:
                        img_resized = iconos[valor].resize((ancho_celda-2, alto_celda-2), Image.Resampling.LANCZOS)
                        tk_img = ImageTk.PhotoImage(img_resized)
                        celda.config(image=tk_img)
                        celda.image = tk_img
                    else:
                        celda.config(text=str(valor))

                    celda.grid(row=x, column=y, sticky="nsew")
        
        
    
    tkinter.Button(
        app,
        text=texto,
        anchor="center",
        font=("Comic Sans Ms", font_size, "bold"),
        bg="#0de86f",
        fg="black",
        pady=5,
        padx=10,
        width=24,
        relief="raised",
        bd=3,
        command=reiniciar_mapa
    ).pack(pady=5)

def dibujar_acciones(app):
    acciones = tkinter.Frame(app, bg="white", highlightbackground="black", highlightthickness=3,
                             width=320, height=603)
    acciones.place(x=690, y=52)
    acciones.pack_propagate(False)

    ver_reporte(acciones)    
    _, algoritmo = seleccionar_algoritmo(acciones)
    btn_recorrer_mapa(acciones, "RECORRER EL MAPA", 9, algoritmo)
    btn_detener_animacion(acciones, "DETENER ANIMACIÓN", 9)
    btn_reiniciar_mapa(acciones, "REINICIAR MAPA", 9)
    btn_cargar_mapa(acciones, "CARGAR NUEVO MAPA", 9)

    return acciones
        
def actualizar_pantalla():
    global mapa_visual
    # eliminar widgets viejos
    for widget in app.winfo_children():
        widget.destroy()
    
    cargar_fondo(app, "assets/secondary-background.png")
    
    # Usar mapa_visual si está disponible, sino mapa_actual
    mapa_a_mostrar = mapa_visual if mapa_visual is not None else mapa_actual
    if mapa_a_mostrar is not None:
        dibujar_matriz(app, mapa_a_mostrar)
        dibujar_acciones(app)
    
    botones_musica(app)
    
# ----------------- INICIAR LA APP Y CONFIGURACION -----------------

app = tkinter.Tk()
app.title("Smart Astronaut")
app.resizable(0, 0)

# ----------------- REPRODUCCION DE MUSICA DE FONDO ----------------

def detener():
    pygame.mixer.music.stop()

def reproducir():
    pygame.mixer.music.load("assets/Hangar-18.mp3")
    pygame.mixer.music.set_volume(0.2)
    pygame.mixer.music.play()

def botones_musica(app):
    btn_play = tkinter.Button(app, text="🔊", command=reproducir, font=("Comic Sans Ms", 13), width=3)
    btn_play.place(relx=0.9, rely=0.01)

    btn_stop = tkinter.Button(app, text="🔇", command=detener, font=("Comic Sans Ms", 13),width=3)
    btn_stop.place(relx=0.95, rely=0.01)

# --------------------- DIMENSIONES Y CENTRADO ---------------------

app.withdraw()
app.update_idletasks()

ancho_pantalla = app.winfo_screenwidth()
alto_pantalla = app.winfo_screenheight()

ancho_app = 1070
alto_app = 700

centrar_x = (ancho_pantalla - ancho_app) // 2
centrar_y = (alto_pantalla - alto_app) // 2 - 30

app.geometry(f"{ancho_app}x{alto_app}+{centrar_x}+{centrar_y}")
app.deiconify()

# ------------------------- ICONO DE LA APP ------------------------

try:
    # Cargar el ícono de la aplicación
    icono = tkinter.PhotoImage(file="assets/icono.png")

    # Establecer el ícono de la ventana
    app.iconphoto(True, icono)
except Exception as e:
    print("No se pudo cargar el ícono:", e)

# ------------------------ IMAGEN DE FONDO -------------------------

cargar_fondo(app, "assets/main-background.png")

# ------------------------------------------------------------------

frame_principal = tkinter.Frame(app, bg="", bd=0)
frame_principal.place(relx=0.5, rely=0.9, anchor="center")

pygame.mixer.init()
reproducir()
botones_musica(app)

btn_cargar_mapa(frame_principal, "CARGAR MAPA", 16)

app.mainloop()
