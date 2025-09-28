import tkinter
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import numpy as np

mapa_actual = None
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
    global mapa_actual
    
    # Abrir ventana para seleccionar un archivo
    file_path = filedialog.askopenfilename(
        title="Seleccionar archivo de mapa",
        filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
    )
    
    if file_path:  # Si efectivamente se seleccionó un archivo
        try:
            # Cargar el archivo directamente como array usando numpy
            mapa_actual = np.loadtxt(file_path, dtype=int)
            actualizar_pantalla()
            return mapa_actual
            
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar el archivo: {e}")
            mapa_actual = None
            return None
        
def dibujar_matriz(app, mapa):
    # Crear frame contenedor con tamaño fijo
    recuadro = tkinter.Frame(app, bg="white", highlightbackground="black", highlightthickness=2,
                             width=600, height=600)
    recuadro.place(x=40, y=45)
    recuadro.pack_propagate(False)

    # Calcular tamaños de celdas
    filas, columnas = len(mapa), len(mapa[0])
    ancho_celda = 600 // columnas
    alto_celda = 600 // filas

    # Dibujar celdas
    for x in range(filas):
        for y in range(columnas):
            valor = mapa[x][y]
            celda = tkinter.Label(recuadro, borderwidth=1, relief="solid")
            
            if valor in iconos and iconos[valor]:
                img_resized = iconos[valor].resize((ancho_celda-2, alto_celda-2), Image.Resampling.LANCZOS)
                tk_img = ImageTk.PhotoImage(img_resized)
                celda.config(image=tk_img)
                celda.image = tk_img
            else:
                celda.config(text=str(valor))

            celda.grid(row=x, column=y, sticky="nsew")

    return recuadro
        
def actualizar_pantalla():
    # eliminar widgets viejos
    for widget in app.winfo_children():
        widget.destroy()
    
    cargar_fondo(app, "assets/secondary-background.png")
    dibujar_matriz(app, mapa_actual)

# ----------------- INICIAR LA APP Y CONFIGURACION -----------------

app = tkinter.Tk()

app.title("Smart Astronaut")
app.resizable(0, 0)

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

# Frame principal para contener los widgets sobre el fondo
frame_principal = tkinter.Frame(app, bg="", bd=0)
frame_principal.place(relx=0.5, rely=0.9, anchor="center")

tkinter.Button(
    frame_principal,
    text="CARGAR MAPA",
    anchor="center",
    font=("Comic Sans Ms", 16, "bold"),
    bg="#e8c00d",
    fg="black",
    pady=10,
    padx=20,
    relief="raised",
    bd=3,
    command=cargar_mapa
).pack(pady=20)

app.mainloop()
