import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import numpy as np

class App:
    def __init__(self, root, dimensiones):
        self.root = root
        self.root.title("Seleccionar Celdas")

        self.buttons = {}
        self.selected_cells = []
        #self.control_pos_cell = None
        #self.control_neg_cell = None
        self.control_pos_cells = []
        self.control_neg_cells = []       

        self.mode = "Ensayo"  # Modo predeterminado
        dimension_x, dimension_y = dimensiones
        # Botones de selección
        #self.cp_btn = tk.Button(self.root, text="C.P.", width=10, height=2, command=lambda: self.set_mode("C.P."))
        #self.cp_btn.grid(row=0, column=9)
        
        #self.cn_btn = tk.Button(self.root, text="C.N.", width=10, height=2, command=lambda: self.set_mode("C.N."))
        #self.cn_btn.grid(row=1, column=9)
        
        #self.ensayo_btn = tk.Button(self.root, text="Ensayo", width=10, height=2, command=lambda: self.set_mode("Ensayo"))
        #self.ensayo_btn.grid(row=2, column=9)
        # --- BOTONES DE MODO (A la derecha de la grilla) ---
        # Usamos column=dimension_x para que siempre esté después de la última columna
        self.cp_btn = tk.Button(self.root, text="Control Positivo", width=15, height=2, command=lambda: self.set_mode("C.P."))
        self.cp_btn.grid(row=0, column=dimension_x, padx=15) 
                
        self.cn_btn = tk.Button(self.root, text="Control Negativo", width=15, height=2, command=lambda: self.set_mode("C.N."))
        self.cn_btn.grid(row=1, column=dimension_x, padx=15)
                
        self.ensayo_btn = tk.Button(self.root, text="Ensayo", width=15, height=2, command=lambda: self.set_mode("Ensayo"))
        self.ensayo_btn.grid(row=2, column=dimension_x, padx=15)

        
        row_labels = [chr(65 + i) for i in range(dimension_y)] # row_labels = ['A', 'B', 'C', 'D', 'E'] in case dimension_y = 5 

        # Crear botones para las celdas
        for i in range(dimension_y):
            for j in range(dimension_x):
                btn = tk.Button(self.root, text=f"{row_labels[i]}{j+1}", width=10, height=3, command=lambda i=i, j=j: self.toggle_cell(i, j))
                btn.grid(row=i, column=j)
                self.buttons[(i, j)] = btn

        # Botones de control
        self.ok_btn = tk.Button(self.root, text="OK", width=15, height=2, command=self.ok_pressed)
        self.ok_btn.grid(row=3, column=dimension_x, padx=15)
        
        self.back_btn = tk.Button(self.root, text="Regresar", width=15, height=2, command=self.reset_selection)
        self.back_btn.grid(row=4, column=dimension_x, padx=15)


    def set_mode(self, mode):
        self.mode = mode

    def toggle_cell(self, i, j):
        if self.mode == "Ensayo":
            if (i, j) in self.selected_cells:
                self.buttons[(i, j)].config(bg='SystemButtonFace')
                self.selected_cells.remove((i, j))
            else:
                self.buttons[(i, j)].config(bg='green')
                self.selected_cells.append((i, j))
        elif self.mode == "C.P.":
            #if self.control_pos_cell:
            #    self.buttons[self.control_pos_cell].config(bg='SystemButtonFace')
            #self.control_pos_cell = (i, j)
            #self.buttons[(i, j)].config(bg='blue')
            if (i, j) in self.control_pos_cells:
                self.buttons[(i, j)].config(bg='SystemButtonFace')
                self.control_pos_cells.remove((i, j))
            else:
                self.buttons[(i, j)].config(bg='blue')
                self.control_pos_cells.append((i, j))
        elif self.mode == "C.N.":
            if (i, j) in self.control_neg_cells:
                self.buttons[(i, j)].config(bg='SystemButtonFace')
                self.control_neg_cells.remove((i, j))
            else:
                self.buttons[(i, j)].config(bg='red')
                self.control_neg_cells.append((i, j))

    def ok_pressed(self):
        answer = messagebox.askquestion("Confirmar", "¿Está seguro de que estas son las celdas que quiere analizar?")
        if answer == 'yes':
            sorted_cells = sorted(self.selected_cells, key=lambda x: (x[0], x[1]))
            #print("Celdas seleccionadas:", [(i+1, j+1) for i, j in sorted_cells])
            #if self.control_pos_cell:
            #    pass
                #print("Control Positivo:", (self.control_pos_cell[0] + 1, self.control_pos_cell[1] + 1))
            #if self.control_neg_cell:
            #    pass
                #print("Control Negativo:", (self.control_neg_cell[0] + 1, self.control_neg_cell[1] + 1))
            if self.control_pos_cells:
                pass
                #print("Control Positivo:", (self.control_pos_cell[0] + 1, self.control_pos_cell[1] + 1))
            if self.control_neg_cells:
                pass
                #print("Control Negativo:", (self.control_neg_cell[0] + 1, self.control_neg_cell[1] + 1))
            self.root.quit()

    def reset_selection(self):
        for i, j in self.selected_cells:
            self.buttons[(i, j)].config(bg='SystemButtonFace')
        #if self.control_pos_cell:
          #  self.buttons[self.control_pos_cell].config(bg='SystemButtonFace')
        #if self.control_neg_cell:
         #   self.buttons[self.control_neg_cell].config(bg='SystemButtonFace')
        if self.control_pos_cells:
            self.buttons[self.control_pos_cells].config(bg='SystemButtonFace')
        if self.control_neg_cells:
            self.buttons[self.control_neg_cells].config(bg='SystemButtonFace')
        self.selected_cells.clear()
        self.control_pos_cells.clear()
        self.control_neg_cells.clear()
        self.mode = "Ensayo"  # Reiniciar al modo predeterminado

    def get_selected_cells(self):
        sorted_cells = sorted(self.selected_cells, key=lambda x: (x[0], x[1]))
        results = {
            "Muestras": [(i+1, j+1) for i, j in sorted_cells],
            #"Control Positivo": None if not self.control_pos_cell else (self.control_pos_cell[0] + 1, self.control_pos_cell[1] + 1),
            #"Control Negativo": None if not self.control_neg_cell else (self.control_neg_cell[0] + 1, self.control_neg_cell[1] + 1)
            "Control Positivo": [(i+1, j+1) for i, j in sorted(self.control_pos_cells)],
            "Control Negativo": [(i+1, j+1) for i, j in sorted(self.control_neg_cells)]
        }
        return results


class DialogoNumeroTratamientos(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.resultado = None
        tk.Label(self, text="¿Cuántos tratamientos va a analizar?").pack(pady=20)
        tk.Button(self, text="1 Tratamiento", command=lambda: self.set_result(1)).pack(side=tk.LEFT, padx=20)
        tk.Button(self, text="2 Tratamientos", command=lambda: self.set_result(2)).pack(side=tk.RIGHT, padx=20)

    def set_result(self, valor):
        self.resultado = valor
        self.destroy()

def main(dimensiones):

    root = tk.Tk()
    root.withdraw()  # Ocultar la ventana principal

    # Crear y mostrar el diálogo
    dialogo = DialogoNumeroTratamientos(root)
    root.wait_window(dialogo)

    # Comprobar si se ha establecido un resultado
    if dialogo.resultado is None:
        print("No se seleccionó ningún número de tratamientos. Saliendo.")
        return

    num_tratamientos = dialogo.resultado

    # Mostrar la ventana principal
    root.deiconify()
    
    app = App(root, dimensiones)
    resultados = {}

    for tratamiento in range(1, num_tratamientos + 1):
        # Restablecer selecciones previas
        app.reset_selection()

        # Mostrar mensaje para seleccionar celdas del tratamiento actual
        messagebox.showinfo("Información", f"Seleccione las celdas del tratamiento {tratamiento}")

        root.mainloop()
        
        # Almacenar resultados
        resultados[f"Tratamiento {tratamiento}"] = app.get_selected_cells()

    # Imprimir resultados
    imprimir = False
    if imprimir:
        for tratamiento, celdas in resultados.items():
            print(tratamiento)
            print("Celdas seleccionadas:", celdas["Celdas"])
            if celdas["Control Positivo"]:
                print("Control Positivo:", celdas["Control Positivo"])
            if celdas["Control Negativo"]:
                print("Control Negativo:", celdas["Control Negativo"])
            print()

    return resultados

if __name__ == "__main__":
    dimensiones = (8, 5)
    main(dimensiones)


def set_values():
        entry_t_interval=int(entry_t_interval.get())
        entry_threshold_images=int(entry_threshold_images.get())
        entry_threshold_graph= int(entry_threshold_graph.get())
        entry_file_name_csv=str(entry_file_name_csv.get())
        entry_folder_name=str(entry_folder_name.get())
        entry_time_choose_image=int(entry_time_choose_image.get())

'''
def initial_settings():
    #Intrace for initial settings
    root = tk.Tk()
    root.title("Configuracion inicial")
    #t_interval, threshold_images, threshold_graphs, file_name_csv, folder_name, time_choose_image

    # Set interval
    tk.Label(root, text="Definir tiempo, ¿Cada cuántos minutos se tomó cada imagen?: ").pack(padx=10, pady=5)
    entry_t_interval = tk.Entry(root)
    entry_t_interval.pack(padx=10, pady=5)

    tk.Label(root, text="Umbral de binarizacion (deteccion de circulos): ").pack(padx=10, pady=5)
    entry_threshold_images = tk.Entry(root)
    entry_threshold_images.pack(padx=10, pady=5)

    tk.Label(root, text="Umbral de positivos:").pack(padx=10, pady=5)
    entry_threshold_graph = tk.Entry(root)
    entry_threshold_graph.pack(padx=10, pady=5)

    tk.Label(root, text="Nombre del archivo csv reporte de temperatura: ").pack(padx=10, pady=5)
    entry_file_name_csv = tk.Entry(root)
    entry_file_name_csv.pack(padx=10, pady=5)

    tk.Label(root, text="Nombre de la carpeta donde se guardaron las imágenes: ").pack(padx=10, pady=5)
    entry_folder_name = tk.Entry(root)
    entry_folder_name.pack(padx=10, pady=5)

    tk.Label(root, text="Escoger el tiempo de la imagen para deteccion de circulos: (prefereiblemente final o inicial): ").pack(padx=10, pady=5)
    entry_time_choose_image = tk.Entry(root)
    entry_time_choose_image.pack(padx=10, pady=5)

    btn_capturar = tk.Button(root, text="Guardar", command=set_values)
    btn_capturar.pack(padx=10, pady=20)

    values=[entry_t_interval, entry_threshold_images, entry_threshold_graph, entry_file_name_csv, entry_folder_name, entry_time_choose_image]

    return values
'''
def initial_settings():
    settings_result = {}
    root = tk.Tk()
    root.title("Configuración Inicial con Validación")

    ##1. VALIDATION LOGIC
    # This function checks if the new text is either completely empty (allowing deletions)
    # or if it consists only of digits (numbers).
    # This version allows digits, empty strings, and a single leading negative sign
    def validate_only_numbers(P):
        if P == "" or P == "-":
            return True
        # Check if it's a digit, or if it's a negative number
        if P.isdigit() or (P.startswith("-") and P[1:].isdigit()):
            return True
        return False

    # Register the validation function with the Tkinter root
    vcmd_numbers = root.register(validate_only_numbers)

    ##2. THE INTERFACE
    # Row 0 Time Interval (Numbers only + Default Value)
    tk.Label(root, text="Indique cada cuantos minutos se tomaron las fotos:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
    entry_t_interval = tk.Entry(
        root, 
        validate="key",                     # Trigger validation on keystroke
        validatecommand=(vcmd_numbers, '%P') # '%P' passes the value of the entry if the edit is allowed
    )
    entry_t_interval.grid(row=0, column=1, padx=12, pady=5)
    
    # Setting a Default Value:
    entry_t_interval.insert(0, 1) # Inserts 1 minute by default
    # Row 1 Image Threshold (Numbers only + Default Value)
    tk.Label(root, text="Umbral binarización (0-255), aunque es 16 por defecto puede verificar que valor usar cuando aparezca la deteccion de objetos:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
    entry_threshold_images = tk.Entry(root, validate="key", validatecommand=(vcmd_numbers, '%P'))
    entry_threshold_images.grid(row=1, column=1, padx=12, pady=5)
    
    # Setting a Default Value:
    entry_threshold_images.insert(0, 16)


    # Row 2 File Name (Standard text - No restriction needed, but with a default)
    tk.Label(root, text="Nombre archivo CSV con reporte de temperatura en °C (no incluir extension .csv):").grid(row=2, column=0, padx=10, pady=5, sticky="w")
    entry_file_name_csv = tk.Entry(root)
    entry_file_name_csv.grid(row=2, column=1, padx=12, pady=5)
    
    # Setting a Default Value:
    entry_file_name_csv.insert(0, "reporte_temperatura")


    # Row 3: 
    tk.Label(root, text="Umbral para determinar positivos (20 por defecto)").grid(row=3, column=0, padx=10, pady=5, sticky="w")
    entry_threshold_graph = tk.Entry(root)
    entry_threshold_graph.grid(row=3, column=1, padx=12, pady=5)
    # Setting a Default Value:
    entry_threshold_graph.insert(0, 20)

    # Row 4: 
    tk.Label(root, text="Carpeta donde se encuentra el archivo .ome.tif y ...metadata.txt (Verificar si hay carpeta interna incluirla en la direccion y escribirla eg: carpeta/carpeta_interna):").grid(row=4, column=0, padx=10, pady=5, sticky="w")
    entry_folder_name = tk.Entry(root)
    entry_folder_name.grid(row=4, column=1, padx=12, pady=5)
    # Setting a Default Value:
    entry_folder_name.insert(0, "photos_treatments_06052026/06052026_test_in_OneFile")

    # Row 5: 
    tk.Label(root, text="Tiempo de imagen para realizar la deteccion de los circulos (Poner -1 si la imagen del tiempo final):").grid(row=5, column=0, padx=10, pady=5, sticky="w")
    entry_time_choose_image = tk.Entry(root)
    entry_time_choose_image.grid(row=5, column=1, padx=12, pady=5)
    # Setting a Default Value:
    entry_time_choose_image.insert(0, -1)
    # Row 6:
    tk.Label(root, text='El area de recorte por defecto es: (x1,y1):(70,190) y (x2,y2):(570,428), puede seleccionar uno nuevo a continuación o solamente darle confirmar si desea mantenerlo').grid(row=6, column=0, padx=10, pady=5, sticky="w")

    #crop_coords = {"x1": 70, "y1": 90, "x2": 570, "y2": 428}   
    
    # --- Save Action ---
    def save_and_close():
        settings_result['entry_t_interval'] = int(entry_t_interval.get())
        settings_result['entry_threshold_images'] = float(entry_threshold_images.get())
        settings_result['entry_file_name_csv'] = entry_file_name_csv.get()
        settings_result['entry_threshold_graph']=float(entry_threshold_graph.get())
        settings_result['entry_folder_name']=entry_folder_name.get()
        if int(entry_time_choose_image.get())<0:
            settings_result['entry_time_choose_image']=int(entry_time_choose_image.get())
        else:
            settings_result['entry_time_choose_image']=int(entry_time_choose_image.get())//int(entry_t_interval.get())
        root.destroy()

    btn_capturar = tk.Button(root, text="Guardar Configuración", command=save_and_close)#, bg="#4CAF50", fg="white")
    btn_capturar.grid(row=7, column=0, columnspan=2, pady=20)

    root.mainloop()
    return settings_result

def get_crop_coordinates(image_ndarray, pixel_x_1, pixel_y_1, pixel_x_2, pixel_y_2):
    """
    Opens a window showing the image, allows the user to click and drag 
    to select a crop zone, and returns (x1, y1, x2, y2).
    """

    #new_root=tk.Tk()
    #new_root.title("whatsup")
    # Dictionary to store coordinates across inner functions 
    crop_coords = {"x1": pixel_x_1, "y1": pixel_y_1, "x2": pixel_x_2, "y2": pixel_y_2, "rect_id":None}
    # 1. CONVERSION STEP: 
    # OpenCV uses BGR, but PIL/Tkinter expects RGB.
    # If your array is already RGB, you can skip the '[:, :, ::-1]' flip.
    #prueba=image_ndarray[3, 1, :, :, :]
    #print(image_ndarray.shape, 'prueba: ', prueba.shape)
    
    rgb_array = image_ndarray[-1, 1, :, :, :]
    #rgb_array = image_ndarray.astype(np.uint8)
    #rgb_array= rgb_array[:,:,::-1]
    pil_image = Image.fromarray(rgb_array)
    #pil_image.show()
    height, width = int(pil_image.size[1]), int(pil_image.size[0])

    # FIX: Explicitly tie this window to the main parent window

    # 2. WINDOW SETUP
    # Note: If this function is called from an already existing Tkinter app, 
    # use tk.Toplevel() instead of tk.Tk()
    crop_win = tk.Tk()
    crop_win.title("Selecciona el área de corte")
    
    canvas = tk.Canvas(crop_win, width=width, height=height)
    canvas.pack()
    
    tk_img = ImageTk.PhotoImage(pil_image)
    canvas.create_image(0, 0, anchor="nw", image=tk_img)
    canvas.image = tk_img # Keep a reference!

    # 3. MOUSE INTERACTION LOGIC
    def on_button_press(event):
        # Save start drag position
        crop_coords["x1"] = event.x
        crop_coords["y1"] = event.y
        # Create a new rectangle if it doesn't exist yet
        if crop_coords["rect_id"]:
            canvas.delete(crop_coords["rect_id"])
        crop_coords["rect_id"] = canvas.create_rectangle(crop_coords["x1"], crop_coords["y1"], crop_coords["x1"], crop_coords["y1"], outline="red", width=2)

    def on_move_press(event):
        crop_coords["x2"] = event.x
        crop_coords["y2"] = event.y
        # Expand rectangle as user drags
        canvas.coords(crop_coords["rect_id"], crop_coords["x1"], crop_coords["y1"], crop_coords["x2"], crop_coords["y2"])

    def on_button_release(event):
        crop_coords["x2"] = event.x
        crop_coords["y2"] = event.y

    # Bind the mouse events to the canvas
    canvas.bind("<ButtonPress-1>", on_button_press)
    canvas.bind("<B1-Motion>", on_move_press)
    canvas.bind("<ButtonRelease-1>", on_button_release)

    # 4. CONFIRMATION & CLOSING
    def confirm_selection():
        if crop_coords["x1"] == crop_coords["x2"] or crop_coords["y1"] == crop_coords["y2"]:
            messagebox.showwarning("Atención", "Por favor selecciona un área válida.")
            return
        # This breaks the mainloop and proceeds to the return statement
        crop_win.quit() 
        crop_win.destroy()

    btn_confirm = tk.Button(crop_win, text="Confirmar Recorte", command=confirm_selection)
    btn_confirm.pack(pady=10)
    
    # 5. THE HALTING MECHANISM
    # This prevents the function from returning immediately 
    crop_win.mainloop() 
    
    return (crop_coords["x1"], crop_coords["y1"], crop_coords["x2"], crop_coords["y2"])

    '''
    #crop_win = tk.Toplevel(new_root) 
    crop_win=tk.Tk()
    crop_win.title("Selecciona el área de corte")
    
    # Make this window modal (blocks interaction with the main settings window until closed)
    crop_win.grab_set() 

    #crop_win.transient() # Keeps it physically on top of the parent window

    canvas = tk.Canvas(crop_win, width=width, height=height)
    canvas.pack()
    
    tk_img = ImageTk.PhotoImage(pil_image)
    canvas.create_image(0, 0, anchor="nw", image=tk_img)

    # ... [Keep your mouse binding logic here exactly the same] ...

    def confirm_selection():
        if crop_coords["x1"] == crop_coords["x2"] or crop_coords["y1"] == crop_coords["y2"]:
            messagebox.showwarning("Atención", "Por favor selecciona un área válida.")
            return
        crop_win.destroy()

    btn_confirm = tk.Button(crop_win, text="Confirmar Recorte", command=confirm_selection)
    btn_confirm.pack(pady=10)

    canvas.image = tk_img 
    
    # FIX: Use wait_window on the child window so execution pauses until it's closed
    #parent.wait_window(crop_win)
    #crop_win.wait_window()
    
    return (crop_coords["x1"], crop_coords["y1"], crop_coords["x2"], crop_coords["y2"])
    '''
