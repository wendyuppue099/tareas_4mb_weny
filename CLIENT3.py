import socket
import serial
import tkinter as tk
from tkinter import messagebox

arduino_baudrate = 9600

ser = serial.Serial()

umbral_distancia = 0.00000001

def actualizar_distancia(client_socket):
    try:
        ser.write(b'M')
        respuesta = ser.readline().decode().strip()
        distancia = ''.join(c for c in respuesta if c.isdigit() or c == '.')

        if distancia:
            etiqueta_distancia.config(text=f'Distancia: {distancia} cm')

            if float(distancia) < umbral_distancia:
                mensaje = f'¡Objeto detectado a {distancia} cm, por debajo del umbral de {umbral_distancia} cm!'
                etiqueta_mensaje.config(text=mensaje)
                # Envía un mensaje al cliente si se detecta un objeto
                client_socket.sendall(f'OBJETO:{distancia}'.encode())
            else:
                etiqueta_mensaje.config(text='')

        # Envía la distancia actualizada al cliente
        client_socket.sendall(f'Distancia:{distancia}'.encode())

    except serial.SerialException as e:
        etiqueta_distancia.config(text=f"Error: {str(e)}")

    ventana.after(300, lambda: actualizar_distancia(client_socket))

def aplicar_umbral(nuevo_umbral):
    global umbral_distancia
    try:
        umbral_distancia = float(nuevo_umbral)
        etiqueta_mensaje.config(text=f'Umbral de distancia actualizado a {umbral_distancia} cm')
    except ValueError:
        etiqueta_mensaje.config(text="Por favor, ingrese un valor numérico válido para el umbral")

def abrir_conexion_serial():
    puerto_com = entrada_puerto_com.get()
    try:
        ser.port = puerto_com
        ser.open()
        messagebox.showinfo("Información", f'Conexión serial abierta en {puerto_com}')
    except serial.SerialException as e:
        messagebox.showerror("Error", f'No se puede abrir la conexión serial en {puerto_com}\nError: {str(e)}')

def manejar_umbral_desde_cliente(nuevo_umbral):
    aplicar_umbral(nuevo_umbral)

# Configura el servidor
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(('192.168.64.210', 65433))
server_socket.listen(1)

print("Esperando conexiones...")

client_socket, client_address = server_socket.accept()
print(f"Conexión establecida con {client_address}")

# Crea la ventana
ventana = tk.Tk()
ventana.title("Medidor de Distancia - Servidor")
ventana.geometry("400x350")

etiqueta_puerto_com = tk.Label(ventana, text="Puerto COM:")
etiqueta_puerto_com.pack(pady=5)

entrada_puerto_com = tk.Entry(ventana)
entrada_puerto_com.pack(pady=5)

boton_abrir_conexion = tk.Button(ventana, text="Abrir Conexión", command=abrir_conexion_serial)
boton_abrir_conexion.pack(pady=5)

etiqueta_distancia = tk.Label(ventana, text="Distancia: -- cm", font=("Arial", 14))
etiqueta_distancia.pack(pady=20)

etiqueta_umbral = tk.Label(ventana, text="Umbral de Distancia:")
etiqueta_umbral.pack(pady=5)

entrada_umbral = tk.Entry(ventana)
entrada_umbral.pack(pady=5)

boton_aplicar_umbral = tk.Button(ventana, text="Aplicar Umbral", command=lambda: aplicar_umbral(entrada_umbral.get()))
boton_aplicar_umbral.pack(pady=5)

etiqueta_mensaje = tk.Label(ventana, text="", fg="red")
etiqueta_mensaje.pack(pady=10)

# Agrega un campo de entrada en el servidor para recibir el umbral desde el cliente
etiqueta_umbral_cliente = tk.Label(ventana, text="Umbral de Distancia desde Cliente:")
etiqueta_umbral_cliente.pack(pady=5)

entrada_umbral_cliente = tk.Entry(ventana)
entrada_umbral_cliente.pack(pady=5)

boton_aplicar_umbral_cliente = tk.Button(ventana, text="Aplicar Umbral desde Cliente", command=lambda: manejar_umbral_desde_cliente(entrada_umbral_cliente.get()))
boton_aplicar_umbral_cliente.pack(pady=5)

boton_aplicar = tk.Button(ventana, text="Aplicar", command=lambda: actualizar_distancia(client_socket))
boton_aplicar.pack(pady=10)

ventana.protocol("WM_DELETE_WINDOW", lambda: [ser.close(), ventana.destroy()])

ventana.after(300, lambda: actualizar_distancia(client_socket))

ventana.mainloop()