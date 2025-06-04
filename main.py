import customtkinter as ctk
from tkinter import messagebox
import re
import math
from PIL import Image, ImageDraw, ImageFont
import os
from pathlib import Path

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
        self.root.geometry("1000x700")
        self.root.resizable(True, True)
        self.root.iconbitmap("icon.ico")
        ctk.set_appearance_mode("system")  # system default theme
        ctk.set_default_color_theme("blue")

        # Main container
        self.main_frame = ctk.CTkFrame(root)
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Configure main frame grid
        self.main_frame.grid_columnconfigure(0, weight=0)
        self.main_frame.grid_columnconfigure(1, weight=2)
        self.main_frame.grid_rowconfigure(0, weight=1)
        
        # Left frame for inputs
        self.input_frame = ctk.CTkFrame(self.main_frame)
        self.input_frame.grid(row=0, column=0, sticky="nsew")
        
        # Right frame for output
        self.output_frame = ctk.CTkFrame(self.main_frame)
        self.output_frame.grid(row=0, column=1, sticky="nsew")
        
        # Output frame sub-frames (tables on left, canvas on right)
        self.output_frame.grid_columnconfigure(0, weight=1)
        self.output_frame.grid_columnconfigure(1, weight=1)
        self.output_frame.grid_rowconfigure(0, weight=1)
        
        # Tables frame (centered)
        self.tables_frame = ctk.CTkFrame(self.output_frame)
        self.tables_frame.grid(row=0, column=0, sticky="nsew")
        self.tables_frame.grid_columnconfigure(0, weight=1)
        
        # Canvas frame (right)
        self.canvas_frame = ctk.CTkFrame(self.output_frame)
        self.canvas_frame.grid(row=0, column=1, sticky="nsew")
        
        # Input frame content
        ctk.CTkLabel(self.input_frame, text="Angle Corrector", font=("Helvetica", 16, "bold")).grid(row=0, column=0, columnspan=2, pady=10)
        ctk.CTkLabel(self.input_frame, text="Enter Angles (e.g., 235:20:25 or 235 20 25):", font=("Helvetica", 11, "italic")).grid(row=1, column=0, columnspan=2, pady=5)
        
        self.angle_entries = []
        self.angle_row = 2
        self.add_angle_field()
        
        # Buttons for adding fields, clearing, and viewing results
        ctk.CTkButton(self.input_frame, text="Add Field", command=self.add_angle_field, corner_radius=8).grid(row=998, column=0, padx=5, pady=5, sticky="ew")
        ctk.CTkButton(self.input_frame, text="Clear Fields", command=self.clear_fields, corner_radius=8).grid(row=998, column=1, padx=5, pady=5, sticky="ew")
        ctk.CTkButton(self.input_frame, text="View Results", command=self.correct_angles, corner_radius=8).grid(row=999, column=0, columnspan=2, padx=5, pady=10, sticky="ew")
        
        # Tables frame content
        ctk.CTkLabel(self.tables_frame, text="Results", font=("Helvetica", 14, "bold")).pack(pady=10)
        
        # Raw angles table (using CTkFrame and CTkLabel as a custom table)
        ctk.CTkLabel(self.tables_frame, text="Raw Angles:", font=("Helvetica", 12, "bold")).pack()
        self.raw_table_frame = ctk.CTkFrame(self.tables_frame, corner_radius=5)
        self.raw_table_frame.pack(fill="x", padx=10, pady=5)
        # Make columns responsive
        for col in range(4):
            self.raw_table_frame.grid_columnconfigure(col, weight=1)
        # Headers
        headers = ["Angle", "Degrees", "Minutes", "Seconds"]
        for col, header in enumerate(headers):
            ctk.CTkLabel(self.raw_table_frame, text=header, font=("Helvetica", 12, "bold"), anchor="center", corner_radius=5).grid(row=0, column=col, padx=1, pady=2, sticky="nsew")
        self.raw_table_labels = []  # To store label widgets for updating
        
        # Error label
        self.error_label = ctk.CTkLabel(self.tables_frame, text="Error: 0 seconds", font=("Helvetica", 12, "bold"))
        self.error_label.pack(pady=5)
        
        # Corrected angles table (using CTkFrame and CTkLabel as a custom table)
        ctk.CTkLabel(self.tables_frame, text="Corrected Angles:", font=("Helvetica", 12, "bold")).pack()
        self.corrected_table_frame = ctk.CTkFrame(self.tables_frame, corner_radius=5)
        self.corrected_table_frame.pack(fill="x", padx=10, pady=5)
        # Make columns responsive
        for col in range(4):
            self.corrected_table_frame.grid_columnconfigure(col, weight=1)
        # Headers
        for col, header in enumerate(headers):
            ctk.CTkLabel(self.corrected_table_frame, text=header, font=("Helvetica", 12, "bold"), anchor="center", corner_radius=5).grid(row=0, column=col, padx=1, pady=2, sticky="nsew")
        self.corrected_table_labels = []  # To store label widgets for updating
        
        # Sum label
        self.sum_label = ctk.CTkLabel(self.tables_frame, text="Sum of Corrected Angles: 0° 0' 0\"", font=("Helvetica", 12, "bold"))
        self.sum_label.pack(pady=5)
        
        # Canvas frame content
        ctk.CTkLabel(self.canvas_frame, text="Polygon Visualization:", font=("Helvetica", 12, "bold")).pack()
        self.zoom_level = 1.0
        self.canvas = ctk.CTkCanvas(self.canvas_frame, width=350, height=350, highlightthickness=1, highlightcolor="#007bff")
        self.canvas.pack(pady=5)
        
        # Store drawing parameters for image saving
        self.drawing_params = None
        
        # Zoom and download buttons
        self.zoom_frame = ctk.CTkFrame(self.canvas_frame, fg_color="transparent")
        self.zoom_frame.pack(pady=5)
        ctk.CTkButton(self.zoom_frame, text="Zoom In", command=self.zoom_in, corner_radius=8).pack(side="left", padx=5)
        ctk.CTkButton(self.zoom_frame, text="Zoom Out", command=self.zoom_out, corner_radius=8).pack(side="left", padx=5)
        ctk.CTkButton(self.zoom_frame, text="Download Image", command=self.download_image, corner_radius=8).pack(side="left", padx=5)
        
        # Status bar
        self.status_var = ctk.StringVar(value="Ready")
        self.status_bar = ctk.CTkLabel(self.root, textvariable=self.status_var, font=("Helvetica", 10, "bold"), anchor="w")
        self.status_bar.pack(side="bottom", fill="x")
    
    def add_angle_field(self):
        """Add a new angle input field in the grid."""
        index = len(self.angle_entries) + 1
        ctk.CTkLabel(self.input_frame, text=f"Angle {index}:", font=("Helvetica", 10, "bold")).grid(row=self.angle_row, column=0, padx=5, pady=2, sticky="w")
        entry = ctk.CTkEntry(self.input_frame, width=150, font=("Helvetica", 10))
        entry.grid(row=self.angle_row, column=1, padx=5, pady=2)
        entry.bind("<KeyRelease>", lambda e: self.validate_entry(entry))
        self.angle_entries.append((entry, f"Angle {index}"))
        self.angle_row += 1
    
    def validate_entry(self, entry):
        """Validate entry in real-time and highlight if invalid."""
        try:
            parse_dms(entry.get())
            entry.configure(fg_color="#CCFFCC")  # Reset to default (white in light mode)
        except ValueError:
            entry.configure(fg_color="#FFCCCC")  # Highlight red if invalid
    
    def clear_fields(self):
        """Clear all angle fields and reset to one field."""
        for entry, _ in self.angle_entries:
            entry.grid_forget()
            entry.destroy()
        for widget in self.input_frame.winfo_children():
            if isinstance(widget, ctk.CTkLabel) and widget.cget("text").startswith("Angle"):
                widget.grid_forget()
                widget.destroy()
        self.angle_entries.clear()
        self.angle_row = 2
        self.add_angle_field()
        self.clear_tables()
        self.status_var.set("Fields cleared")
    
    def clear_tables(self):
        """Clear the raw and corrected angles tables, reset labels, and clear canvas."""
        # Clear raw table
        for row in self.raw_table_labels:
            for label in row:
                label.destroy()
        self.raw_table_labels.clear()
        
        # Clear corrected table
        for row in self.corrected_table_labels:
            for label in row:
                label.destroy()
        self.corrected_table_labels.clear()
        
        self.error_label.configure(text="Error: 0 seconds")
        self.sum_label.configure(text="Sum of Corrected Angles: 0° 0' 0\"")
        self.status_var.set("Ready")
        self.canvas.delete("all")
        self.zoom_level = 1.0
        self.drawing_params = None
    
    def zoom_in(self):
        """Increase zoom level and redraw polygon."""
        self.zoom_level = min(self.zoom_level * 1.2, 2.0)
        self.correct_angles()
        self.status_var.set("Zoomed in")
    
    def zoom_out(self):
        """Decrease zoom level and redraw polygon."""
        self.zoom_level = max(self.zoom_level / 1.2, 0.5)
        self.correct_angles()
        self.status_var.set("Zoomed out")
    
    def draw_polygon(self, angles):
        """Draw the polygon on the canvas and store parameters for image saving."""
        self.canvas.delete("all")
        
        def dms_to_decimal(d, m, s):
            return d + m / 60.0 + s / 3600.0
        
        decimal_angles = [dms_to_decimal(d, m, s) for d, m, s in angles]
        exterior_angles = [180 - angle for angle in decimal_angles]
        
        side_length = 80
        center_x, center_y = 175, 175
        vertices = []
        current_angle = 0
        x, y = center_x + side_length, center_y
        
        for angle in exterior_angles:
            vertices.append((x, y))
            current_angle += math.radians(angle)
            x += side_length * math.cos(current_angle)
            y -= side_length * math.sin(current_angle)
        
        vertices.append(vertices[0])
        
        min_x = min(x for x, y in vertices)
        max_x = max(x for x, y in vertices)
        min_y = min(y for x, y in vertices)
        max_y = max(y for x, y in vertices)
        poly_width = max_x - min_x
        poly_height = max_y - min_y
        scale_factor = min(350 / poly_width, 350 / poly_height) * 0.8 * self.zoom_level
        center_x_poly = (min_x + max_x) / 2
        center_y_poly = (min_y + max_y) / 2
        
        scaled_vertices = [
            ((x - center_x_poly) * scale_factor + center_x,
             (y - center_y_poly) * scale_factor + center_y)
            for x, y in vertices
        ]
        
        # Draw on canvas
        self.canvas.create_rectangle(0, 0, 350, 350, fill="white", outline="#007bff")
        self.canvas.create_polygon(scaled_vertices, outline="#007bff", fill="#e6f3ff", width=2)
        
        for i, (x, y) in enumerate(scaled_vertices[:-1]):
            self.canvas.create_oval(x-5, y-5, x+5, y+5, fill="#007bff", outline="white")
            angle_text = f"A{i+1}: {decimal_angles[i]:.2f}°"
            offset_x = 20 if x < center_x else -20
            offset_y = 20 if y < center_y else -20
            self.canvas.create_text(x + offset_x, y + offset_y, text=angle_text, font=("Helvetica", 8), fill="#333")
        
        # Store drawing parameters for image saving
        self.drawing_params = {
            "scaled_vertices": scaled_vertices,
            "decimal_angles": decimal_angles,
            "center_x": center_x,
            "center_y": center_y
        }
    
    def download_image(self):
        """Save the canvas as a PNG image in the Downloads folder."""
        try:
            if not self.drawing_params:
                raise ValueError("No polygon to save. Please view results first.")
            
            # Create a blank PIL image
            img = Image.new("RGB", (350, 350), "white")
            draw = ImageDraw.Draw(img)
            
            # Redraw the content
            scaled_vertices = self.drawing_params["scaled_vertices"]
            decimal_angles = self.drawing_params["decimal_angles"]
            center_x = self.drawing_params["center_x"]
            center_y = self.drawing_params["center_y"]
            
            # Draw background and polygon
            draw.rectangle([0, 0, 350, 350], fill="white", outline="#007bff")
            draw.polygon(scaled_vertices, outline="#007bff", fill="#e6f3ff", width=2)
            
            # Draw vertices and labels
            try:
                font = ImageFont.truetype("arial.ttf", 12)
            except:
                font = ImageFont.load_default()
            
            for i, (x, y) in enumerate(scaled_vertices[:-1]):
                draw.ellipse([x-5, y-5, x+5, y+5], fill="#007bff", outline="white")
                angle_text = f"A{i+1}: {decimal_angles[i]:.2f}°"
                offset_x = 20 if x < center_x else -20
                offset_y = 20 if y < center_y else -20
                draw.text((x + offset_x, y + offset_y), angle_text, font=font, fill="#333")
            
            # Get the Downloads folder path
            downloads_path = str(Path.home() / "Downloads")
            if not os.path.exists(downloads_path):
                os.makedirs(downloads_path)  # Create Downloads folder if it doesn't exist
            
            # Include timestamp in filename to avoid overwriting
            timestamp = "20250604_1635"  # Updated to 04:35 PM GMT, June 04, 2025
            filename = f"polygon_{timestamp}.png"
            save_path = os.path.join(downloads_path, filename)
            
            # Save the image
            img.save(save_path, "PNG")
            self.status_var.set(f"Image saved as {save_path}")
        
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save image: {str(e)}")
            self.status_var.set(f"Error: Failed to save image - {str(e)}")
    
    def correct_angles(self):
        """Process, correct, and draw angles."""
        try:
            sides = len(self.angle_entries)
            if sides < 3:
                messagebox.showerror("Error", "Polygon must have at least 3 angles.")
                self.status_var.set("Error: At least 3 angles required")
                return
            
            angles = []
            for entry, label in self.angle_entries:
                text = entry.get().strip()
                if not text:
                    messagebox.showerror("Error", f"Missing input for {label}.")
                    self.status_var.set(f"Error: Missing input for {label}")
                    return
                try:
                    angles.append(parse_dms(text))
                except ValueError:
                    messagebox.showerror("Error", f"Invalid format for {label}. Use 'D:M:S' or 'D M S' (e.g., 235:20:25).")
                    self.status_var.set(f"Error: Invalid format for {label}")
                    return
            
            corrected_angles, error_seconds = correct_angles(angles, sides)
            
            self.clear_tables()
            
            # Populate raw angles table
            self.raw_table_labels = []
            for i, (d, m, s) in enumerate(angles, 1):
                row_labels = []
                row_labels.append(ctk.CTkLabel(self.raw_table_frame, text=f"Angle {i}", anchor="center", font=("Helvetica", 10, "bold"), corner_radius=5))
                row_labels[-1].grid(row=i, column=0, padx=1, pady=2, sticky="nsew")
                row_labels.append(ctk.CTkLabel(self.raw_table_frame, text=str(d), anchor="center", font=("Helvetica", 10, "bold"), corner_radius=5))
                row_labels[-1].grid(row=i, column=1, padx=1, pady=2, sticky="nsew")
                row_labels.append(ctk.CTkLabel(self.raw_table_frame, text=str(m), anchor="center", font=("Helvetica", 10, "bold"), corner_radius=5))
                row_labels[-1].grid(row=i, column=2, padx=1, pady=2, sticky="nsew")
                row_labels.append(ctk.CTkLabel(self.raw_table_frame, text=str(s), anchor="center", font=("Helvetica", 10, "bold"), corner_radius=5))
                row_labels[-1].grid(row=i, column=3, padx=1, pady=2, sticky="nsew")
                self.raw_table_labels.append(row_labels)
            
            self.error_label.configure(text=f"Error: {error_seconds} seconds")
            
            # Populate corrected angles table
            self.corrected_table_labels = []
            for i, (d, m, s) in enumerate(corrected_angles, 1):
                row_labels = []
                row_labels.append(ctk.CTkLabel(self.corrected_table_frame, text=f"Angle {i}", anchor="center", font=("Helvetica", 10, "bold"), corner_radius=5))
                row_labels[-1].grid(row=i, column=0, padx=1, pady=2, sticky="nsew")
                row_labels.append(ctk.CTkLabel(self.corrected_table_frame, text=str(d), anchor="center", font=("Helvetica", 10, "bold"), corner_radius=5))
                row_labels[-1].grid(row=i, column=1, padx=1, pady=2, sticky="nsew")
                row_labels.append(ctk.CTkLabel(self.corrected_table_frame, text=str(m), anchor="center", font=("Helvetica", 10, "bold"), corner_radius=5))
                row_labels[-1].grid(row=i, column=2, padx=1, pady=2, sticky="nsew")
                row_labels.append(ctk.CTkLabel(self.corrected_table_frame, text=str(s), anchor="center", font=("Helvetica", 10, "bold"), corner_radius=5))
                row_labels[-1].grid(row=i, column=3, padx=1, pady=2, sticky="nsew")
                self.corrected_table_labels.append(row_labels)
            
            total_seconds = sum(dms_to_seconds(*angle) for angle in corrected_angles)
            total_degrees, total_minutes, total_seconds_remainder = seconds_to_dms(total_seconds)
            expected_sum = calculate_expected_sum(sides)
            self.sum_label.configure(text=f"Sum of Corrected Angles: {total_degrees}° {total_minutes}' {total_seconds_remainder}\"")
            if total_degrees == expected_sum and total_minutes == 0 and total_seconds_remainder == 0:
                self.status_var.set(f"Sum is exactly {expected_sum} degrees")
            else:
                self.status_var.set("Warning: Sum may have minor rounding errors")
            
            self.draw_polygon(corrected_angles)
        
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
            self.status_var.set(f"Error: {str(e)}")

if __name__ == "__main__":
    root = ctk.CTk()
    app = AngleCorrectorApp(root)
    root.mainloop()