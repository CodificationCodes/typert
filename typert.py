import tkinter as tk
from tkinter import scrolledtext, messagebox
import pyautogui
import threading
import time

class AutoTyperGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Auto Typer - Safe GUI Version")
        self.root.geometry("600x500")
        self.root.resizable(True, True)
        
        # Typing control variables
        self.is_typing = False
        self.typing_thread = None
        self.stop_typing_flag = False
        
        self.setup_ui()
        
    def setup_ui(self):
        # Main frame
        main_frame = tk.Frame(self.root, padx=10, pady=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Text input area
        tk.Label(main_frame, text="Text to Type:", font=("Arial", 10, "bold")).pack(anchor=tk.W, pady=(0, 5))
        
        self.text_area = scrolledtext.ScrolledText(main_frame, height=10, wrap=tk.WORD, font=("Arial", 10))
        self.text_area.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Insert default text
        default_text = """Enter Text Here..."""
        self.text_area.insert(tk.END, default_text)
        
        # Settings frame
        settings_frame = tk.LabelFrame(main_frame, text="Settings", padx=10, pady=10)
        settings_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Delay before start
        tk.Label(settings_frame, text="Delay before start (seconds):").grid(row=0, column=0, sticky=tk.W, padx=5)
        self.delay_var = tk.StringVar(value="5")
        tk.Entry(settings_frame, textvariable=self.delay_var, width=10).grid(row=0, column=1, padx=5)
        
        # Typing speed
        tk.Label(settings_frame, text="Seconds per character:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.speed_var = tk.StringVar(value="0.3")
        tk.Entry(settings_frame, textvariable=self.speed_var, width=10).grid(row=1, column=1, padx=5)
        
        # Control buttons frame
        control_frame = tk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=10)
        
        self.start_button = tk.Button(control_frame, text="Start Typing", command=self.start_typing, 
                                     bg="green", fg="white", font=("Arial", 10, "bold"), height=2)
        self.start_button.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        self.stop_button = tk.Button(control_frame, text="Stop Typing", command=self.stop_typing,
                                    bg="red", fg="white", font=("Arial", 10, "bold"), height=2, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        # Status bar
        self.status_label = tk.Label(main_frame, text="Ready", font=("Arial", 9), fg="blue")
        self.status_label.pack(fill=tk.X, pady=(5, 0))
        
        # Warning label
        warning_text = "⚠️ Click on the target text field within the delay period. Move mouse to cancel."
        self.warning_label = tk.Label(main_frame, text=warning_text, font=("Arial", 8), fg="orange")
        self.warning_label.pack(fill=tk.X, pady=(5, 0))
        
    def start_typing(self):
        if self.is_typing:
            return
            
        text = self.text_area.get("1.0", tk.END).strip()
        if not text:
            messagebox.showwarning("No Text", "Please enter some text to type.")
            return
            
        try:
            delay = float(self.delay_var.get())
            speed = float(self.speed_var.get())
            if speed < 0.01:
                messagebox.showwarning("Invalid Speed", "Speed must be at least 0.01 seconds per character.")
                return
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter valid numbers for delay and speed.")
            return
        
        # Disable controls during typing
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.text_area.config(state=tk.DISABLED)
        self.status_label.config(text=f"Starting in {delay} seconds...", fg="orange")
        self.stop_typing_flag = False
        self.is_typing = True
        
        # Start typing in a separate thread
        self.typing_thread = threading.Thread(target=self.perform_typing, args=(text, delay, speed))
        self.typing_thread.daemon = True
        self.typing_thread.start()
        
    def perform_typing(self, text, delay, speed):
        try:
            # Countdown
            for i in range(int(delay), 0, -1):
                if self.stop_typing_flag:
                    self.update_status("Cancelled", "blue")
                    return
                self.update_status(f"Starting in {i} seconds... Click target field!", "orange")
                time.sleep(1)
            
            if self.stop_typing_flag:
                self.update_status("Cancelled", "blue")
                return
                
            self.update_status("Typing in progress... Press Stop to cancel", "green")
            
            # Type the text with interval
            for i, char in enumerate(text):
                if self.stop_typing_flag:
                    self.update_status("Stopped by user", "red")
                    return
                pyautogui.write(char)
                time.sleep(speed)
                
                # Update status every 10 characters
                if i % 10 == 0:
                    self.update_status(f"Typing... {i+1}/{len(text)} characters", "green")
            
            self.update_status("✓ Typing completed successfully!", "blue")
            messagebox.showinfo("Complete", "Text has been typed successfully!")
            
        except Exception as e:
            self.update_status(f"Error: {str(e)}", "red")
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
        finally:
            self.typing_finished()
    
    def update_status(self, message, color):
        # Update status from any thread
        self.root.after(0, lambda: self.status_label.config(text=message, fg=color))
    
    def stop_typing(self):
        self.stop_typing_flag = True
        self.update_status("Stopping...", "orange")
        self.stop_button.config(state=tk.DISABLED)
        
    def typing_finished(self):
        self.is_typing = False
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.text_area.config(state=tk.NORMAL)
        
        if not self.stop_typing_flag:
            self.update_status("Ready", "blue")
        else:
            self.update_status("Stopped", "red")
            
    def on_closing(self):
        if self.is_typing:
            if messagebox.askokcancel("Quit", "Typing is in progress. Are you sure you want to quit?"):
                self.stop_typing_flag = True
                self.root.destroy()
        else:
            self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = AutoTyperGUI(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()