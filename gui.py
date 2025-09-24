import tkinter

app = tkinter.Tk()

app.title("Smart Astronaut")
app.resizable(0, 0)

# --------------------- DIMENSIONES Y CENTRADO ---------------------

app.withdraw()
app.update_idletasks()

ancho_pantalla = app.winfo_screenwidth()
alto_pantalla = app.winfo_screenheight()

ancho_app = 800
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

try:
    # Cargar la imagen de fondo
    imagen_fondo = tkinter.PhotoImage(file="assets/main-background.png")
    
    # Crear un label para mostrar la imagen de fondo
    label_fondo = tkinter.Label(app, image=imagen_fondo)
    label_fondo.place(x=0, y=0, relwidth=1, relheight=1)
    
    # Importante: mantener una referencia de la imagen
    app.imagen_fondo = imagen_fondo
    
except Exception as e:
    print("No se pudo cargar la imagen de fondo:", e)
    # Si no se puede cargar la imagen, usar un color de fondo
    app.configure(bg="#1a1a2e")

# ------------------------------------------------------------------

# Frame principal para contener los widgets sobre el fondo
frame_principal = tkinter.Frame(app, bg="", bd=0)
frame_principal.place(relx=0.5, rely=0.5, anchor="center")

tkinter.Button(
    frame_principal,
    text="Iniciar Simulación",
    anchor="center",
    font=("Arial", 14, "bold"),
    bg="#16213e",
    fg="white",
    pady=10,
    padx=20,
    relief="raised",
    bd=3
).pack(pady=20)

app.mainloop()
