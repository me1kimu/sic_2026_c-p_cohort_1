import json

class GrafoLogistica:
    def __init__(self):
        # 1. Tu idea principal: El Caché Vectorial
        # Formato esperado -> "PA123-PA456": {"distancia_km": 4.2, "tiempo_minutos": 12.5, "servicios": ["210", "F30"]}
        self.cache_rutas = {}

        # 2. Diccionario de Adyacencia para la IA
        # Formato esperado -> "PA123": ["PA456", "PA789"] (A quiénes está conectado directamente)
        self.adyacencia = {}

        # 3. Registro único de paraderos (Nodos)
        self.paraderos = set()

    def _generar_llave(self, origen, destino):
        """Método interno privado para asegurar que la llave siempre tenga el mismo formato."""
        return f"{origen}-{destino}"

    def agregar_paradero(self, codigo_paradero):
        """Registra un paradero nuevo en el sistema y le prepara su lista de vecinos."""
        if codigo_paradero not in self.paraderos:
            self.paraderos.add(codigo_paradero)
            self.adyacencia[codigo_paradero] = []

    def registrar_ruta(self, origen, destino, distancia, tiempo, servicios):
        """Guarda los datos devueltos por la API de OSRM en nuestra memoria (Hit de caché)."""
        # 1. Asegurarnos de que los paraderos existan
        self.agregar_paradero(origen)
        self.agregar_paradero(destino)

        # 2. Guardar en el Caché
        llave = self._generar_llave(origen, destino)
        self.cache_rutas[llave] = {
            "distancia_km": distancia,
            "tiempo_minutos": tiempo,
            "servicios": servicios
        }

        # 3. Conectar en la lista de adyacencia (Para que la IA sepa que son vecinos)
        if destino not in self.adyacencia[origen]:
            self.adyacencia[origen].append(destino)

    def consultar_cache(self, origen, destino):
        """
        Le pregunta a la memoria si ya conocemos esta ruta.
        Retorna el diccionario con los vectores de tiempo/distancia o None si no existe.
        """
        llave = self._generar_llave(origen, destino)
        return self.cache_rutas.get(llave, None)

    def obtener_vecinos(self, codigo_paradero):
        """Devuelve la lista de paraderos a los que puedo viajar directamente desde aquí."""
        return self.adyacencia.get(codigo_paradero, [])

    def exportar_cache_json(self, nombre_archivo="cache_rutas.json"):
        """¡Nivel Dios! Guarda el estado actual del caché en un archivo para no perderlo al apagar Colab."""
        with open(nombre_archivo, 'w') as f:
            json.dump(self.cache_rutas, f, indent=4)
        print(f"✅ Caché exportado exitosamente a {nombre_archivo}")

    def mostrar_estado(self):
        """Muestra cuántos datos tiene guardados el grafo actualmente."""
        print("--- ESTADO DEL GRAFO LOGÍSTICO ---")
        print(f"📍 Paraderos registrados: {len(self.paraderos)}")
        print(f"🛣️ Rutas en caché: {len(self.cache_rutas)}")
        print("----------------------------------")