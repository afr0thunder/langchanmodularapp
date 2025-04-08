import tkinter as tk
from tkinter import ttk, scrolledtext

class ChatInterface:
    def __init__(self, master, agent_manager):
        self.master = master
        self.master.title("LangChain Modular AI Chat App")

        self.agent_manager = agent_manager
        self.agent_names = self.agent_manager.list_agents()
        self.chat_handlers = {}

        self._build_widgets()
        self._set_active_agent(self.agent_names[0])

    def _build_widgets(self):
        # Agent selector
        self.agent_var = tk.StringVar()
        self.agent_dropdown = ttk.Combobox(self.master, textvariable=self.agent_var, values=self.agent_names)
        self.agent_dropdown.bind("<<ComboboxSelected>>", self._on_agent_change)
        self.agent_dropdown.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        # Clear chat button
        self.clear_btn = ttk.Button(self.master, text="Clear Chat", command=self._clear_chat)
        self.clear_btn.grid(row=0, column=1, padx=10, pady=10)

        # Chat display
        self.chat_display = scrolledtext.ScrolledText(self.master, state='disabled', wrap='word', width=80, height=20)
        self.chat_display.grid(row=1, column=0, columnspan=2, padx=10, pady=10)

        # User input
        self.user_input = tk.Entry(self.master, width=70)
        self.user_input.grid(row=2, column=0, padx=10, pady=10, sticky="ew")
        self.user_input.bind("<Return>", lambda event: self._send_message())

        # Send button
        self.send_btn = ttk.Button(self.master, text="Send", command=self._send_message)
        self.send_btn.grid(row=2, column=1, padx=10, pady=10)

    def _set_active_agent(self, agent_name):
        self.agent_var.set(agent_name)
        agent = self.agent_manager.get_agent(agent_name)

        if agent_name not in self.chat_handlers:
            from chat.chat_handler import ChatHandler
            self.chat_handlers[agent_name] = ChatHandler(agent)

        self.handler = self.chat_handlers[agent_name]
        self._refresh_display()

    def _on_agent_change(self, event):
        self._set_active_agent(self.agent_var.get())

    def _refresh_display(self):
        self.chat_display.config(state='normal')
        self.chat_display.delete(1.0, tk.END)
        for msg in self.handler.get_history():
            self.chat_display.insert(tk.END, f"[{msg['timestamp']}] {msg['role'].capitalize()}: {msg['content']}\n\n")
        self.chat_display.config(state='disabled')
        self.chat_display.yview(tk.END)

    def _send_message(self):
        user_input = self.user_input.get().strip()
        if user_input:
            response = self.handler.send_message(user_input)
            self.user_input.delete(0, tk.END)
            self._refresh_display()

    def _clear_chat(self):
        self.handler.clear_history()
        self._refresh_display()


def launch_interface(agent_manager):
    root = tk.Tk()
    app = ChatInterface(root, agent_manager)
    root.mainloop()