import socket
import tkinter as tk
from tkinter import scrolledtext
import threading

class SocketApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Socket Chat")

        self.connection_type_label = tk.Label(self.root, text="Connection Type:")
        self.connection_type_label.pack(pady=5)

        self.connection_type_var = tk.StringVar()
        self.connection_type_var.set("Server")

        self.server_radio = tk.Radiobutton(self.root, text="Server", variable=self.connection_type_var, value="Server")
        self.server_radio.pack(anchor=tk.W)
        self.client_radio = tk.Radiobutton(self.root, text="Client", variable=self.connection_type_var, value="Client")
        self.client_radio.pack(anchor=tk.W)

        self.ip_label = tk.Label(self.root, text="Enter IP Address:")
        self.ip_label.pack(pady=5)

        self.ip_entry = tk.Entry(self.root)
        self.ip_entry.pack(pady=5)

        self.text_area = scrolledtext.ScrolledText(self.root, wrap=tk.WORD, width=40, height=10)
        self.text_area.pack(padx=10, pady=10)

        self.message_entry = tk.Entry(self.root)
        self.message_entry.pack(pady=10)

        self.send_button = tk.Button(self.root, text="Send", command=self.send_message)
        self.send_button.pack(pady=5)

        self.start_button = tk.Button(self.root, text="Start", command=self.start_connection)
        self.start_button.pack(pady=10)

        self.clients = []

    def start_connection(self):
        connection_type = self.connection_type_var.get()
        ip_address = self.ip_entry.get()

        if connection_type == "Server":
            threading.Thread(target=self.start_server, args=(ip_address,), daemon=True).start()
        elif connection_type == "Client":
            threading.Thread(target=self.start_client, args=(ip_address,), daemon=True).start()

    def start_server(self, host):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            server_socket.bind((host, 65433))
            server_socket.listen()
            self.text_area.insert(tk.END, f"Server listening on {host}:65433\n")

            while True:
                conn, addr = server_socket.accept()
                self.clients.append(conn)
                threading.Thread(target=self.handle_client, args=(conn, addr), daemon=True).start()

    def handle_client(self, client_socket, addr):
        with client_socket:
            self.text_area.insert(tk.END, f"Connected by {addr}\n")
            while True:
                try:
                    data = client_socket.recv(1024)
                    if not data:
                        self.text_area.insert(tk.END, f"Client {addr} disconnected\n")
                        self.clients.remove(client_socket)
                        break
                    self.text_area.insert(tk.END, f"Client {addr}: {data.decode('utf-8')}\n")
                except Exception as e:
                    self.text_area.insert(tk.END, f"Error on server: {e}\n")
                    self.clients.remove(client_socket)
                    break

    def start_client(self, host):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            try:
                client_socket.connect((host, 65433))
                self.text_area.insert(tk.END, f"Connected to {host}:65433\n")
                while True:
                    message = self.message_entry.get()
                    if message:
                        client_socket.sendall(message.encode('utf-8'))
                        self.text_area.insert(tk.END, f"You: {message}\n")
                        self.message_entry.delete(0, tk.END)

                        # Receive and display the response from the server
                        data = client_socket.recv(1024)
                        if not data:
                            self.text_area.insert(tk.END, "Server disconnected\n")
                            break
                        self.text_area.insert(tk.END, f"Server: {data.decode('utf-8')}\n")

            except Exception as e:
                self.text_area.insert(tk.END, f"Error on client: {e}\n")

    def send_message(self):
        message = self.message_entry.get()
        if message:
            self.text_area.insert(tk.END, f"You: {message}\n")
            if self.connection_type_var.get() == "Server":
                self.broadcast(f"Server: {message}\n", None)
            elif self.connection_type_var.get() == "Client":
                self.clients[0].sendall(message.encode('utf-8'))
            self.message_entry.delete(0, tk.END)

    def broadcast(self, message, sender_socket):
        for client_socket in self.clients:
            if client_socket != sender_socket:
                try:
                    client_socket.sendall(message.encode('utf-8'))
                except Exception as e:
                    self.text_area.insert(tk.END, f"Error broadcasting to a client: {e}\n")

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = SocketApp()
    app.run()
