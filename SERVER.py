import socket
import serial
import tkinter as tk
from tkinter import messagebox

# Velocidad de baudios para la comunicación con Arduino
arduino_baudrate = 9600

# Objeto Serial para la comunicación con Arduino
ser = serial.Serial()

# Umbral de distancia para la detección de objetos
umbral_distancia = 0.00000001

# Función para actualizar la distancia y enviar información al cliente
def actualizar_distancia(client_socket):
    try:
        # Envia el comando 'M' a Arduino y lee la respuesta para obtener la distancia
        ser.write(b'M')
        respuesta = ser.readline().decode().strip()
        distancia = ''.join(c for c in respuesta if c.isdigit() or c == '.')

        if distancia:
            # Actualiza la etiqueta en la GUI con la distancia
            etiqueta_distancia.config(text=f'Distancia: {distancia} cm')

            # Si la distancia es inferior al umbral, muestra un mensaje y envía una notificación al cliente
            if float(distancia) < umbral_distancia:
                mensaje = f'¡Objeto detectado a {distancia} cm, por debajo del umbral de {umbral_distancia} cm!'
                etiqueta_mensaje.config(text=mensaje)
                # Envía un mensaje al cliente si se detecta un objeto
                client_socket.sendall(f'Umbral:{distancia}'.encode())
            else:
                etiqueta_mensaje.config(text='')

        # Envía la distancia actualizada al cliente
        client_socket.sendall(f'Distancia:{distancia}'.encode())

    except serial.SerialException as e:
        # Maneja los errores de comunicación serial y muestra el mensaje de error en la GUI
        etiqueta_distancia.config(text=f"Error: {str(e)}")

    # Programa la función para que se llame nuevamente cada 300 milisegundos
    ventana.after(300, lambda: actualizar_distancia(client_socket))

# Función para aplicar un nuevo umbral de distancia
def aplicar_umbral(nuevo_umbral):
    global umbral_distancia
    try:
        # Actualiza el umbral con el nuevo valor
        umbral_distancia = float(nuevo_umbral)
        # Muestra un mensaje en la GUI indicando que el umbral se ha actualizado
        etiqueta_mensaje.config(text=f'Umbral de distancia actualizado a {umbral_distancia} cm')
    except ValueError:
        # Maneja errores si el valor ingresado no es numérico
        etiqueta_mensaje.config(text="Por favor, ingrese un valor numérico válido para el umbral")

# Función para abrir la conexión serial con el puerto especificado en la GUI
def abrir_conexion_serial():
    puerto_com = entrada_puerto_com.get()
    try:
        # Configura el puerto COM para la comunicación serial y abre la conexión
        ser.port = puerto_com
        ser.open()
        # Muestra un mensaje de información en la GUI si la conexión es exitosa
        messagebox.showinfo("Información", f'Conexión serial abierta en {puerto_com}')
    except serial.SerialException as e:
        # Muestra un mensaje de error en la GUI si no se puede abrir la conexión serial
        messagebox.showerror("Error", f'No se puede abrir la conexión serial en {puerto_com}\nError: {str(e)}')

# Función para manejar actualizaciones del umbral enviadas por el cliente
def manejar_umbral_desde_cliente(nuevo_umbral):
    aplicar_umbral(nuevo_umbral)

# Configuración del servidor
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(('192.168.68.71', 65433))
server_socket.listen(1)

print("Esperando conexiones...")

# Acepta una conexión cuando se recibe una solicitud
client_socket, client_address = server_socket.accept()
print(f"Conexión establecida con {client_address}")

# Crea la ventana Tkinter
ventana = tk.Tk()
ventana.title("Medidor de Distancia - Servidor")
ventana.geometry("400x350")

# Etiqueta y entrada para el puerto COM
etiqueta_puerto_com = tk.Label(ventana, text="Puerto COM:")
etiqueta_puerto_com.pack(pady=5)
entrada_puerto_com = tk.Entry(ventana)
entrada_puerto_com.pack(pady=5)

# Botón para abrir la conexión serial
boton_abrir_conexion = tk.Button(ventana, text="Abrir Conexión", command=abrir_conexion_serial)
boton_abrir_conexion.pack(pady=5)

# Etiqueta para mostrar la distancia
etiqueta_distancia = tk.Label(ventana, text="Distancia: -- cm", font=("Arial", 14))
etiqueta_distancia.pack(pady=20)

# Etiqueta y entrada para el umbral de distancia
etiqueta_umbral = tk.Label(ventana, text="Umbral de Distancia:")
etiqueta_umbral.pack(pady=5)
entrada_umbral = tk.Entry(ventana)
entrada_umbral.pack(pady=5)

# Botón para aplicar el umbral
boton_aplicar_umbral = tk.Button(ventana, text="Aplicar Umbral", command=lambda: aplicar_umbral(entrada_umbral.get()))
boton_aplicar_umbral.pack(pady=5)

# Etiqueta para mensajes de error
etiqueta_mensaje = tk.Label(ventana, text="", fg="red")
etiqueta_mensaje.pack(pady=10)

# Configura la acción al cerrar la ventana
ventana.protocol("WM_DELETE_WINDOW", lambda: [ser.close(), ventana.destroy()])

# Programa la función para que se ejecute cada 300 milisegundos
ventana.after(300, lambda: actualizar_distancia(client_socket))

# Inicia el bucle principal de Tkinter
ventana.mainloop()
