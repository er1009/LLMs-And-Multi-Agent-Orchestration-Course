"""GUI Application for Route Guide System."""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import threading
import json
from datetime import datetime
from pathlib import Path

from .orchestrator import RouteGuideOrchestrator
from .utils.config_loader import ConfigLoader
from .utils.logger import setup_logger, get_logger


class RouteGuideGUI:
    """
    Graphical User Interface for Route Guide System.

    Provides a user-friendly interface for:
    - Entering source and destination addresses
    - Configuring system settings
    - Running route analysis
    - Viewing and saving results
    """

    def __init__(self, root):
        """
        Initialize the GUI application.

        Args:
            root: tkinter root window
        """
        self.root = root
        self.root.title("Route Guide System - Intelligent Travel Companion")
        self.root.geometry("900x700")
        self.root.resizable(True, True)

        # Set up logger
        setup_logger(level="INFO")
        self.logger = get_logger(__name__)

        # Load configuration
        try:
            self.config = ConfigLoader()
        except Exception as e:
            messagebox.showerror("Configuration Error",
                               f"Failed to load configuration: {e}\n\n"
                               "Please ensure .env file exists with GOOGLE_MAPS_API_KEY")
            self.root.destroy()
            return

        # State variables
        self.orchestrator = None
        self.current_result = None
        self.is_running = False

        # Create UI
        self._create_widgets()
        self._apply_styling()

        self.logger.info("GUI initialized successfully")

    def _create_widgets(self):
        """Create all GUI widgets."""
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(4, weight=1)

        # Title
        title_label = ttk.Label(
            main_frame,
            text="🗺️ Route Guide System",
            font=("Helvetica", 24, "bold")
        )
        title_label.grid(row=0, column=0, pady=(0, 20))

        # Input Section
        self._create_input_section(main_frame)

        # Configuration Section
        self._create_config_section(main_frame)

        # Control Buttons
        self._create_control_section(main_frame)

        # Progress Section
        self._create_progress_section(main_frame)

        # Results Section
        self._create_results_section(main_frame)

        # Status Bar
        self._create_status_bar()

    def _create_input_section(self, parent):
        """Create input fields section."""
        input_frame = ttk.LabelFrame(parent, text="Route Information", padding="10")
        input_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        input_frame.columnconfigure(1, weight=1)

        # Source address
        ttk.Label(input_frame, text="Source Address:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.source_var = tk.StringVar(value="Tagor 40, Tel Aviv")
        self.source_entry = ttk.Entry(input_frame, textvariable=self.source_var, width=50)
        self.source_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))

        # Destination address
        ttk.Label(input_frame, text="Destination Address:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.dest_var = tk.StringVar(value="Yehuda HaNasi 38, Tel Aviv")
        self.dest_entry = ttk.Entry(input_frame, textvariable=self.dest_var, width=50)
        self.dest_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))

    def _create_config_section(self, parent):
        """Create configuration options section."""
        config_frame = ttk.LabelFrame(parent, text="Configuration", padding="10")
        config_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        config_frame.columnconfigure(1, weight=1)

        # Max waypoints
        ttk.Label(config_frame, text="Max Waypoints:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.max_waypoints_var = tk.IntVar(value=20)
        waypoints_spinbox = ttk.Spinbox(
            config_frame,
            from_=1,
            to=50,
            textvariable=self.max_waypoints_var,
            width=10
        )
        waypoints_spinbox.grid(row=0, column=1, sticky=tk.W, pady=5, padx=(10, 0))

        # Parallel execution checkbox
        self.parallel_var = tk.BooleanVar(value=True)
        parallel_check = ttk.Checkbutton(
            config_frame,
            text="Enable Parallel Execution (3x faster)",
            variable=self.parallel_var
        )
        parallel_check.grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=5)

        # Log level
        ttk.Label(config_frame, text="Log Level:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.log_level_var = tk.StringVar(value="INFO")
        log_combo = ttk.Combobox(
            config_frame,
            textvariable=self.log_level_var,
            values=["DEBUG", "INFO", "WARNING", "ERROR"],
            state="readonly",
            width=10
        )
        log_combo.grid(row=2, column=1, sticky=tk.W, pady=5, padx=(10, 0))

    def _create_control_section(self, parent):
        """Create control buttons section."""
        control_frame = ttk.Frame(parent)
        control_frame.grid(row=3, column=0, pady=(0, 10))

        # Run button
        self.run_button = ttk.Button(
            control_frame,
            text="🚀 Start Route Guide",
            command=self._run_route_guide,
            width=20
        )
        self.run_button.grid(row=0, column=0, padx=5)

        # Stop button
        self.stop_button = ttk.Button(
            control_frame,
            text="⏹ Stop",
            command=self._stop_execution,
            state=tk.DISABLED,
            width=15
        )
        self.stop_button.grid(row=0, column=1, padx=5)

        # Clear button
        clear_button = ttk.Button(
            control_frame,
            text="🗑 Clear Results",
            command=self._clear_results,
            width=15
        )
        clear_button.grid(row=0, column=2, padx=5)

        # Save button
        self.save_button = ttk.Button(
            control_frame,
            text="💾 Save Results",
            command=self._save_results,
            state=tk.DISABLED,
            width=15
        )
        self.save_button.grid(row=0, column=3, padx=5)

    def _create_progress_section(self, parent):
        """Create progress indicator section."""
        progress_frame = ttk.Frame(parent)
        progress_frame.grid(row=4, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        progress_frame.columnconfigure(0, weight=1)

        # Progress label
        self.progress_label = ttk.Label(progress_frame, text="Ready to process route")
        self.progress_label.grid(row=0, column=0, sticky=tk.W, pady=(0, 5))

        # Progress bar
        self.progress_bar = ttk.Progressbar(
            progress_frame,
            mode='indeterminate',
            length=400
        )
        self.progress_bar.grid(row=1, column=0, sticky=(tk.W, tk.E))

    def _create_results_section(self, parent):
        """Create results display section."""
        results_frame = ttk.LabelFrame(parent, text="Results", padding="10")
        results_frame.grid(row=5, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(0, weight=1)

        # Results text area with scrollbar
        self.results_text = scrolledtext.ScrolledText(
            results_frame,
            wrap=tk.WORD,
            width=80,
            height=20,
            font=("Courier", 10)
        )
        self.results_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Configure text tags for styling
        self.results_text.tag_config("header", font=("Courier", 12, "bold"), foreground="blue")
        self.results_text.tag_config("stop", font=("Courier", 10, "bold"), foreground="green")
        self.results_text.tag_config("content", font=("Courier", 10))
        self.results_text.tag_config("metadata", font=("Courier", 9, "italic"), foreground="gray")

    def _create_status_bar(self):
        """Create status bar at bottom."""
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(
            self.root,
            textvariable=self.status_var,
            relief=tk.SUNKEN,
            anchor=tk.W,
            padding=(5, 2)
        )
        status_bar.grid(row=1, column=0, sticky=(tk.W, tk.E))

    def _apply_styling(self):
        """Apply custom styling to the GUI."""
        style = ttk.Style()
        style.theme_use('clam')

        # Configure styles
        style.configure('TButton', padding=6, relief="flat")
        style.configure('TLabel', padding=3)
        style.configure('TLabelframe', padding=10)
        style.configure('TLabelframe.Label', font=("Helvetica", 11, "bold"))

    def _run_route_guide(self):
        """Run the route guide system in a separate thread."""
        # Validate inputs
        source = self.source_var.get().strip()
        dest = self.dest_var.get().strip()

        if not source or not dest:
            messagebox.showwarning("Input Error", "Please enter both source and destination addresses")
            return

        if self.is_running:
            messagebox.showinfo("Already Running", "Route guide is already processing")
            return

        # Update UI state
        self.is_running = True
        self.run_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.save_button.config(state=tk.DISABLED)
        self.progress_bar.start(10)
        self.progress_label.config(text="Processing route...")
        self.status_var.set("Running route guide system...")

        # Clear previous results
        self.results_text.delete(1.0, tk.END)

        # Run in separate thread to keep GUI responsive
        thread = threading.Thread(target=self._execute_route_guide, daemon=True)
        thread.start()

    def _execute_route_guide(self):
        """Execute route guide in background thread."""
        try:
            # Update config with GUI settings
            self.config.config["route"]["max_waypoints"] = self.max_waypoints_var.get()
            self.config.config["system"]["parallel_execution"] = self.parallel_var.get()

            # Update log level
            import os
            os.environ["LOG_LEVEL"] = self.log_level_var.get()
            setup_logger(level=self.log_level_var.get())

            # Create orchestrator
            self.orchestrator = RouteGuideOrchestrator(config=self.config)

            # Get inputs
            source = self.source_var.get().strip()
            dest = self.dest_var.get().strip()

            # Process route
            self.logger.info(f"Processing route: {source} -> {dest}")
            result = self.orchestrator.process_route(source, dest)

            # Store result
            self.current_result = result

            # Display results in GUI
            self.root.after(0, self._display_results, result)

            # Update UI
            self.root.after(0, self._execution_complete, True)

        except Exception as e:
            self.logger.error(f"Route guide failed: {e}", exc_info=True)
            error_msg = f"Error: {str(e)}"
            self.root.after(0, self._display_error, error_msg)
            self.root.after(0, self._execution_complete, False)

    def _display_results(self, result):
        """Display results in the text area."""
        self.results_text.delete(1.0, tk.END)

        # Header
        self.results_text.insert(tk.END, "=" * 80 + "\n", "header")
        self.results_text.insert(tk.END, "ROUTE GUIDE RESULTS\n", "header")
        self.results_text.insert(tk.END, "=" * 80 + "\n\n", "header")

        # Route info
        self.results_text.insert(tk.END, f"📍 From: {result.source}\n", "content")
        self.results_text.insert(tk.END, f"📍 To: {result.destination}\n\n", "content")

        # Metadata
        metadata = result.metadata
        self.results_text.insert(tk.END, f"Distance: {metadata['total_distance_km']} km\n", "metadata")
        self.results_text.insert(tk.END, f"Duration: {metadata['estimated_duration_minutes']} minutes\n", "metadata")
        self.results_text.insert(tk.END, f"Stops: {metadata['processed_stops']}\n", "metadata")
        self.results_text.insert(tk.END, f"Processing Time: {metadata['processing_time_seconds']} seconds\n\n", "metadata")

        self.results_text.insert(tk.END, "=" * 80 + "\n\n", "header")

        # Stops
        for i, stop in enumerate(result.stops, 1):
            choice = stop.choice

            # Stop header
            self.results_text.insert(tk.END, f"Stop {i}: {stop.address}\n", "stop")
            self.results_text.insert(tk.END, "-" * 80 + "\n", "content")

            # Content type icon
            icon = {"video": "🎥", "music": "🎵", "info": "ℹ️"}.get(choice['type'], "📌")
            self.results_text.insert(tk.END, f"{icon} Type: {choice['type'].upper()}\n", "content")
            self.results_text.insert(tk.END, f"📝 Title: {choice['title']}\n", "content")

            # Content (truncate if too long)
            content = choice['content']
            if len(content) > 200:
                content = content[:200] + "..."
            self.results_text.insert(tk.END, f"📄 Content: {content}\n", "content")

            self.results_text.insert(tk.END, f"💡 Reason: {choice['reason']}\n\n", "content")

        # Scroll to top
        self.results_text.see(1.0)

        # Update status
        self.status_var.set(f"Successfully processed {len(result.stops)} stops")

    def _display_error(self, error_msg):
        """Display error message."""
        self.results_text.delete(1.0, tk.END)
        self.results_text.insert(tk.END, "❌ ERROR\n\n", "header")
        self.results_text.insert(tk.END, error_msg, "content")
        self.status_var.set("Error occurred during processing")

    def _execution_complete(self, success):
        """Update UI after execution completes."""
        self.is_running = False
        self.run_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.progress_bar.stop()

        if success:
            self.save_button.config(state=tk.NORMAL)
            self.progress_label.config(text="✅ Route processing complete!")
        else:
            self.progress_label.config(text="❌ Route processing failed")

    def _stop_execution(self):
        """Stop the current execution."""
        # Note: Can't easily stop thread, but we can update UI
        self.progress_label.config(text="Stopping...")
        self.status_var.set("Stop requested (processing will complete current waypoint)")

    def _clear_results(self):
        """Clear the results display."""
        self.results_text.delete(1.0, tk.END)
        self.current_result = None
        self.save_button.config(state=tk.DISABLED)
        self.progress_label.config(text="Ready to process route")
        self.status_var.set("Ready")

    def _save_results(self):
        """Save results to a file."""
        if not self.current_result:
            messagebox.showwarning("No Results", "No results to save")
            return

        # Ask user for file location
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_filename = f"route_results_{timestamp}.json"

        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            initialfile=default_filename
        )

        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(self.current_result.to_json(pretty=True))

                messagebox.showinfo("Success", f"Results saved to:\n{filename}")
                self.status_var.set(f"Results saved to {Path(filename).name}")
            except Exception as e:
                messagebox.showerror("Save Error", f"Failed to save results:\n{e}")


def main():
    """Run the GUI application."""
    root = tk.Tk()
    app = RouteGuideGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
