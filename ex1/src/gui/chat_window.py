"""GUI chat window for the Ollama chat application."""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from typing import Callable, Optional


class ChatWindow:
    """Main chat window GUI component."""
    
    def __init__(self, root: tk.Tk):
        """Initialize chat window.
        
        Args:
            root: Tkinter root window
        """
        self.root = root
        self.root.title("Ollama Chat")
        self.root.geometry("800x600")
        
        self.on_send_message: Optional[Callable] = None
        self.on_model_change: Optional[Callable] = None
        
        self._create_widgets()
        self._setup_layout()
    
    def _create_widgets(self):
        """Create all GUI widgets."""
        # Top frame for model selection and status
        top_frame = ttk.Frame(self.root, padding="5")
        top_frame.pack(fill=tk.X)
        
        ttk.Label(top_frame, text="Model:").pack(side=tk.LEFT, padx=5)
        self.model_var = tk.StringVar()
        self.model_combo = ttk.Combobox(
            top_frame,
            textvariable=self.model_var,
            state="readonly",
            width=25
        )
        self.model_combo.pack(side=tk.LEFT, padx=5)
        self.model_combo.bind("<<ComboboxSelected>>", self._on_model_selected)
        
        self.status_label = ttk.Label(top_frame, text="●", foreground="red")
        self.status_label.pack(side=tk.RIGHT, padx=10)
        
        # Chat display area
        self.chat_display = scrolledtext.ScrolledText(
            self.root,
            wrap=tk.WORD,
            state=tk.DISABLED,
            font=("Arial", 11),
            bg="#f5f5f5",
            padx=10,
            pady=10
        )
        self.chat_display.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Input frame
        input_frame = ttk.Frame(self.root, padding="5")
        input_frame.pack(fill=tk.X)
        
        self.input_field = tk.Text(input_frame, height=2, font=("Arial", 11), wrap=tk.WORD)
        self.input_field.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        self.input_field.bind("<Return>", self._on_enter_key)
        self.input_field.bind("<Shift-Return>", lambda e: None)  # Allow Shift+Enter for newline
        
        self.send_button = ttk.Button(
            input_frame,
            text="Send",
            command=self._on_send_clicked,
            width=10
        )
        self.send_button.pack(side=tk.RIGHT, padx=5)
    
    def _setup_layout(self):
        """Configure widget layout and styling."""
        # Configure tags for message styling
        self.chat_display.tag_config("user", foreground="#0066cc", justify=tk.LEFT)
        self.chat_display.tag_config("assistant", foreground="#006600", justify=tk.LEFT)
        self.chat_display.tag_config("system", foreground="#666666", justify=tk.LEFT, font=("Arial", 10, "italic"))
    
    def _on_enter_key(self, event):
        """Handle Enter key press in input field."""
        if event.state == 0:  # No modifier keys
            self._on_send_clicked()
            return "break"
        return None
    
    def _on_send_clicked(self):
        """Handle send button click."""
        message = self.input_field.get("1.0", tk.END).strip()
        if message and self.on_send_message:
            self.input_field.delete("1.0", tk.END)
            self.on_send_message(message)
    
    def _on_model_selected(self, event=None):
        """Handle model selection change."""
        if self.on_model_change:
            self.on_model_change(self.model_var.get())
    
    def set_models(self, models: list):
        """Set available models in dropdown.
        
        Args:
            models: List of model names
        """
        self.model_combo['values'] = models
        if models:
            self.model_var.set(models[0])
    
    def set_status(self, connected: bool):
        """Update connection status indicator.
        
        Args:
            connected: True if connected, False otherwise
        """
        if connected:
            self.status_label.config(text="● Connected", foreground="green")
        else:
            self.status_label.config(text="● Disconnected", foreground="red")
    
    def add_message(self, sender: str, message: str):
        """Add a message to the chat display.
        
        Args:
            sender: Message sender ("user" or "assistant")
            message: Message text
        """
        self.chat_display.config(state=tk.NORMAL)
        tag = sender if sender in ["user", "assistant"] else "system"
        
        if sender == "system":
            prefix = ""
            suffix = "\n"
        else:
            prefix = f"You: " if sender == "user" else f"Assistant: "
            suffix = "\n\n"
        
        self.chat_display.insert(tk.END, f"{prefix}{message}{suffix}", tag)
        self.chat_display.config(state=tk.DISABLED)
        self.chat_display.see(tk.END)
    
    def show_error(self, title: str, message: str):
        """Show error message dialog.
        
        Args:
            title: Error dialog title
            message: Error message text
        """
        messagebox.showerror(title, message)
    
    def set_loading(self, loading: bool):
        """Set loading state for send button.
        
        Args:
            loading: True if loading, False otherwise
        """
        if loading:
            self.send_button.config(state=tk.DISABLED, text="Sending...")
        else:
            self.send_button.config(state=tk.NORMAL, text="Send")

