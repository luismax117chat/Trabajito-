import tkinter as tk
from tkinter import messagebox
import cafeteriaback
from PIL import Image, ImageTk
from cafeteriaback import Persona
import json
import os
import sys

class CafeteriaApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Cafetería - Sistema de Pedidos")

        import cafeteriaback
        print(f"Ruta del archivo de productos: {cafeteriaback.ARCHIVO_PRODUCTOS}")
        print(f"Contenido de cafeteriaback: {cafeteriaback.__file__}")
        print(f"cargar_productos_json en cafeteriaback: {cafeteriaback.cargar_productos_json}")
        self.menu_productos = cafeteriaback.cargar_productos_json()
        self.inventario = cafeteriaback.Inventario()  # Inicializa self.inventario usando la clase del backend
        self.load_inventory_from_json()
        self.cargar_datos_iniciales()

        self.mostrar_pantalla_inicio()

    def cargar_datos_iniciales(self):
        personas_cargadas = cafeteriaback.cargar_personas_json()
        cafeteriaback.Persona.personas_registradas = personas_cargadas

    def load_inventory_from_json(self):
        # Cambiado la ruta a "data/productos.json"
        if os.path.exists("data/productos.json"):
            with open("data/productos.json", 'r') as f:
                try:
                    data = json.load(f)
                    for item in data.get("productos", []):
                        nombre = item.get("producto")
                        cantidad = item.get("cantidad", 0)
                        if nombre:
                            if nombre in self.inventario.stock: # Verifica si el producto ya está en el inventario
                                self.inventario.stock[nombre] = cantidad
                            else:
                                self.inventario.stock[nombre] = cantidad # Si no existe, lo añade
                except json.JSONDecodeError:
                    print("Error al decodificar productos.json para el inventario")

    def save_inventory_to_json(self):
        inventario_data = {"productos": []}
        for producto in self.menu_productos:
            cantidad = self.inventario.stock.get(producto.producto, 0)
            inventario_data["productos"].append({
                "producto": producto.producto,
                "cantidad": cantidad
            })
        # Cambiado la ruta a "data/productos.json"
        with open("data/productos.json", "w") as f:
            json.dump(inventario_data, f, indent=4)

    def mostrar_pantalla_inicio(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        try:
            # Construir la ruta de forma relativa al script
            script_dir = os.path.dirname(os.path.abspath(__file__))
            image_path = os.path.join(script_dir, "imagenes", "cafeteria-en-puebla.jpg") 
            logo = Image.open(image_path).resize((600, 400))
            self.logo_img = ImageTk.PhotoImage(logo)
            logo_label = tk.Label(self.root, image=self.logo_img)
            logo_label.pack(pady=10)
        except FileNotFoundError:
            print("Error: No se encontró la imagen del logo.")

        tk.Label(self.root, text="Bienvenido a la Cafetería", font=("Arial", 16)).pack(pady=20)
        tk.Button(self.root, text="Soy Cliente", command=self.mostrar_menu_cliente).pack(pady=10)
        tk.Button(self.root, text="Soy Empleado", command=self.mostrar_menu_empleado).pack(pady=10)

    def mostrar_menu_cliente(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        try:
            # Ruta relativa
            script_dir = os.path.dirname(os.path.abspath(__file__))
            image_path = os.path.join(script_dir, "imagenes", "cafeteria-cafe-1571841265380_v2_450x800.jpg")

            cliente_img = Image.open(image_path).resize((200, 80))
            self.cliente_imagen = ImageTk.PhotoImage(cliente_img)
            cliente_label = tk.Label(self.root, image=self.cliente_imagen)
            cliente_label.pack(pady=10)

        except FileNotFoundError:
            print(f"Error: No se encontró la imagen del menú de cliente en: {image_path}")

        tk.Label(self.root, text="Menú de Productos", font=("Arial", 14)).pack(pady=10)
        self.lista_productos_cliente = tk.Listbox(self.root, width=60)
        for producto in self.menu_productos:
            disponible = self.inventario.stock.get(producto.producto, 0)
            detalles = f"{producto.producto}: ${producto.precio} (Disponible: {disponible})"
            if isinstance(producto, cafeteriaback.Bebida):
                detalles += f" (Sabor: {producto.sabor}, Tamaño: {producto.tamaño})"
            elif isinstance(producto, cafeteriaback.Postre):
                detalles += f" (Azúcar: {producto.azucar}, Sin Azúcar: {producto.sinazucar})"
            self.lista_productos_cliente.insert(tk.END, detalles)
        self.lista_productos_cliente.bind('<<ListboxSelect>>', self.abrir_ventana_personalizacion)
        self.lista_productos_cliente.pack(padx=10, pady=10)

        self.sin_azucar_var = tk.BooleanVar()
        self.check_sin_azucar = tk.Checkbutton(self.root, text="Sin Azúcar", variable=self.sin_azucar_var)

        self.cantidad_cliente_label = tk.Label(self.root, text="Cantidad:", font=("Arial", 12))
        self.cantidad_cliente_entry = tk.Entry(self.root, width=10)
        self.agregar_al_pedido_btn = tk.Button(self.root, text="Agregar al Pedido", command=self.agregar_al_pedido)

        # Nuevo Listbox para mostrar pedido seleccionable
        self.pedido_cliente_listbox = tk.Listbox(self.root, width=50, height=6)
        self.pedido_cliente_listbox.pack(padx=10, pady=10)

        # Botón para eliminar producto del pedido
        tk.Button(self.root, text="Eliminar Producto del Pedido", command=self.eliminar_producto_pedido).pack(pady=5)
        tk.Button(self.root, text="Ver Total y Disponibilidad", command=self.ver_total_disponibilidad).pack(pady=10)
        tk.Button(self.root, text="Confirmar Pedido", command=self.confirmar_pedido).pack(pady=10)
        tk.Button(self.root, text="Volver al Inicio", command=self.mostrar_pantalla_inicio).pack(pady=5)

        self.pedido_cliente = {}
        self.producto_seleccionado = None

    def abrir_ventana_personalizacion(self, event):
        seleccion = self.lista_productos_cliente.curselection()
        if seleccion:
            indice = seleccion[0]
            self.producto_seleccionado = self.menu_productos[indice]
            self.sin_azucar_var.set(False) # Resetear el checkbutton

            if isinstance(self.producto_seleccionado, cafeteriaback.Bebida):
                self.check_sin_azucar.pack_forget() # Ocultar si es bebida
                self.mostrar_ventana_personalizacion_bebida()
            elif isinstance(self.producto_seleccionado, cafeteriaback.Postre):
                self.check_sin_azucar.pack() # Mostrar si es postre
                self.cantidad_cliente_label.pack()
                self.cantidad_cliente_entry.pack()
                self.agregar_al_pedido_btn.pack(pady=5)
            else:
                self.check_sin_azucar.pack_forget() # Ocultar si no es bebida ni postre
                self.cantidad_cliente_label.pack()
                self.cantidad_cliente_entry.pack()
                self.agregar_al_pedido_btn.pack(pady=5)

    def mostrar_ventana_personalizacion_bebida(self):
        ventana_personalizacion = tk.Toplevel(self.root)
        ventana_personalizacion.title(f"Personalizar {self.producto_seleccionado.producto}")

        tk.Label(ventana_personalizacion, text="Tamaño:", font=("Arial", 12)).pack(pady=5)
        tamaños = ["Pequeño", "Mediano", "Grande"]
        self.tamaño_seleccionado = tk.StringVar(ventana_personalizacion)
        self.tamaño_seleccionado.set(tamaños[1])
        tamaño_menu = tk.OptionMenu(ventana_personalizacion, self.tamaño_seleccionado, *tamaños)
        tamaño_menu.pack()

        tk.Label(ventana_personalizacion, text="Leche:", font=("Arial", 12)).pack(pady=5)
        tipos_leche = ["Normal", "Deslactosada", "Almendras", "Soya"]
        self.leche_seleccionada = tk.StringVar(ventana_personalizacion)
        self.leche_seleccionada.set(tipos_leche[0])
        leche_menu = tk.OptionMenu(ventana_personalizacion, self.leche_seleccionada, *tipos_leche)
        leche_menu.pack()

        tk.Label(ventana_personalizacion, text="Azúcar:", font=("Arial", 12)).pack(pady=5)
        niveles_azucar = ["Normal", "Poca", "Sin Azúcar", "Extra"]
        self.azucar_seleccionada = tk.StringVar(ventana_personalizacion)
        self.azucar_seleccionada.set(niveles_azucar[0])
        azucar_menu = tk.OptionMenu(ventana_personalizacion, self.azucar_seleccionada, *niveles_azucar)
        azucar_menu.pack()

        tk.Label(ventana_personalizacion, text="Cantidad:", font=("Arial", 12)).pack(pady=5)
        self.cantidad_personalizada_entry = tk.Entry(ventana_personalizacion, width=5)
        self.cantidad_personalizada_entry.insert(0, "1")
        self.cantidad_personalizada_entry.pack()

        boton_añadir_personalizado = tk.Button(ventana_personalizacion, text="Añadir al Pedido", command=self.agregar_bebida_personalizada)
        boton_añadir_personalizado.pack(pady=10)

    def agregar_bebida_personalizada(self):
        if self.producto_seleccionado:
            cantidad_str = self.cantidad_personalizada_entry.get()
            if cantidad_str.isdigit() and int(cantidad_str) > 0:
                cantidad = int(cantidad_str)
                nombre_personalizado = f"{self.producto_seleccionado.producto} ({self.tamaño_seleccionado.get()}, Leche {self.leche_seleccionada.get()}, Azúcar: {self.azucar_seleccionada.get()})"
                self.pedido_cliente[nombre_personalizado] = (cantidad, self.producto_seleccionado.precio)
                self.actualizar_texto_pedido_cliente()
                self.producto_seleccionado = None
                self.cantidad_cliente_label.pack_forget()
                self.cantidad_cliente_entry.pack_forget()
                self.agregar_al_pedido_btn.pack_forget()
                self.cantidad_cliente_entry.delete(0, tk.END)
                self.cantidad_personalizada_entry.master.destroy()
            else:
                messagebox.showerror("Error", "Cantidad inválida.")

    def agregar_al_pedido(self):
        if self.producto_seleccionado:
            cantidad_str = self.cantidad_cliente_entry.get()
            if cantidad_str.isdigit() and int(cantidad_str) > 0:
                cantidad = int(cantidad_str)
                disponible = self.inventario.stock.get(self.producto_seleccionado.producto, 0)
                if cantidad <= disponible:
                    nombre_producto = self.producto_seleccionado.producto
                    if isinstance(self.producto_seleccionado, cafeteriaback.Postre) and self.sin_azucar_var.get():
                        nombre_producto += " (Sin Azúcar)"
                    self.pedido_cliente[nombre_producto] = (cantidad, self.producto_seleccionado.precio)
                    self.actualizar_texto_pedido_cliente()
                    self.cantidad_cliente_entry.delete(0, tk.END)
                    self.producto_seleccionado = None
                    self.cantidad_cliente_label.pack_forget()
                    self.cantidad_cliente_entry.pack_forget()
                    self.agregar_al_pedido_btn.pack_forget()
                    self.check_sin_azucar.pack_forget() # Ocultar el checkbutton después de agregar
                else:
                    messagebox.showerror("Error", f"No hay suficiente stock de {self.producto_seleccionado.producto}.")
            else:
                messagebox.showerror("Error", "Cantidad inválida.")
        else:
            messagebox.showerror("Error", "Por favor, seleccione un producto.")

    def actualizar_texto_pedido_cliente(self):
        self.pedido_cliente_listbox.delete(0, tk.END)
        for item, detalles in self.pedido_cliente.items():
            cantidad, precio = detalles
            self.pedido_cliente_listbox.insert(tk.END, f"{item}: {cantidad}")


    def ver_total_disponibilidad(self):
        total = 0
        mensaje_disponibilidad = "Disponibilidad Actual:\n"
        for item, detalles in self.pedido_cliente.items():
            cantidad, precio_unitario = detalles
            nombre_base = item.split('(')[0].strip()
            producto = next((p for p in self.menu_productos if p.producto == nombre_base), None)
            if producto:
                total += precio_unitario * cantidad
                disponible = self.inventario.stock.get(nombre_base, 0)
                mensaje_disponibilidad += f"{item}: Pedido({cantidad}), Disponible({disponible})\n"
        messagebox.showinfo("Total del Pedido", f"Total: ${total:.2f}\n\n{mensaje_disponibilidad}")

    def confirmar_pedido(self):
        if self.pedido_cliente:
            ventana_info_cliente = tk.Toplevel(self.root)
            ventana_info_cliente.title("Información del Cliente")

            tk.Label(ventana_info_cliente, text="Nombre:", font=("Arial", 12)).pack(pady=5)
            nombre_entry = tk.Entry(ventana_info_cliente, width=30)
            nombre_entry.pack(pady=5)

            tk.Label(ventana_info_cliente, text="Teléfono:", font=("Arial", 12)).pack(pady=5)
            telefono_entry = tk.Entry(ventana_info_cliente, width=30)
            telefono_entry.pack(pady=5)

            def finalizar_confirmacion():
                nombre_cliente = nombre_entry.get()
                telefono_cliente = telefono_entry.get()

                if nombre_cliente and telefono_cliente:
                    cliente_fiel = False
                    for persona in Persona.personas_registradas:
                        if persona.nombre == nombre_cliente and persona.telefono == telefono_cliente:
                            cliente_fiel = True
                            break

                    total = 0
                    cantidad_productos_pedido = sum(detalles[0] for detalles in self.pedido_cliente.values())
                    detalle_pedido = "Tu pedido es:\n"
                    for item, detalles in self.pedido_cliente.items():
                        cantidad, precio_unitario = detalles
                        subtotal = precio_unitario * cantidad
                        total += subtotal
                        detalle_pedido += f"- {item}: {cantidad} x ${precio_unitario:.2f} = ${subtotal:.2f}\n"

                        nombre_base = item.split('(')[0].strip()
                        if nombre_base in self.inventario.stock:
                            self.inventario.actualizar_stock(nombre_base, -cantidad)

                    descuento_aplicado_fidelidad = 0.0
                    if cliente_fiel and cantidad_productos_pedido >= 3:
                        descuento_aplicado_fidelidad = total * 0.05
                        total -= descuento_aplicado_fidelidad
                        detalle_pedido += f"\nDescuento por fidelidad (5%): -${descuento_aplicado_fidelidad:.2f}"
                    elif cliente_fiel:
                        detalle_pedido += "\n(Descuento por fidelidad no aplicado: Necesitas 3 o más productos en tu pedido)"

                    detalle_pedido += f"\nTotal del pedido: ${total:.2f}"
                    messagebox.showinfo("Pedido Confirmado", detalle_pedido)
                    self.save_inventory_to_json()
                    self.pedido_cliente = {}
                    self.actualizar_texto_pedido_cliente()
                    ventana_info_cliente.destroy()
                else:
                    messagebox.showerror("Error", "Por favor, ingresa tu nombre y teléfono.")

            # ¡Aquí estaba faltando el botón!
            tk.Button(ventana_info_cliente, text="Verificar Fidelidad y Confirmar", command=finalizar_confirmacion).pack(pady=10)

        else:
            messagebox.showinfo("Pedido Vacío", "Tu pedido está vacío.")
    def eliminar_producto_pedido(self):
        seleccion = self.pedido_cliente_listbox.curselection()
        if seleccion:
            indice = seleccion[0]
            producto = list(self.pedido_cliente.keys())[indice]
            del self.pedido_cliente[producto]
            self.actualizar_texto_pedido_cliente()
        else:
            messagebox.showwarning("Sin selección", "Selecciona un producto para eliminar.")


    def mostrar_menu_empleado(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        
        try:
            # Construir la ruta de forma relativa
            script_dir = os.path.dirname(os.path.abspath(__file__))
            image_path = os.path.join(script_dir, "imagenes", "images (1)22.jfif")

            empleado_img = Image.open(image_path).resize((200, 80))
            self.empleado_imagen = ImageTk.PhotoImage(empleado_img)
            empleado_label = tk.Label(self.root, image=self.empleado_imagen)
            empleado_label.pack(pady=10)

        except FileNotFoundError:
            print(f"Error: No se encontró la imagen del menú de empleado en: {image_path}")  # Ruta en el error

        tk.Label(self.root, text="Menú de Empleado", font=("Arial", 14)).pack(pady=10)

        tk.Label(self.root, text="Gestión de Productos", font=("Arial", 12)).pack()
        tk.Button(self.root, text="Agregar Nuevo Producto", command=self.mostrar_agregar_producto).pack(pady=5)
        tk.Button(self.root, text="Eliminar Producto", command=self.mostrar_eliminar_producto).pack(pady=5)
        tk.Button(self.root, text="Modificar Productos", command=self.gestionar_productos_menu).pack(pady=5) # Mover botón aquí

        tk.Label(self.root, text="Gestión de Usuarios", font=("Arial", 12,)).pack(pady=10)
        tk.Button(self.root, text="Ver Usuarios", command=self.mostrar_ver_usuarios).pack(pady=5) # Cambiado a "Ver Usuarios"

        tk.Button(self.root, text="Volver al Inicio", command=self.mostrar_pantalla_inicio).pack(pady=10)

    def mostrar_agregar_producto(self):
        ventana_agregar = tk.Toplevel(self.root)
        ventana_agregar.title("Agregar Nuevo Producto")

        tk.Label(ventana_agregar, text="Tipo de Producto:", font=("Arial", 12)).pack()
        tipos_producto = ["Base", "Bebida", "Postre"]
        self.nuevo_tipo_producto = tk.StringVar(ventana_agregar)
        self.nuevo_tipo_producto.set(tipos_producto[0]) # Valor por defecto
        tipo_menu = tk.OptionMenu(ventana_agregar, self.nuevo_tipo_producto, *tipos_producto, command=self.mostrar_campos_producto)
        tipo_menu.pack(pady=5)

        self.campos_producto_frame = tk.Frame(ventana_agregar)
        self.campos_producto_frame.pack(padx=10, pady=10)

        # Campos base (nombre, precio, cantidad) - Siempre visibles
        tk.Label(self.campos_producto_frame, text="Nombre:", font=("Arial", 12)).grid(row=0, column=0, sticky="w")
        self.nuevo_nombre_entry = tk.Entry(self.campos_producto_frame, width=30)
        self.nuevo_nombre_entry.grid(row=0, column=1, padx=5)

        tk.Label(self.campos_producto_frame, text="Precio:", font=("Arial", 12)).grid(row=1, column=0, sticky="w")
        self.nuevo_precio_entry = tk.Entry(self.campos_producto_frame, width=30)
        self.nuevo_precio_entry.grid(row=1, column=1, padx=5)

        tk.Label(self.campos_producto_frame, text="Cantidad Inicial:", font=("Arial", 12)).grid(row=2, column=0, sticky="w")
        self.nuevo_cantidad_entry = tk.Entry(self.campos_producto_frame, width=30)
        self.nuevo_cantidad_entry.grid(row=2, column=1, padx=5)

        self.campos_especificos = {} # Diccionario para guardar widgets específicos

        tk.Button(ventana_agregar, text="Agregar Producto", command=self.agregar_nuevo_producto).pack(pady=10)

    def mostrar_campos_producto(self, tipo):
        # Destruir campos específicos anteriores
        for widget in self.campos_especificos.values():
            widget.destroy()
        self.campos_especificos = {}

        if tipo == "Bebida":
            tk.Label(self.campos_producto_frame, text="Sabor:", font=("Arial", 12)).grid(row=3, column=0, sticky="w")
            self.campos_especificos["sabor"] = tk.Entry(self.campos_producto_frame, width=30)
            self.campos_especificos["sabor"].grid(row=3, column=1, padx=5)

            tk.Label(self.campos_producto_frame, text="Tamaño:", font=("Arial", 12)).grid(row=4, column=0, sticky="w")
            self.campos_especificos["tamaño"] = tk.Entry(self.campos_producto_frame, width=30)
            self.campos_especificos["tamaño"].grid(row=4, column=1, padx=5)

        elif tipo == "Postre":
            self.campos_especificos["azucar_var"] = tk.BooleanVar()
            check_azucar = tk.Checkbutton(self.campos_producto_frame, text="Con Azúcar", variable=self.campos_especificos["azucar_var"])
            check_azucar.grid(row=3, column=0, columnspan=2, sticky="w")

            self.campos_especificos["sinazucar_var"] = tk.BooleanVar()
            check_sinazucar = tk.Checkbutton(self.campos_producto_frame, text="Sin Azúcar", variable=self.campos_especificos["sinazucar_var"])
            check_sinazucar.grid(row=4, column=0, columnspan=2, sticky="w")

        # Reconfigurar las filas para que se muestren correctamente
        for i in range(5):
            self.campos_producto_frame.grid_rowconfigure(i, weight=1)

    def agregar_nuevo_producto(self):
        tipo = self.nuevo_tipo_producto.get()
        nombre = self.nuevo_nombre_entry.get()
        precio_str = self.nuevo_precio_entry.get()
        cantidad_str = self.nuevo_cantidad_entry.get()

        if nombre and precio_str.replace('.', '', 1).isdigit() and cantidad_str.isdigit():
            precio = float(precio_str)
            cantidad = int(cantidad_str)

            if tipo == "Base":
                nuevo_producto = cafeteriaback.ProductoBase(nombre, precio)
            elif tipo == "Bebida":
                sabor = self.campos_especificos.get("sabor").get()
                tamaño = self.campos_especificos.get("tamaño").get()
                if sabor and tamaño:
                    nuevo_producto = cafeteriaback.Bebida(nombre, precio, sabor, tamaño)
                else:
                    messagebox.showerror("Error", "Por favor, complete sabor y tamaño para la bebida.")
                    return
            elif tipo == "Postre":
                azucar = self.campos_especificos.get("azucar_var").get()
                sinazucar = self.campos_especificos.get("sinazucar_var").get()
                nuevo_producto = cafeteriaback.Postre(nombre, precio, azucar, sinazucar)

            if nuevo_producto:
                self.menu_productos.append(nuevo_producto)
                self.inventario.stock[nombre] = cantidad
                self.save_inventory_to_json()
                messagebox.showinfo("Éxito", f"Producto '{nombre}' ({tipo}) agregado.")
                # Opcional: Cerrar la ventana de agregar producto
                # self.mostrar_agregar_producto().master.destroy()
            return
        else:
            messagebox.showerror("Error", "Por favor, complete nombre, precio y cantidad correctamente.")

    def mostrar_eliminar_producto(self):
        ventana_eliminar = tk.Toplevel(self.root)
        ventana_eliminar.title("Eliminar Producto")

        tk.Label(ventana_eliminar, text="Seleccionar Producto a Eliminar:", font=("Arial", 12)).pack()
        lista_productos = tk.Listbox(ventana_eliminar, width=70)
        for producto in self.menu_productos:
            tipo = "Bebida" if isinstance(producto, cafeteriaback.Bebida) else "Postre" if isinstance(producto, cafeteriaback.Postre) else "Base"
            detalles = f"[{tipo}] {producto.producto}: ${producto.precio}"
            if isinstance(producto, cafeteriaback.Bebida):
                detalles += f", Sabor: {producto.sabor}, Tamaño: {producto.tamaño}"
            elif isinstance(producto, cafeteriaback.Postre):
                detalles += f", Azúcar: {producto.azucar}, Sin Azúcar: {producto.sinazucar}"
            lista_productos.insert(tk.END, detalles)
        lista_productos.pack(padx=10, pady=10)

        def eliminar_producto():
            seleccion = lista_productos.curselection()
            if seleccion:
                indice = seleccion[0]
                producto_a_eliminar = self.menu_productos[indice]
                confirmar = messagebox.askyesno("Confirmar", f"¿Eliminar '{producto_a_eliminar.producto}'?")
                if confirmar:
                    if producto_a_eliminar.producto in self.inventario.stock:
                        del self.inventario.stock[producto_a_eliminar.producto]
                    self.menu_productos.pop(indice)
                    self.save_inventory_to_json()
                    messagebox.showinfo("Éxito", f"Producto '{producto_a_eliminar.producto}' eliminado.")
                    ventana_eliminar.destroy()
            else:
                messagebox.showerror("Error", "Selecciona un producto para eliminar.")

        tk.Button(ventana_eliminar, text="Eliminar Producto", command=eliminar_producto).pack(pady=10)

    def mostrar_ver_usuarios(self):
        ventana_ver_usuarios = tk.Toplevel(self.root)
        ventana_ver_usuarios.title("Usuarios Registrados")
        lista_usuarios = tk.Listbox(ventana_ver_usuarios, width=60)
        self.usuarios_mostrados = []  # Lista para mantener los usuarios en el orden de la Listbox

        # Mostrar todos los usuarios en el Listbox
        for persona in cafeteriaback.Persona.personas_registradas:
            detalles = f"Nombre: {persona.nombre}, Teléfono: {persona.telefono}"
            if isinstance(persona, cafeteriaback.Empleado):
                detalles += f", Rol: {persona.puesto}"
            elif isinstance(persona, cafeteriaback.Cliente):
                detalles += f", Tipo: Cliente"
            lista_usuarios.insert(tk.END, detalles)
            self.usuarios_mostrados.append(persona)  # Añadir a la lista mostrada

        lista_usuarios.pack(padx=10, pady=5)

        tk.Label(ventana_ver_usuarios, text="Nuevo Nombre (opcional):", font=("Arial", 12)).pack()
        nuevo_nombre_entry = tk.Entry(ventana_ver_usuarios, width=30)
        nuevo_nombre_entry.pack()

        tk.Label(ventana_ver_usuarios, text="Nuevo Teléfono (opcional):", font=("Arial", 12)).pack()
        nuevo_telefono_entry = tk.Entry(ventana_ver_usuarios, width=30)
        nuevo_telefono_entry.pack()

        tk.Label(ventana_ver_usuarios, text="Nuevo Rol (solo empleados):", font=("Arial", 12)).pack()
        nuevo_rol_entry = tk.Entry(ventana_ver_usuarios, width=30)
        nuevo_rol_entry.pack()

        def actualizar_usuario():
            seleccion = lista_usuarios.curselection()
            if seleccion:
                indice = seleccion[0]
                if 0 <= indice < len(self.usuarios_mostrados):
                    persona_a_modificar = self.usuarios_mostrados[indice]
                    nuevo_nombre = nuevo_nombre_entry.get()
                    nuevo_telefono = nuevo_telefono_entry.get()
                    nuevo_rol = nuevo_rol_entry.get()

                    # Modificar los atributos de la persona seleccionada
                    if nuevo_nombre:
                        persona_a_modificar.nombre = nuevo_nombre
                    if nuevo_telefono:
                        persona_a_modificar.telefono = nuevo_telefono
                    if isinstance(persona_a_modificar, cafeteriaback.Empleado) and nuevo_rol:
                        persona_a_modificar.puesto = nuevo_rol

                    # Guardar las modificaciones en el archivo JSON
                    cafeteriaback.guardar_personas_json()

                    messagebox.showinfo("Éxito", "Datos de usuario actualizados.")

                    # Refrescar la lista de usuarios en la interfaz
                    lista_usuarios.delete(0, tk.END)
                    self.usuarios_mostrados = []
                    for persona in cafeteriaback.Persona.personas_registradas:
                        detalles = f"Nombre: {persona.nombre}, Teléfono: {persona.telefono}"
                        if isinstance(persona, cafeteriaback.Empleado):
                            detalles += f", Rol: {persona.puesto}"
                        elif isinstance(persona, cafeteriaback.Cliente):
                            detalles += f", Tipo: Cliente"
                        lista_usuarios.insert(tk.END, detalles)
                        self.usuarios_mostrados.append(persona)

                    nuevo_nombre_entry.delete(0, tk.END)
                    nuevo_telefono_entry.delete(0, tk.END)
                    nuevo_rol_entry.delete(0, tk.END)
                else:
                    messagebox.showerror("Error", "Índice de usuario inválido.")
            else:
                messagebox.showerror("Error", "Selecciona un usuario.")

        def crear_nuevo_usuario():
            nuevo_nombre = nuevo_nombre_entry.get()
            nuevo_telefono = nuevo_telefono_entry.get()
            nuevo_rol = nuevo_rol_entry.get()

            if not nuevo_nombre or not nuevo_telefono:
                messagebox.showerror("Error", "Debe ingresar nombre y teléfono.")
                return

            # Crear nuevo usuario, ya sea cliente o empleado
            if nuevo_rol:  # Si tiene rol, es un empleado
                nuevo_usuario = cafeteriaback.Empleado(nuevo_nombre, 0, nuevo_telefono, nuevo_rol) # Edad por defecto 0
            else:  # Si no tiene rol, es un cliente
                nuevo_usuario = cafeteriaback.Cliente(nuevo_nombre, 0, nuevo_telefono) # Edad por defecto 0

            # Añadir el nuevo usuario a la lista
            cafeteriaback.Persona.personas_registradas.append(nuevo_usuario)

            # Guardar el nuevo usuario en el archivo JSON
            cafeteriaback.guardar_personas_json()

            messagebox.showinfo("Éxito", "Nuevo usuario creado.")

            # Refrescar la lista de usuarios
            lista_usuarios.delete(0, tk.END)
            self.usuarios_mostrados = []
            for persona in cafeteriaback.Persona.personas_registradas:
                detalles = f"Nombre: {persona.nombre}, Teléfono: {persona.telefono}"
                if isinstance(persona, cafeteriaback.Empleado):
                    detalles += f", Rol: {persona.puesto}"
                elif isinstance(persona, cafeteriaback.Cliente):
                    detalles += f", Tipo: Cliente"
                lista_usuarios.insert(tk.END, detalles)
                self.usuarios_mostrados.append(persona)

            nuevo_nombre_entry.delete(0, tk.END)
            nuevo_telefono_entry.delete(0, tk.END)
            nuevo_rol_entry.delete(0, tk.END)

        # Botón para crear un nuevo usuario
        tk.Button(ventana_ver_usuarios, text="Crear Nuevo Usuario", command=crear_nuevo_usuario).pack(pady=10)

        tk.Button(ventana_ver_usuarios, text="Actualizar Usuario", command=actualizar_usuario).pack(pady=10)


    def gestionar_productos_menu(self):
        ventana = tk.Toplevel(self.root)
        ventana.title("Gestionar Productos")

        tk.Label(ventana, text="Modificar Producto Existente", font=("Arial", 14, "bold")).pack(pady=5)
        tk.Label(ventana, text="Seleccionar Producto:", font=("Arial", 12)).pack()
        lista_productos = tk.Listbox(ventana, width=70)
        for producto in self.menu_productos:
            tipo = "Bebida" if isinstance(producto, cafeteriaback.Bebida) else "Postre" if isinstance(producto, cafeteriaback.Postre) else "Base"
            detalles = f"[{tipo}] {producto.producto}: ${producto.precio}"
            if isinstance(producto, cafeteriaback.Bebida):
                detalles += f", Sabor: {producto.sabor}, Tamaño: {producto.tamaño}"
            elif isinstance(producto, cafeteriaback.Postre):
                detalles += f", Azúcar: {producto.azucar}, Sin Azúcar: {producto.sinazucar}"
            lista_productos.insert(tk.END, detalles)
        lista_productos.pack(padx=10, pady=5)

        tk.Label(ventana, text="Nuevo Precio (opcional):", font=("Arial", 12)).pack()
        nuevo_precio_entry = tk.Entry(ventana, width=10)
        nuevo_precio_entry.pack()

        tk.Label(ventana, text="Cantidad a Agregar/Quitar (opcional):", font=("Arial", 12)).pack()
        cantidad_entry = tk.Entry(ventana, width=10)
        cantidad_entry.pack()

        def aplicar_cambios():
            seleccion = lista_productos.curselection()
            if seleccion:
                indice = seleccion[0]
                producto = self.menu_productos[indice]

                precio_txt = nuevo_precio_entry.get()
                if precio_txt:
                    try:
                        nuevo_precio = float(precio_txt)
                        producto.precio = nuevo_precio
                        messagebox.showinfo("Precio actualizado", f"Nuevo precio de '{producto.producto}': ${nuevo_precio:.2f}")
                    except ValueError:
                        messagebox.showerror("Error", "Precio inválido")

                cantidad_txt = cantidad_entry.get()
                if cantidad_txt.lstrip('-').isdigit():
                    cantidad = int(cantidad_txt)
                    if producto.producto in self.inventario.stock:
                        self.inventario.actualizar_stock(producto.producto, cantidad)
                    else:
                        self.inventario.stock[producto.producto] = max(0, cantidad)
                    messagebox.showinfo("Inventario actualizado", f"Stock actualizado de '{producto.producto}': {self.inventario.stock[producto.producto]}")
                elif cantidad_txt:
                    messagebox.showerror("Error", "Cantidad inválida")

                cafeteriaback.guardar_productos_json(self.menu_productos)
                self.save_inventory_to_json()
                nuevo_precio_entry.delete(0, tk.END)
                cantidad_entry.delete(0, tk.END)
            else:
                messagebox.showerror("Error", "Selecciona un producto.")

        tk.Button(ventana, text="Aplicar Cambios", command=aplicar_cambios).pack(pady=10)
if __name__ == "__main__":
    root = tk.Tk()
    app = CafeteriaApp(root)
    root.mainloop()
