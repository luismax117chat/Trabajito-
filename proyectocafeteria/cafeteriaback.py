# === INICIO DEL CÓDIGO ===
import json
import os

# --- Configuración de Rutas de Archivos ---
RUTA_BASE = os.path.dirname(os.path.abspath(__file__))
ARCHIVO_PERSONAS = os.path.join(RUTA_BASE, "data", "personas.json")
ARCHIVO_PRODUCTOS = os.path.join(RUTA_BASE, "data", "productos.json")

# --- Clase Base para Personas ---
class Persona:
    personas_registradas = []

    def __init__(self, nombre, edad, telefono):
        self.nombre = nombre
        self.edad = edad
        self.telefono = telefono

    def registrar(self):
        Persona.personas_registradas.append(self)
        guardar_personas_json()

    @classmethod
    def mostrar_personas_registradas(cls):
        if not cls.personas_registradas:
            print("No hay personas registradas.")
            return
        print("--- Personas Registradas ---")
        for persona in cls.personas_registradas:
            tipo = "Cliente" if isinstance(persona, Cliente) else "Empleado"
            print(f"- {persona.nombre} ({tipo}) - Edad: {persona.edad} - Teléfono: {persona.telefono}")
        print("--------------------------")

    @classmethod
    def obtener_personas_registradas(cls):
        return cls.personas_registradas
    @classmethod
    def obtener_nombres_registrados(cls):
        nombres = [persona.nombre for persona in cls.personas_registradas]
        return nombres

# --- Clase para Clientes ---
class Cliente(Persona):
    def __init__(self, nombre, edad, telefono):
        super().__init__(nombre, edad, telefono)
        self.historial_pedidos = []

    def realizar_pedido(self, pedido):
        self.historial_pedidos.append(pedido)

    def consultar_historial(self):
        return self.historial_pedidos

# --- Clase para Empleados ---
class Empleado(Persona):
    def __init__(self, nombre, edad, telefono, puesto):
        super().__init__(nombre, edad, telefono)
        self.puesto = puesto  # gerente, cajero, etc.

    def tiene_privilegio(self, accion):
        if self.puesto == "gerente":
            return True
        if self.puesto == "cajero" and accion in ["ver"]:
            return True
        return False

    def actualizar_inventario(self, inventario, ingrediente, cantidad):
        if self.tiene_privilegio("editar"):
            inventario.actualizar_stock(ingrediente, cantidad)
        else:
            print("No tiene permisos para editar el inventario.")

    @classmethod
    def eliminar_cliente(cls, nombre_cliente):
        for persona in list(cls.personas_registradas): # Iterar sobre una copia para permitir la eliminación
            if isinstance(persona, Cliente) and persona.nombre == nombre_cliente:
                cls.personas_registradas.remove(persona)
                guardar_personas_json()
                print(f"Cliente '{nombre_cliente}' eliminado.")
                return
        print(f"Cliente '{nombre_cliente}' no encontrado.")

    @classmethod
    def modificar_cliente(cls, nombre_cliente, nuevo_telefono=None, nueva_edad=None):
        encontrado = False
        for persona in cls.personas_registradas:
            if isinstance(persona, Cliente) and persona.nombre == nombre_cliente:
                if nuevo_telefono:
                    persona.telefono = nuevo_telefono
                    print(f"Teléfono de '{nombre_cliente}' actualizado a {nuevo_telefono}.")
                if nueva_edad:
                    persona.edad = nueva_edad
                    print(f"Edad de '{nombre_cliente}' actualizada a {nueva_edad}.")
                guardar_personas_json()
                encontrado = True
                return
        if not encontrado:
            print(f"Cliente '{nombre_cliente}' no encontrado.")

# --- Clase Base para Productos ---
class ProductoBase:
    def __init__(self, producto, precio):
        self.producto = producto
        self.precio = precio

# --- Clase para Bebidas ---
class Bebida(ProductoBase):
    def __init__(self, producto, precio, sabor, tamaño, personalizables=None):
        super().__init__(producto, precio)
        self.sabor = sabor
        self.tamaño = tamaño
        self.personalizables = personalizables or []

# --- Clase para Postres ---
class Postre(ProductoBase):
    def __init__(self, producto, precio, azucar, sinazucar):
        super().__init__(producto, precio)
        self.azucar = azucar
        self.sinazucar = sinazucar

# --- Clase para el Inventario ---
class Inventario:
    def __init__(self):
        self.stock = {}

    def agregar_ingrediente(self, ingrediente, cantidad):
        self.stock[ingrediente] = self.stock.get(ingrediente, 0) + cantidad
        print(f"Ingrediente '{ingrediente}' agregado. Total: {self.stock[ingrediente]}")

    def verificar_stock(self, lista_ingredientes):
        for ingrediente in lista_ingredientes:
            if self.stock.get(ingrediente, 0) <= 0:
                return False
        return True

    def actualizar_stock(self, ingrediente, cantidad):
        self.stock[ingrediente] = self.stock.get(ingrediente, 0) + cantidad
        print(f"Stock de '{ingrediente}': {self.stock[ingrediente]}")

# --- Clase para Pedidos ---
class Pedido:
    def __init__(self, cliente, productos):
        self.cliente = cliente
        self.productos = productos
        self.estado = "Pendiente"
        self.total = self.calcular_total()

    def calcular_total(self):
        return sum(producto.precio for producto in self.productos)

    def aplicar_promocion(self, promocion):
        promocion.aplicar_descuento(self)

# --- Clase para Promociones ---
class Promocion:
    def __init__(self, tipo, valor):
        self.tipo = tipo  # "descuento", "fidelidad"
        self.valor = valor

    def aplicar_descuento(self, pedido):
        if self.tipo == "descuento":
            pedido.total -= pedido.total * (self.valor / 100)
        elif self.tipo == "fidelidad":
            pedido.total -= self.valor
        print(f"Nuevo total del pedido con promoción: {pedido.total:.2f}")

# ---------- Funciones de JSON ----------

def guardar_personas_json():
    data = []
    for persona in Persona.personas_registradas:
        d = {
            "tipo": "Cliente" if isinstance(persona, Cliente) else "Empleado",
            "nombre": persona.nombre,
            "edad": persona.edad,
            "telefono": persona.telefono
        }
        if isinstance(persona, Empleado):
            d["puesto"] = persona.puesto
        data.append(d)
    try:
        with open(ARCHIVO_PERSONAS, "w", encoding="utf-8") as f:
            json.dump({"personas": data}, f, indent=4)
        print(f"Datos de personas guardados en: {ARCHIVO_PERSONAS}")
    except IOError as e:
        print(f"Error al escribir en {ARCHIVO_PERSONAS}: {e}")

def cargar_personas_json():
    personas_registradas_temp = [] # Creamos una lista temporal
    if os.path.exists(ARCHIVO_PERSONAS):
        try:
            with open(ARCHIVO_PERSONAS, "r", encoding="utf-8") as f:
                datos = json.load(f)
                for item in datos.get("personas", []):
                    if item.get("tipo") == "Cliente":
                        personas_registradas_temp.append(Cliente(item["nombre"], item["edad"], item["telefono"]))
                    elif item.get("tipo") == "Empleado":
                        personas_registradas_temp.append(Empleado(item["nombre"], item["edad"], item["telefono"], item["puesto"]))
                print(f"Datos de personas cargados desde: {ARCHIVO_PERSONAS}. Total: {len(personas_registradas_temp)}")
                print(f"Contenido de personas cargadas: {personas_registradas_temp}") # Para diagnóstico
                return personas_registradas_temp # Devolvemos la lista cargada
        except json.JSONDecodeError:
            print(f"Error al decodificar {ARCHIVO_PERSONAS}. El archivo podría estar corrupto.")
        except IOError as e:
            print(f"Error al leer {ARCHIVO_PERSONAS}: {e}")
    else:
        print(f"No se encontró el archivo {ARCHIVO_PERSONAS}. Se creará al guardar.")
    return [] # Devolvemos una lista vacía si no se pudo cargar

def guardar_productos_json(productos):
    data = []
    for p in productos:
        if isinstance(p, Bebida):
            data.append({
                "tipo": "Bebida",
                "producto": p.producto,
                "precio": p.precio,
                "sabor": p.sabor,
                "tamaño": p.tamaño,
                "personalizables": p.personalizables,
                "cantidad": 0 # Inicializamos la cantidad en 0 al guardar desde el backend
            })
        elif isinstance(p, Postre):
            data.append({
                "tipo": "Postre",
                "producto": p.producto,
                "precio": p.precio,
                "azucar": p.azucar,
                "sinazucar": p.sinazucar,
                "cantidad": 0 # Inicializamos la cantidad en 0 al guardar desde el backend
            })
    try:
        with open(ARCHIVO_PRODUCTOS, "w", encoding="utf-8") as f:
            json.dump({"productos": data}, f, indent=4)
        print(f"Datos de productos guardados en: {ARCHIVO_PRODUCTOS}")
    except IOError as e:
        print(f"Error al escribir en {ARCHIVO_PRODUCTOS}: {e}")

def cargar_productos_json():
    productos = []
    if os.path.exists(ARCHIVO_PRODUCTOS):
        try:
            with open(ARCHIVO_PRODUCTOS, "r", encoding="utf-8") as f:
                datos = json.load(f)
                for item in datos.get("productos", []):
                    print(f"Item cargado (backend): {item}") # Imprime el item en el backend
                    if item.get("tipo") == "Bebida":
                        productos.append(Bebida(item["producto"], item["precio"], item["sabor"], item["tamaño"], item.get("personalizables", [])))
                    elif item.get("tipo") == "Postre":
                        productos.append(Postre(item["producto"], item["precio"], item.get("azucar", False), item.get("sinazucar", False)))
                print(f"Datos de productos cargados desde: {ARCHIVO_PRODUCTOS}. Total: {len(productos)}")
        except json.JSONDecodeError:
            print(f"Error al decodificar {ARCHIVO_PRODUCTOS}. El archivo podría estar corrupto.")
        except IOError as e:
            print(f"Error al leer {ARCHIVO_PRODUCTOS}: {e}")
    else:
        print(f"No se encontró el archivo {ARCHIVO_PRODUCTOS}. Se creará al guardar.")
    return productos

# ---------- MAIN ----------
if __name__ == "__main__":
    Persona.personas_registradas = cargar_personas_json() 
    productos = cargar_productos_json()
    inventario = Inventario() # Inicializar el inventario
    # Inicializar el inventario con los productos cargados (cantidad por defecto 0)
    for producto in productos:
        inventario.agregar_ingrediente(producto.producto, 0)
    print("Backend sincronizado con JSON.")