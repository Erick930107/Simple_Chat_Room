import socket
import threading
import tkinter as tk
from tkinter import simpledialog, Menu
from tkinter import *

BROADCAST_PORT = 5678
TCP_PORT = 1234
SERVER_IP = '127.0.0.1'

class ClientApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Chat Client")

        self.labelBottom = Label(self.master, bg="#959595", height=80) 
        self.labelBottom.place(relwidth=1, rely=0.825)

        self.text_area = tk.Text(self.master, state='disabled', bg='#23272A', fg='#999999', insertbackground='white')
        self.text_area.pack(fill=tk.BOTH, expand=True)
        
        self.entry_frame = tk.Frame(self.master, bg='#2C2F33')
        self.entry_frame.pack(fill=tk.X, padx=10, pady=10)

        self.entry = tk.Entry(self.entry_frame, bg='#2C2F33', fg='#cccccc', insertbackground='gray')
        self.entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        self.entry.bind("<Return>", self.send_message)
        self.entry.bind("<Key>", self.typing)

        self.send_button = tk.Button(self.entry_frame, text="Send", command=self.send_message, bg='#858585', fg='#FFFFFF')
        self.send_button.pack(side=tk.RIGHT)

        self.nickname = simpledialog.askstring("Nickname", "Please enter your nickname:", parent=self.master)

        self.master.title(f"{self.nickname}")
        
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect((SERVER_IP, TCP_PORT))
        self.client.send(self.nickname.encode('utf-8'))

        self.listener_thread = threading.Thread(target=self.listen_for_messages)
        self.listener_thread.start()
        
        self.typing_event = threading.Event()

        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.udp_socket.bind(('0.0.0.0', BROADCAST_PORT))
        self.udp_listener_thread = threading.Thread(target=self.receive_broadcast)
        self.udp_listener_thread.start()

        self.right_click_menu = Menu(self.master, tearoff=0)
        self.right_click_menu.add_command(label="Reply", command=self.reply_to_message)

        self.text_area.bind("<Button-3>", self.show_right_click_menu)
        self.reply_message = None

    def send_message(self, event=None):
        msg = self.entry.get()
        if msg:
            if self.reply_message:
                reply_text = f"\nReplying to {self.reply_message['nickname']}: {self.reply_message['message']}"
                full_msg = f"{self.nickname}: {msg}{reply_text}"
                self.reply_message = None
            else:
                full_msg = f"{self.nickname}: {msg}"
            self.client.send(full_msg.encode('utf-8'))
            self.entry.delete(0, tk.END)
            self.typing_event.clear()
            self.client.send(f"{self.nickname} stopped typing".encode('utf-8'))

    def typing(self, event=None):
        if not self.typing_event.is_set():
            self.typing_event.set()
            self.client.send(f"{self.nickname} is typing...".encode('utf-8'))
            self.master.after(2000, self.stop_typing)

    def stop_typing(self):
        self.typing_event.clear()
        self.client.send(f"{self.nickname} stopped typing".encode('utf-8'))

    def listen_for_messages(self):
        while True:
            try:
                msg = self.client.recv(1024).decode('utf-8')
                if "is typing..." in msg:
                    if not msg.startswith(self.nickname):
                        self.show_typing_message(msg)
                elif "stopped typing" in msg:
                    self.remove_typing_message(msg)
                else:
                    self.display_message(msg)
            except:
                break

    def receive_broadcast(self):
        while True:
            try:
                msg, _ = self.udp_socket.recvfrom(1024)
                msg = msg.decode('utf-8')
                if "is typing..." in msg:
                    if not msg.startswith(self.nickname):
                        self.show_typing_message(msg)
                elif "stopped typing" in msg:
                    self.remove_typing_message(msg)
                else:
                    self.display_message(msg)
            except:
                break

    def show_typing_message(self, msg):
        self.text_area.config(state='normal')
        self.text_area.insert(tk.END, msg + '\n')
        self.text_area.config(state='disabled')
        self.text_area.yview(tk.END)

    def remove_typing_message(self, msg):
        nickname = msg.split()[0]
        start_idx = "1.0"
        end_idx = tk.END
        self.text_area.config(state='normal')
        while True:
            pos = self.text_area.search(f"{nickname} is typing...", start_idx, stopindex=end_idx)
            if not pos:
                break
            line_end = f"{pos.split('.')[0]}.end"
            self.text_area.delete(pos, line_end)
            start_idx = pos
        self.text_area.config(state='disabled')

    def display_message(self, msg):
        self.text_area.config(state='normal')
        if "\nReplying to" in msg:
            parts = msg.split('\nReplying to ')
            main_msg = parts[0]
            reply_msg = parts[1]
            if main_msg.startswith(self.nickname):
                self.text_area.tag_configure('right', justify='right')
                self.text_area.insert(tk.END, main_msg + '\n', 'right')
                self.text_area.insert(tk.END, "  " + reply_msg + '\n', 'reply')
            else:
                self.text_area.tag_configure('left', justify='left')
                self.text_area.insert(tk.END, main_msg + '\n', 'left')
                self.text_area.insert(tk.END, "  " + reply_msg + '\n', 'reply')
        else:
            if msg.startswith(self.nickname):
                self.text_area.tag_configure('right', justify='right')
                self.text_area.insert(tk.END, msg + '\n', 'right')
            else:
                self.text_area.tag_configure('left', justify='left')
                self.text_area.insert(tk.END, msg + '\n', 'left')
        self.text_area.config(state='disabled')
        self.text_area.yview(tk.END)

    def show_right_click_menu(self, event):
        try:
            if self.text_area.tag_ranges("sel"):
                self.right_click_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.right_click_menu.grab_release()

    def reply_to_message(self):
        try:
            selected_text = self.text_area.selection_get()
            nickname = selected_text.split(":")[0]
            message = ": ".join(selected_text.split(":")[1:]).strip()
            self.entry.delete(0, tk.END)
            self.entry.insert(0, f"Replying to {nickname}: {message} ")
        except tk.TclError:
            pass

if __name__ == "__main__":
    root = tk.Tk()
    app = ClientApp(root)
    root.mainloop()
