import tkinter
import customtkinter

customtkinter.set_appearance_mode("System")   #Modo de apariencia  (colores, estilos de botones) con el argumento "sistem"
customtkinter.set_default_color_theme("blue")  # Temas: azul (predeterminado), azul oscuro, verde
#app- aplicacion diseñanda para realizar una tarea especifica o un conjunto de tareas.
app = customtkinter.CTk()  #  crear una ventana CTk como lo haces con la ventana Tk
app.geometry("500x240")

def button_function():
    print("button pressed")

    

# Utilice CTkButton en lugar del botón tkinter
button = customtkinter.CTkButton(master=app, text="Auxilio Ingenierooos", command=button_function)
button.place(relx=0.5, rely=0.5, anchor=tkinter.CENTER)

app.mainloop()