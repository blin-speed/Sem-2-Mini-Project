import tkinter as tk
from tkinter import Button, ttk
from datetime import datetime
import sqlite3
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError
import folium  # type: ignore
import webbrowser
from tkinter import simpledialog, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Initialize the main application window
root = tk.Tk()
root.geometry('768x1024')  # Set window size
root.title('Kisan Link')

# Auto-maximize the window

root.state('zoomed')

# Update the main application window background color
root.configure(bg="black")

# Global variable to track menu visibility
menu_open = False

# Splash Screen Fade-in Animation
def fade_in_splash_screen(color_val=100):
    if color_val < 255:
        color_val += 5
        hex_color = f"#{color_val:02x}{color_val:02x}{color_val:02x}"
        splash_label.config(fg=hex_color)
        root.after(50, fade_in_splash_screen, color_val)
    else:
        root.after(1000, fade_in_text)

def fade_in_text(color_val=100):
    if color_val < 255:
        color_val += 5
        hex_color = f"#{color_val:02x}{color_val:02x}{color_val:02x}"
        start_label.config(fg=hex_color)
        root.after(50, fade_in_text, color_val)
    else:
        start_label.pack_forget()
        splash_screen.pack_forget()
        main_app()

# Function to open inventory management window
def open_inventory_management():
    inventory_window = tk.Toplevel(root)
    inventory_window.state("zoomed")
    inventory_window.configure(bg="white")  # Set background to white

    # Add heading label
    tk.Label(inventory_window, text="INVENTORY MANAGER", font=("Bold", 20), bg="white", fg="black").pack(pady=20)

    # Create a green box to enclose the buttons
    button_frame = tk.Frame(inventory_window, bg="green", width=300, height=200)
    button_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)  # Center the frame
    button_frame.pack_propagate(False)

    # Add buttons for different inventory types
    tk.Button(button_frame, text="Crop Inventory", font=("Bold", 15), bg="white", fg="green", bd=0, command=lambda: open_table_management("crop")).pack(pady=10)
    tk.Button(button_frame, text="Products Inventory", font=("Bold", 15), bg="white", fg="green", bd=0, command=lambda: open_table_management("products")).pack(pady=10)
    tk.Button(button_frame, text="Materials Inventory", font=("Bold", 15), bg="white", fg="green", bd=0, command=lambda: open_table_management("materials")).pack(pady=10)

# Function to open table management window
def open_table_management(inventory_type):
    table_window = tk.Toplevel(root)
    table_window.geometry("600x400")  # Set a fixed size for the window
    table_window.configure(bg="white")  # Set background to white

    # Create a green box to enclose the content
    content_frame = tk.Frame(table_window, bg="green", width=500, height=300)
    content_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)  # Center the frame
    content_frame.pack_propagate(False)

    # Add a scrollbar for the table list
    table_frame = tk.Frame(content_frame, bg="white")
    table_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

    canvas = tk.Canvas(table_frame, bg="white")
    scrollbar = tk.Scrollbar(table_frame, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas, bg="white")

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )

    canvas.create_window((0.5, 0.5), window=scrollable_frame, anchor="center")  # Centrally align the frame
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    # Add buttons for table management options
    tk.Button(scrollable_frame, text="New Table", font=("Bold", 15), bg="green", fg="white", command=lambda: create_new_table(inventory_type)).pack(pady=10)
    tk.Button(scrollable_frame, text="Manage Table", font=("Bold", 15), bg="green", fg="white", command=lambda: manage_existing_table(inventory_type)).pack(pady=10)
    tk.Button(scrollable_frame, text="Delete Table", font=("Bold", 15), bg="green", fg="white", command=lambda: delete_existing_table(inventory_type)).pack(pady=10)

# Function to create a new table
def create_new_table(inventory_type):
    new_table_window = tk.Toplevel(root)
    new_table_window.geometry("400x300")  # Set a fixed size for the window
    new_table_window.configure(bg="white")  # Set background to white

    # Create a frame to center the content
    content_frame = tk.Frame(new_table_window, bg="white", width=350, height=200)  # Changed background to white
    content_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)  # Center the frame
    content_frame.pack_propagate(False)

    tk.Label(content_frame, text="Enter Table Name:", font=("Arial", 10), fg="black", bg="white").pack(pady=10)
    table_name_entry = tk.Entry(content_frame, font=("Arial", 10), fg="black", bg="white")
    table_name_entry.pack(pady=10)

    # Label to display messages
    message_label = tk.Label(content_frame, text="", font=("Arial", 9), fg="black", bg="white")
    message_label.pack(pady=10)

    def create_table():
        table_name = table_name_entry.get().strip()
        if table_name:
            # Sanitize table name to ensure it is a valid SQLite identifier
            if not table_name.isidentifier():
                message_label.config(text="Invalid table name. Use only letters, numbers, and underscores.", fg="red")
                return
            with sqlite3.connect(f"{inventory_type}_inventory.db") as conn:
                cursor = conn.cursor()
                cursor.execute(f"CREATE TABLE IF NOT EXISTS '{table_name}' (id INTEGER PRIMARY KEY, crops TEXT, kg INTEGER)")
                conn.commit()
            message_label.config(text=f"Table '{table_name}' created successfully!", fg="green")
        else:
            message_label.config(text="Table name cannot be empty.", fg="red")

    tk.Button(content_frame, text="Create Table", font=("Arial", 10), bg="green", fg="white", command=create_table).pack(pady=10)

# Function to manage existing tables
def manage_existing_table(inventory_type):
    manage_table_window = tk.Toplevel(root)
    manage_table_window.geometry("400x300")
    manage_table_window.configure(bg="white")  # Set background to white

    # Add a scrollbar for the table list
    table_frame = tk.Frame(manage_table_window, bg="white")
    table_frame.pack(fill=tk.BOTH, expand=True)

    canvas = tk.Canvas(table_frame, bg="white")
    scrollbar = tk.Scrollbar(table_frame, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas, bg="white")

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    tk.Label(scrollable_frame, text="Select a Table to Manage:", font=("Arial", 10), fg="black", bg="white").pack(pady=10)

    # Fetch existing tables
    with sqlite3.connect(f"{inventory_type}_inventory.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()

    for table in tables:
        table_name = table[0]
        tk.Button(scrollable_frame, text=table_name, font=("Arial", 10), bg="green", fg="white", command=lambda t=table_name: manage_inventory(inventory_type, t)).pack(pady=5)

# Function to delete existing tables
def delete_existing_table(inventory_type):
    delete_table_window = tk.Toplevel(root)
    delete_table_window.geometry("400x300")
    delete_table_window.configure(bg="white")  # Set background to white

    # Add a scrollbar for the table list
    table_frame = tk.Frame(delete_table_window, bg="white")
    table_frame.pack(fill=tk.BOTH, expand=True)

    canvas = tk.Canvas(table_frame, bg="white")
    scrollbar = tk.Scrollbar(table_frame, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas, bg="white")

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    tk.Label(scrollable_frame, text="Select a Table to Delete:", font=("Arial", 10), fg="black", bg="white").pack(pady=10)

    # Fetch existing tables
    with sqlite3.connect(f"{inventory_type}_inventory.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()

    def delete_table(table_name):
        with sqlite3.connect(f"{inventory_type}_inventory.db") as conn:
            cursor = conn.cursor()
            cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
            conn.commit()
        tk.Label(scrollable_frame, text=f"Table '{table_name}' deleted successfully!", font=("Arial", 9), fg="red", bg="white").pack(pady=10)

    for table in tables:
        table_name = table[0]
        tk.Button(scrollable_frame, text=table_name, font=("Arial", 10), bg="green", fg="white", command=lambda t=table_name: delete_table(t)).pack(pady=5)

# Function to manage inventory for a specific table
def manage_inventory(inventory_type, table_name):
    inventory_window = tk.Toplevel(root)
    inventory_window.state("zoomed")
    inventory_window.configure(bg="white")  # Set background to white

    # Connect to the database
    connection = sqlite3.connect(f"{inventory_type}_inventory.db")
    cursor = connection.cursor()

    # Determine headers based on inventory type
    if inventory_type == "materials":
        headers = ("ID", "Materials", "Kg")
    elif inventory_type == "products":
        headers = ("ID", "Products", "Kg")
    else:  # Default to crop management
        headers = ("ID", "Crops", "Kg")

    # Create Treeview to display data
    style = ttk.Style()
    style.configure("Treeview", background="white", foreground="black", fieldbackground="white")
    style.configure("Treeview.Heading", background="white", foreground="black")

    tree = ttk.Treeview(inventory_window, columns=headers, show="headings", style="Treeview")
    for header in headers:
        tree.heading(header, text=header)
        tree.column(header, width=150, anchor="center")
    tree.pack(expand=True, fill="both")

    # Function to refresh Treeview
    def refresh_treeview():
        for item in tree.get_children():
            tree.delete(item)
        cursor.execute(f"SELECT * FROM {table_name}")
        rows = cursor.fetchall()
        for row in rows:
            tree.insert("", "end", values=row)

    refresh_treeview()

    # Input frame for Add/Edit/Delete
    input_frame = ttk.Frame(inventory_window)
    input_frame.pack(pady=10)

    ttk.Label(input_frame, text=headers[1] + ":", foreground="black", background="white").grid(row=0, column=0, padx=5, pady=5)
    item_entry = ttk.Entry(input_frame, foreground="black", background="white")
    item_entry.grid(row=0, column=1, padx=5, pady=5)

    ttk.Label(input_frame, text="Kg:", foreground="black", background="white").grid(row=1, column=0, padx=5, pady=5)
    kg_entry = ttk.Entry(input_frame, foreground="black", background="white")
    kg_entry.grid(row=1, column=1, padx=5, pady=5)

    # Add row function
    def add_row():
        item = item_entry.get()
        kg = kg_entry.get()
        if item and kg.isdigit():
            cursor.execute(f"INSERT INTO {table_name} ({headers[1].lower()}, kg) VALUES (?, ?)", (item, int(kg)))
            connection.commit()
            refresh_treeview()
            item_entry.delete(0, tk.END)
            kg_entry.delete(0, tk.END)

    # Edit row function
    def edit_row():
        selected_item = tree.selection()
        if selected_item:
            item_values = tree.item(selected_item, "values")
            item = item_entry.get()
            kg = kg_entry.get()
            if item and kg.isdigit():
                cursor.execute(f"UPDATE {table_name} SET {headers[1].lower()} = ?, kg = ? WHERE id = ?", (item, int(kg), item_values[0]))
                connection.commit()
                refresh_treeview()
                item_entry.delete(0, tk.END)
                kg_entry.delete(0, tk.END)

    # Delete row function
    def delete_row():
        selected_item = tree.selection()
        if selected_item:
            item_values = tree.item(selected_item, "values")
            cursor.execute(f"DELETE FROM {table_name} WHERE id = ?", (item_values[0],))
            connection.commit()
            refresh_treeview()

    # Buttons for Add/Edit/Delete
    ttk.Button(input_frame, text="Add Row", command=add_row).grid(row=2, column=0, padx=5, pady=5)
    ttk.Button(input_frame, text="Edit Selected Row", command=edit_row).grid(row=2, column=1, padx=5, pady=5)
    ttk.Button(input_frame, text="Delete Selected Row", command=delete_row).grid(row=2, column=2, padx=5, pady=5)

    # Close database connection on window close
    inventory_window.protocol("WM_DELETE_WINDOW", lambda: connection.close() or inventory_window.destroy())

# Main Application Function
def main_app():
    global main_frame, options_frame, show_options_button
    main_frame = tk.Frame(root)
    main_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
    main_frame.configure(width=200, height=400)

    # Display greeting based on the time of day
    greeting = get_greeting()
    tk.Label(main_frame, text="Hello :)", font=("Bold", 30), fg="black").pack(pady=10)
    tk.Label(main_frame, text=greeting, font=("Bold", 20), fg="black").pack(pady=10)

    # Create a centered green box for buttons
    button_frame = tk.Frame(main_frame, bg="green", width=300, height=150)
    button_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
    button_frame.pack_propagate(False)

    # Add buttons to the green box
    tk.Button(button_frame, text="Farming Assistance", font=("Bold", 15), bg="white", bd=0, command=toggle_menu).pack(pady=10)
    tk.Button(button_frame, text="Inventory Management", font=("Bold", 15), bg="white", bd=0, command=open_inventory_management).pack(pady=10)

    # Create the "=" button (hidden initially)
    show_options_button = tk.Button(root, text="=", font=("Bold", 15), bg="#CCCCCC", bd=0, command=toggle_menu)
    show_options_button.place(x=10, y=10)
    show_options_button.place_forget()

# Toggle Sidebar Menu
def toggle_menu():
    global menu_open, options_frame, show_options_button
    if not menu_open:
        option_list()
        show_options_button.place_forget()
        menu_open = True
    else:
        options_frame.pack_forget()
        show_options_button.place(x=10, y=10)
        menu_open = False

# Sidebar Menu Options
def option_list():
    global options_frame

    # Functions for pages
    def home_page():
        delete_pages()
        greeting = get_greeting()
        tk.Label(main_frame, text="Hello :)", font=("Bold", 30), fg="black").pack(pady=10)
        tk.Label(main_frame, text=greeting, font=("Bold", 20), fg="black").pack(pady=10)

        button_frame = tk.Frame(main_frame, bg="green", width=300, height=150)
        button_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)  # Fixed duplicate relx
        button_frame.pack_propagate(False)

        tk.Button(button_frame, text="Farming Assistance", font=("Bold", 15), bg="white", command=toggle_menu).pack(pady=10)
        tk.Button(button_frame, text="Inventory Management", font=("Bold", 15), bg="white", command=open_inventory_management).pack(pady=10)

    def weather_page():
        delete_pages()  # Clear previous content

        # Add input field and button for entering city name
        tk.Label(main_frame, text="Enter City Name:", font=("Bold", 15), fg="white", bg="black").pack(pady=10)
        city_entry = tk.Entry(main_frame, font=("Arial", 12), fg="black", bg="white", width=30)
        city_entry.pack(pady=10)

        def create_map():
            city = city_entry.get().strip()
            if city:
                try:
                    # Use geopy to get latitude and longitude for the city
                    geolocator = Nominatim(user_agent="weathermap")
                    location = geolocator.geocode(city, timeout=10)  # Set a timeout for geocoding

                    if location:
                        lat, lon = location.latitude, location.longitude
                        # Create a map with the geocoded location
                        m = folium.Map(location=[lat, lon], zoom_start=12)
                        m.save('gmap.html')  # Save the map to an HTML file
                        webbrowser.open('gmap.html')  # Open the saved map in the default web browser
                    else:
                        # Show an error message if the city is not found
                        messagebox.showerror("Error", "City not found. Please try again.")
                except (GeocoderTimedOut, GeocoderServiceError) as e:
                    # Handle geocoding service errors
                    messagebox.showerror("Error", f"Geocoding service error: {e}")
            else:
                # Show an error message if no input is provided
                messagebox.showerror("Error", "No city name entered.")

        # Add a button to generate the map
        tk.Button(main_frame, text="Generate Map", font=("Bold", 12), bg="green", fg="white", bd=0, command=create_map).pack(pady=10)

        # Add the graph below the "Generate Map" button
        def add_graph():
            # Data for the graph (updated based on the provided graph)
            months = ["January", "February", "March", "April", "May", "June", 
                      "July", "August", "September", "October", "November", "December"]
            precipitation = [10, 20, 30, 50, 100, 150, 300, 250, 200, 100, 50, 20]
            temperature = [7, 10, 15, 20, 25, 30, 35, 38, 35, 25, 15, 10]

            # Ensure temperature values do not exceed 38
            temperature = [min(temp, 38) for temp in temperature]

            # Create the plot
            fig, ax1 = plt.subplots(figsize=(8, 4))

            # Bar chart for precipitation
            ax1.bar(months, precipitation, color='dodgerblue', label='Precipitation (mm)')
            ax1.set_ylabel('Precipitation (mm)', color='dodgerblue')
            ax1.tick_params(axis='y', labelcolor='dodgerblue')
            ax1.set_yticks(range(0, 401, 20))  # Set scale up to 400 with intervals of 20
            ax1.set_xticklabels(months, rotation=45)

            # Line chart for temperature
            ax2 = ax1.twinx()
            ax2.plot(months, temperature, color='red', marker='o', linewidth=2, label='Temperature (°C)')
            ax2.set_ylabel('Temperature (°C)', color='red')
            ax2.tick_params(axis='y', labelcolor='red')
            ax2.set_yticks(range(0, 41, 4))  # Set scale up to 40 with intervals of 4

            # Title and layout
            plt.title("Monthly Precipitation and Temperature")
            fig.tight_layout()

            # Embed the graph in the Tkinter window
            canvas = FigureCanvasTkAgg(fig, master=main_frame)
            canvas_widget = canvas.get_tk_widget()
            canvas_widget.pack(pady=20)

        add_graph()

    def soil_page():
        delete_pages()  # Clear previous content

        # Add title
        tk.Label(main_frame, text="SOIL QUALITY", font=("Bold", 30)).pack(pady=20)

        # Create a frame for the table and calculator
        content_frame = tk.Frame(main_frame)
        content_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)  # Center the content frame
        content_frame.pack(fill=tk.BOTH, expand=True)

        # Add a scrollbar
        scrollbar = tk.Scrollbar(content_frame, orient="vertical")
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Create a canvas to hold the content
        canvas = tk.Canvas(content_frame, yscrollcommand=scrollbar.set)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=canvas.yview)

        # Create a frame inside the canvas
        scrollable_frame = tk.Frame(canvas)
        canvas.create_window((0.5, 0.5), window=scrollable_frame, anchor=tk.CENTER)  # Center the table
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        # Display table contents
        table_frame = tk.Frame(scrollable_frame)
        table_frame.pack(pady=20, padx=20)

        # Table data split by parameters
        table_data = [
            ["Parameter", "Measurement", "Score", "Interpretation"],
            ["pH Level", "6.5 – 7.5", "9–10", "Ideal range\nfor most crops"],
            ["", "6.0 – 6.4 or\n7.6 – 8.0", "7–8", "Acceptable"],
            ["", "5.5 – 5.9 or\n8.1 – 8.5", "4–6", "Moderately\nproblematic"],
            ["", "<5.5 or >8.5", "1–3", "Poor – needs\ncorrection"],
            ["Organic Matter", ">5%", "9–10", "Excellent"],
            ["(% by weight)", "3–5%", "7–8", "Good"],
            ["", "2–3%", "4–6", "Fair"],
            ["", "<2%", "1–3", "Poor"],
            ["Nutrient Levels", "Balanced N-P-K\n(per crop needs)", "9–10", "Optimal nutrient\navailability"],
            ["", "Slightly imbalanced\n(minor excess/deficit)", "6–8", "Adequate, minor\nadjustments needed"],
            ["", "Major deficiency\nor excess", "1–5", "Poor – needs\nfertilization or\nremediation"],
            ["Texture/\nDrainage", "Loamy, good\ndrainage", "9–10", "Ideal soil\nstructure"],
            ["", "Slightly sandy/\nclayey", "6–8", "Manageable with\namendments"],
            ["", "Heavy clay or\nvery sandy", "3–5", "Poor structure\nor drainage"],
            ["", "Compacted, poor\ndrainage", "1–2", "Problematic for\nroot growth"]
        ]

        # Create table headers
        for col, header in enumerate(table_data[0]):
            tk.Label(
                table_frame, 
                text=header, 
                font=("Bold", 10), 
                bg="#CCCCCC", 
                borderwidth=1, 
                relief="solid", 
                width=15, 
                anchor="center", 
                padx=5, 
                pady=5
            ).grid(row=0, column=col, sticky="nsew")

        # Populate table rows
        for row, data_row in enumerate(table_data[1:], start=1):
            for col, cell in enumerate(data_row):
                tk.Label(
                    table_frame, 
                    text=cell, 
                    font=("Arial", 9), 
                    borderwidth=1, 
                    relief="solid", 
                    width=15, 
                    anchor="center", 
                    padx=5, 
                    pady=5
                ).grid(row=row, column=col, sticky="nsew")

        # Adjust column weights to ensure proper alignment
        for col in range(len(table_data[0])):
            table_frame.grid_columnconfigure(col, weight=1)

        # Interactive Soil Quality Index (SQI) Calculator
        calculator_frame = tk.Frame(scrollable_frame, bg="#F0F0F0", padx=10, pady=10)
        calculator_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)  # Center the calculator frame
        calculator_frame.pack(pady=20, fill=tk.X)

        tk.Label(calculator_frame, text="Soil Quality Index (SQI) Calculator", font=("Bold", 14), bg="#F0F0F0").grid(row=0, column=0, columnspan=2, pady=10)

        # Input fields
        tk.Label(calculator_frame, text="pH Score (1–10):", bg="#F0F0F0").grid(row=1, column=0, sticky="e", padx=10, pady=5)
        ph_score_entry = tk.Entry(calculator_frame, width=20)
        ph_score_entry.grid(row=1, column=1, sticky="w", padx=10, pady=5)

        tk.Label(calculator_frame, text="Organic Matter Score (1–10):", bg="#F0F0F0").grid(row=2, column=0, sticky="e", padx=10, pady=5)
        organic_score_entry = tk.Entry(calculator_frame, width=20)
        organic_score_entry.grid(row=2, column=1, sticky="w", padx=10, pady=5)

        tk.Label(calculator_frame, text="Nutrient Score (1–10):", bg="#F0F0F0").grid(row=3, column=0, sticky="e", padx=10, pady=5)
        nutrient_score_entry = tk.Entry(calculator_frame, width=20)
        nutrient_score_entry.grid(row=3, column=1, sticky="w", padx=10, pady=5)

        tk.Label(calculator_frame, text="Texture/Drainage Score (1–10):", bg="#F0F0F0").grid(row=4, column=0, sticky="e", padx=10, pady=5)
        texture_score_entry = tk.Entry(calculator_frame, width=20)
        texture_score_entry.grid(row=4, column=1, sticky="w", padx=10, pady=5)

        # Output label
        result_label = tk.Label(calculator_frame, text="", font=("Arial", 12), bg="#F0F0F0", fg="green")
        result_label.grid(row=5, column=0, columnspan=2, pady=10)

        # Calculate function
        def calculate_sqi():
            try:
                ph_score = float(ph_score_entry.get())
                organic_score = float(organic_score_entry.get())
                nutrient_score = float(nutrient_score_entry.get())
                texture_score = float(texture_score_entry.get())
                sqi = (ph_score + organic_score + nutrient_score + texture_score) / 4
                result_label.config(text=f"Calculated SQI: {sqi:.2f}", fg="green")
            except ValueError:
                result_label.config(text="Please enter valid numbers.", fg="red")

        # Calculate button
        calculate_button = tk.Button(calculator_frame, text="Calculate", font=("Bold", 12), bg="#CCCCCC", command=calculate_sqi)
        calculate_button.grid(row=6, column=0, columnspan=2, pady=10)

    def fertilizer_page():
        delete_pages()  # Clear previous content

        # Add title
        tk.Label(main_frame, text="FERTILIZER", font=("Bold", 30)).pack(pady=20)

        # Display table contents
        table_frame = tk.Frame(main_frame)
        table_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)  # Center the table frame
        table_frame.pack(pady=20, padx=20)

        # Updated table data with long sentences broken into multiple lines
        table_data = [
            ["Crop", "Recommended Fertilizer", "Purpose"],
            ["Rice", "Urea,\nDAP (Diammonium Phosphate)", 
             "Boosts nitrogen and phosphorus\nlevels for better yield."],
            ["Wheat", "Urea,\nPotash", 
             "Enhances growth and grain\nquality."],
            ["Maize (Corn)", "NPK (Nitrogen,\nPhosphorus, Potassium)", 
             "Supports overall plant\ndevelopment."],
            ["Sugarcane", "Ammonium Sulfate,\nPotash", 
             "Improves yield and sugar\ncontent."],
            ["Cotton", "NPK,\nZinc Sulfate", 
             "Promotes fiber quality and\nplant health."],
            ["Vegetables", "Compost,\nNPK", 
             "Provides balanced nutrients\nfor growth."],
            ["Fruits (e.g., Mango)", "Organic Manure,\nPotash", 
             "Enhances fruit size and\nsweetness."],
            ["Pulses (e.g., Lentils)", "Phosphorus-rich\nFertilizers", 
             "Encourages root development\nand nitrogen fixation."]
        ]

        # Create table headers
        for col, header in enumerate(table_data[0]):
            tk.Label(
                table_frame, 
                text=header, 
                font=("Bold", 12), 
                bg="#CCCCCC", 
                borderwidth=1, 
                relief="solid", 
                width=20,  # Adjusted width for better alignment
                anchor="center",  # Center-align text
                padx=5,  # Add horizontal padding
                pady=5   # Add vertical padding
            ).grid(row=0, column=col, sticky="nsew")  # Ensure the cell expands properly

        # Populate table rows
        for row, data_row in enumerate(table_data[1:], start=1):
            for col, cell in enumerate(data_row):
                tk.Label(
                    table_frame, 
                    text=cell, 
                    font=("Arial", 10), 
                    borderwidth=1, 
                    relief="solid", 
                    width=20,  # Adjusted width for better alignment
                    anchor="center",  # Center-align text in all columns
                    padx=5,  # Add horizontal padding
                    pady=5   # Add vertical padding
                ).grid(row=row, column=col, sticky="nsew")

        # Adjust column weights to ensure proper alignment
        for col in range(len(table_data[0])):
            table_frame.grid_columnconfigure(col, weight=1)

        # Interactive Fertilizer Calculator
        calculator_frame = tk.Frame(main_frame, bg="#F0F0F0", padx=10, pady=10)
        calculator_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)  # Center the calculator frame
        calculator_frame.pack(pady=20, fill=tk.X)

        tk.Label(calculator_frame, text="Fertilizer Calculator", font=("Bold", 14), bg="#F0F0F0").grid(row=0, column=0, columnspan=2, pady=10)

        # Input fields
        tk.Label(calculator_frame, text="Required Nutrient Application Rate (kg/ha):", bg="#F0F0F0").grid(row=1, column=0, sticky="e", padx=10, pady=5)
        nutrient_rate_entry = tk.Entry(calculator_frame, width=20)
        nutrient_rate_entry.grid(row=1, column=1, sticky="w", padx=10, pady=5)

        tk.Label(calculator_frame, text="Percentage of Nutrient in Fertilizer (%):", bg="#F0F0F0").grid(row=2, column=0, sticky="e", padx=10, pady=5)
        nutrient_percentage_entry = tk.Entry(calculator_frame, width=20)
        nutrient_percentage_entry.grid(row=2, column=1, sticky="w", padx=10, pady=5)

        # Output label
        result_label = tk.Label(calculator_frame, text="", font=("Arial", 12), bg="#F0F0F0", fg="green")
        result_label.grid(row=3, column=0, columnspan=2, pady=10)

        # Calculate function
        def calculate_fertilizer():
            try:
                nutrient_rate = float(nutrient_rate_entry.get())
                nutrient_percentage = float(nutrient_percentage_entry.get())
                if nutrient_percentage == 0:
                    raise ZeroDivisionError
                total_fertilizer = (nutrient_rate * 100) / nutrient_percentage
                result_label.config(text=f"Total Fertilizer Required: {total_fertilizer:.2f} kg", fg="green")
            except ZeroDivisionError:
                result_label.config(text="Nutrient percentage cannot be zero.", fg="red")
            except ValueError:
                result_label.config(text="Please enter valid numbers.", fg="red")

        # Calculate button
        calculate_button = tk.Button(calculator_frame, text="Calculate", font=("Bold", 12), bg="#CCCCCC", command=calculate_fertilizer)
        calculate_button.grid(row=4, column=0, columnspan=2, pady=10)

    # Ensure the Inventory Management button is always linked correctly
    def create_page(title):
        delete_pages()
        tk.Label(main_frame, text=title, font=("Bold", 30)).pack(pady=20)

    # Helper functions
    def hide_indicators():
        for indicator in [home_indicate, weather_indicate, soil_indicate, fertilizer_indicate]:
            indicator.config(bg="green")  # Set indicator background to green

    def delete_pages():
        for frame in main_frame.winfo_children():
            frame.destroy()

    def indicate(lb, page):
        hide_indicators()
        delete_pages()
        page()
        lb.config(bg="white")  # Set active indicator to white

    # Sidebar Buttons
    options_frame = tk.Frame(root, bg="green", width=150)  # Set menu background to green
    options_frame.pack(side=tk.LEFT, fill=tk.Y)
    options_frame.configure(width=100, height=400)

    tk.Button(options_frame, text="X", font=("Bold", 10), bg="red", fg="white", bd=0, command=toggle_menu).place(x=70, y=10)

    home_bt = tk.Button(options_frame, text='Home', font=('Bold', 15), fg='white', bg='green', bd=0, command=lambda: indicate(home_indicate, home_page))
    home_bt.place(x=10, y=50)
    home_indicate = tk.Label(options_frame, text='', bg='green')
    home_indicate.place(x=3, y=50, width=5, height=40)

    soil_bt = tk.Button(options_frame, text='Soil', font=('Bold', 15), fg='white', bg='green', bd=0, command=lambda: indicate(soil_indicate, soil_page))
    soil_bt.place(x=10, y=100)
    soil_indicate = tk.Label(options_frame, text='', bg='green')
    soil_indicate.place(x=3, y=100, width=5, height=40)

    fertilizer_bt = tk.Button(options_frame, text='Fertilizer', font=('Bold', 15), fg='white', bg='green', bd=0, command=lambda: indicate(fertilizer_indicate, fertilizer_page))
    fertilizer_bt.place(x=10, y=150)
    fertilizer_indicate = tk.Label(options_frame, text='', bg='green')
    fertilizer_indicate.place(x=3, y=150, width=5, height=40)

    weather_bt = tk.Button(options_frame, text='Weather', font=('Bold', 15), fg='white', bg='green', bd=0, command=lambda: indicate(weather_indicate, weather_page))
    weather_bt.place(x=10, y=200)  # Adjusted to be at the bottom
    weather_indicate = tk.Label(options_frame, text='', bg='green')
    weather_indicate.place(x=3, y=200, width=5, height=40)

# Helper Function to Get Greeting
def get_greeting():
    current_hour = datetime.now().hour
    if current_hour < 12:
        return "Good Morning"
    elif current_hour < 18:
        return "Good Afternoon"
    elif current_hour < 21:
        return "Good Evening"
    else:
        return "Good Night"

# Splash Screen
splash_screen = tk.Frame(root)
splash_screen.pack(fill=tk.BOTH, expand=True)

splash_label = tk.Label(splash_screen, text="Starting Kisan Link", font=("Bold", 40), fg="green")
splash_label.pack(pady=200)

start_label = tk.Label(root, text="kissan..", font=("Arial", 20), fg="#075E54")

# Trigger Splash Screen Fade-in
root.after(0, fade_in_splash_screen)

root.mainloop()