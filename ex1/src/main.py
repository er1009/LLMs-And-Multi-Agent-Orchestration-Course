"""Main application entry point for Ollama Chat."""

import tkinter as tk
import threading
from src.api.ollama_client import OllamaClient
from src.gui.chat_window import ChatWindow


class ChatApplication:
    """Main application controller."""
    
    def __init__(self):
        """Initialize the chat application."""
        self.root = tk.Tk()
        self.client = OllamaClient()
        self.chat_window = ChatWindow(self.root)
        
        # Application state
        self.current_model: str = ""
        self.conversation_history: list = []
        
        # Setup callbacks
        self.chat_window.on_send_message = self._handle_send_message
        self.chat_window.on_model_change = self._handle_model_change
        
        # Initialize
        self._initialize_application()
    
    def _initialize_application(self):
        """Initialize application on startup."""
        # Check connection and load models in background
        thread = threading.Thread(target=self._load_models, daemon=True)
        thread.start()
    
    def _load_models(self):
        """Load available models from Ollama."""
        if self.client.check_connection():
            models = self.client.list_models()
            if models:
                self.root.after(0, lambda: self.chat_window.set_models(models))
                self.root.after(0, lambda: self.chat_window.set_status(True))
                self.current_model = models[0]
            else:
                self.root.after(0, lambda: self.chat_window.set_status(False))
                self.root.after(0, lambda: self.chat_window.add_message(
                    "system", "No models found. Please install a model: ollama pull tinyllama"
                ))
        else:
            self.root.after(0, lambda: self.chat_window.set_status(False))
            self.root.after(0, lambda: self.chat_window.show_error(
                "Connection Error",
                "Cannot connect to Ollama. Please ensure Ollama is running."
            ))
    
    def _handle_model_change(self, model: str):
        """Handle model selection change.
        
        Args:
            model: Selected model name
        """
        self.current_model = model
        self.conversation_history = []
        self.chat_window.add_message("system", f"Switched to model: {model}")
    
    def _handle_send_message(self, message: str):
        """Handle user message send.
        
        Args:
            message: User message text
        """
        if not self.current_model:
            self.chat_window.show_error(
                "No Model Selected",
                "Please select a model first."
            )
            return
        
        if not self.client.check_connection():
            self.chat_window.show_error(
                "Connection Error",
                "Cannot connect to Ollama. Please ensure Ollama is running."
            )
            return
        
        # Display user message
        self.chat_window.add_message("user", message)
        self.chat_window.set_loading(True)
        
        # Send message in background thread
        thread = threading.Thread(
            target=self._send_message_async,
            args=(message,),
            daemon=True
        )
        thread.start()
    
    def _send_message_async(self, message: str):
        """Send message to model asynchronously.
        
        Args:
            message: User message text
        """
        try:
            # Send message with current conversation history
            response = self.client.send_message(
                self.current_model,
                message,
                self.conversation_history
            )
            
            # Update conversation history (client already added user message, we add assistant response)
            self.conversation_history.append({"role": "user", "content": message})
            self.conversation_history.append({"role": "assistant", "content": response})
            
            # Update UI on main thread
            self.root.after(0, lambda: self.chat_window.add_message("assistant", response))
            self.root.after(0, lambda: self.chat_window.set_loading(False))
            
        except Exception as e:
            self.root.after(0, lambda: self.chat_window.set_loading(False))
            error_msg = str(e)
            self.root.after(0, lambda: self.chat_window.add_message(
                "system", f"Error: {error_msg}"
            ))
    
    def run(self):
        """Start the application."""
        self.root.mainloop()


def main():
    """Application entry point."""
    app = ChatApplication()
    app.run()


if __name__ == "__main__":
    main()

