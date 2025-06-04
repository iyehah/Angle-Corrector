import tkinter as tk
from tkinter import messagebox, ttk
import re

def dms_to_seconds(degrees, minutes, seconds):
    """Convert degrees, minutes, seconds to total seconds."""
    return degrees * 3600 + minutes * 60 + seconds

def seconds_to_dms(seconds):
    """Convert total seconds to degrees, minutes, seconds."""
    seconds = round(seconds)
    degrees = seconds // 3600
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60
    return degrees, minutes, seconds

def calculate_expected_sum(sides):
    """Calculate expected sum of interior angles in degrees for an n-sided polygon."""
    return (sides - 2) * 180

def correct_angles(angles, sides):
    """Correct angles to sum to (n-2)*180 degrees."""
    angles_in_seconds = [dms_to_seconds(*angle) for angle in angles]
    total_seconds = sum(angles_in_seconds)
    expected_seconds = calculate_expected_sum(sides) * 3600
    error_seconds = total_seconds - expected_seconds
    
    if error_seconds != 0:
        total_weight = total_seconds
        corrections = [-(error_seconds * angle / total_weight) for angle in angles_in_seconds]
        corrected_seconds = [angle + correction for angle, correction in zip(angles_in_seconds, corrections)]
    else:
        corrected_seconds = angles_in_seconds
    
    corrected_angles = [seconds_to_dms(seconds) for seconds in corrected_seconds]
    return corrected_angles, error_seconds

def parse_dms(text):
    """Parse DMS string (e.g., '235:20:25' or '235 20 25') into (degrees, minutes, seconds)."""
    text = text.strip().replace(':', ' ')
    try:
        d, m, s = map(int, re.split(r'\s+', text))
        if d < 0 or m < 0 or s < 0 or m >= 60 or s >= 60:
            raise ValueError("Invalid DMS values")
        return d, m, s
    except ValueError:
        raise ValueError("Invalid DMS format")

class AngleCorrectorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Angle Corrector")
        self.root.geometry("800x600")
        self.root.configure(bg="#f0f4f8")
        self.root.resizable(True, True)
        self.root.iconbitmap("icon.ico") 
        # Styling
        self.style = ttk.Style()
        self.style.configure("TButton", font=("Arial", 10, "bold"), padding=10, foreground="#0056b3", background="#e0e7ff")
        self.style.map("TButton", background=[("active", "#c0d4ff")])
        self.style.configure("TLabel", font=("Arial", 11), background="#f0f4f8")
        self.style.configure("TEntry", font=("Arial", 10))
        self.style.configure("Treeview", font=("Arial", 10))
        self.style.configure("Treeview.Heading", font=("Arial", 10, "bold"))
        
        # Main container using grid
        self.main_frame = tk.Frame(root, bg="#f0f4f8")
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Left frame for inputs (grid layout)
        self.input_frame = tk.Frame(self.main_frame, bg="#f0f4f8")
        self.input_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        
        # Right frame for output
        self.output_frame = tk.Frame(self.main_frame, bg="#f0f4f8")
        self.output_frame.grid(row=0, column=1, sticky="nsew")
        
        # Configure grid weights
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(1, weight=2)
        self.main_frame.grid_rowconfigure(0, weight=1)
        
        # Input frame content
        tk.Label(self.input_frame, text="Angle Corrector", bg="#f0f4f8", font=("Arial", 14, "bold")).grid(row=0, column=0, columnspan=2, pady=10)
        tk.Label(self.input_frame, text="Enter Angles (e.g., 235:20:25 or 235 20 25):", bg="#f0f4f8", font=("Arial", 11, "italic")).grid(row=1, column=0, columnspan=2, pady=5)
        
        self.angle_entries = []
        self.angle_row = 2  # Start angle fields at row 2
        self.add_angle_field()  # Start with one field
        
        # Buttons
        ttk.Button(self.input_frame, text="Add Field", command=self.add_angle_field).grid(row=998, column=0, padx=5, pady=5, sticky="ew")
        ttk.Button(self.input_frame, text="Clear Fields", command=self.clear_fields).grid(row=998, column=1, padx=5, pady=5, sticky="ew")
        ttk.Button(self.input_frame, text="View Results", command=self.correct_angles).grid(row=999, column=0, columnspan=2, padx=5, pady=5, sticky="ew")
        
        # Output frame content
        tk.Label(self.output_frame, text="Results", bg="#f0f4f8", font=("Arial", 12, "bold")).pack(anchor="w", pady=10)
        
        # Raw angles table
        tk.Label(self.output_frame, text="Raw Angles:", bg="#f0f4f8", font=("Arial", 10, "bold")).pack(anchor="w")
        self.raw_table = ttk.Treeview(self.output_frame, columns=("Angle", "Degrees", "Minutes", "Seconds"), show="headings", height=5)
        self.raw_table.heading("Angle", text="Angle")
        self.raw_table.heading("Degrees", text="Degrees")
        self.raw_table.heading("Minutes", text="Minutes")
        self.raw_table.heading("Seconds", text="Seconds")
        self.raw_table.column("Angle", width=80, anchor="center")
        self.raw_table.column("Degrees", width=80, anchor="center")
        self.raw_table.column("Minutes", width=80, anchor="center")
        self.raw_table.column("Seconds", width=80, anchor="center")
        self.raw_table.pack(fill="x", padx=5, pady=5)
        
        # Error label
        self.error_label = tk.Label(self.output_frame, text="Error: 0 seconds", bg="#f0f4f8", font=("Arial", 10, "bold"))
        self.error_label.pack(anchor="w", pady=5)
        
        # Corrected angles table
        tk.Label(self.output_frame, text="Corrected Angles:", bg="#f0f4f8", font=("Arial", 10, "bold")).pack(anchor="w")
        self.corrected_table = ttk.Treeview(self.output_frame, columns=("Angle", "Degrees", "Minutes", "Seconds"), show="headings", height=5)
        self.corrected_table.heading("Angle", text="Angle")
        self.corrected_table.heading("Degrees", text="Degrees")
        self.corrected_table.heading("Minutes", text="Minutes")
        self.corrected_table.heading("Seconds", text="Seconds")
        self.corrected_table.column("Angle", width=80, anchor="center")
        self.corrected_table.column("Degrees", width=80, anchor="center")
        self.corrected_table.column("Minutes", width=80, anchor="center")
        self.corrected_table.column("Seconds", width=80, anchor="center")
        self.corrected_table.pack(fill="x", padx=5, pady=5)
        
        # Sum label
        self.sum_label = tk.Label(self.output_frame, text="Sum of Corrected Angles: 0° 0' 0\"", bg="#f0f4f8", font=("Arial", 10, "bold"))
        self.sum_label.pack(anchor="w", pady=5)
        
        # Status label
        self.status_label = tk.Label(self.output_frame, text="", bg="#f0f4f8", font=("Arial", 10))
        self.status_label.pack(anchor="w", pady=5)
    
    def add_angle_field(self):
        """Add a new angle input field in the grid."""
        index = len(self.angle_entries) + 1
        tk.Label(self.input_frame, text=f"Angle {index}:", bg="#f0f4f8", font=("Arial", 10)).grid(row=self.angle_row, column=0, padx=5, pady=2, sticky="w")
        entry = ttk.Entry(self.input_frame, width=20)
        entry.grid(row=self.angle_row, column=1, padx=5, pady=2)
        self.angle_entries.append((entry, f"Angle {index}"))
        self.angle_row += 1
    
    def clear_fields(self):
        """Clear all angle fields and reset to one field."""
        for entry, _ in self.angle_entries:
            entry.grid_forget()
            entry.destroy()
        for widget in self.input_frame.grid_slaves():
            if int(widget.grid_info()["row"]) >= 2 and int(widget.grid_info()["row"]) < 998:
                widget.grid_forget()
                widget.destroy()
        self.angle_entries.clear()
        self.angle_row = 2
        self.add_angle_field()
        self.clear_tables()
    
    def clear_tables(self):
        """Clear the raw and corrected angles tables and reset labels."""
        for item in self.raw_table.get_children():
            self.raw_table.delete(item)
        for item in self.corrected_table.get_children():
            self.corrected_table.delete(item)
        self.error_label.config(text="Error: 0 seconds")
        self.sum_label.config(text="Sum of Corrected Angles: 0° 0' 0\"")
        self.status_label.config(text="")
    
    def correct_angles(self):
        """Process and correct angles."""
        try:
            sides = len(self.angle_entries)
            if sides < 3:
                messagebox.showerror("Error", "Polygon must have at least 3 angles.")
                return
            
            angles = []
            for entry, label in self.angle_entries:
                text = entry.get().strip()
                if not text:
                    messagebox.showerror("Error", f"Missing input for {label}.")
                    return
                try:
                    angles.append(parse_dms(text))
                except ValueError:
                    messagebox.showerror("Error", f"Invalid format for {label}. Use 'D:M:S' or 'D M S' (e.g., 235:20:25).")
                    return
            
            corrected_angles, error_seconds = correct_angles(angles, sides)
            
            # Clear tables
            self.clear_tables()
            
            # Populate raw angles table
            for i, (d, m, s) in enumerate(angles, 1):
                self.raw_table.insert("", "end", values=(f"Angle {i}", d, m, s))
            
            # Update error
            self.error_label.config(text=f"Error: {error_seconds} seconds")
            
            # Populate corrected angles table
            for i, (d, m, s) in enumerate(corrected_angles, 1):
                self.corrected_table.insert("", "end", values=(f"Angle {i}", d, m, s))
            
            # Update sum and status
            total_seconds = sum(dms_to_seconds(*angle) for angle in corrected_angles)
            total_degrees, total_minutes, total_seconds_remainder = seconds_to_dms(total_seconds)
            expected_sum = calculate_expected_sum(sides)
            self.sum_label.config(text=f"Sum of Corrected Angles: {total_degrees}° {total_minutes}' {total_seconds_remainder}\"")
            if total_degrees == expected_sum and total_minutes == 0 and total_seconds_remainder == 0:
                self.status_label.config(text=f"Sum is exactly {expected_sum} degrees.", foreground="green")
            else:
                self.status_label.config(text="Warning: Sum may have minor rounding errors.", foreground="orange")
        
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = AngleCorrectorApp(root)
    root.mainloop()