import requests

class MotorLogico:
    def __init__(self, grafo):
        # Recibe el objeto GrafoLogistica por inyección de dependencias
        self.grafo = grafo

        # Diccionario para almacenar las coordenadas de los paraderos.
        # Formato: "PA123": (Latitud, Longitud)
        self.coordenadas_paraderos = {}

        # Simulación de una base de datos que nos dice qué micros pasan por qué tramo.
        # Formato: "PA123-PA456": ["210", "F30"]
        self.servicios_tramos = {}

    def cargar_datos_base(self, paraderos_dict, servicios_dict):
        """Simula la carga de un archivo CSV/JSON con las paradas y las micros."""
        self.coordenadas_paraderos = paraderos_dict
        self.servicios_tramos = servicios_dict

    def procesar_ruta(self, origen, destino):
        """
        El corazón de esta clase. Busca en la memoria local; si no está,
        va a internet, lo descarga, lo guarda y lo devuelve.
        """
        # 1. HIT DE CACHÉ: Le preguntamos al grafo si ya conoce el camino
        datos_cacheados = self.grafo.consultar_cache(origen, destino)
        if datos_cacheados:
            print(f"⚡ [Caché Hit] Ruta {origen} -> {destino} cargada desde la memoria al instante.")
            return datos_cacheados

        # 2. MISS DE CACHÉ: Si no existe, buscamos las coordenadas para consultar la API
        if origen not in self.coordenadas_paraderos or destino not in self.coordenadas_paraderos:
            print(f"❌ Error: No se tienen las coordenadas GPS de {origen} o {destino}.")
            return None

        print(f"🌐 [API Request] Descargando datos de tráfico real para {origen} -> {destino}...")
        lat_origen, lon_origen = self.coordenadas_paraderos[origen]
        lat_destino, lon_destino = self.coordenadas_paraderos[destino]

        # URL de OSRM (Cuidado con el orden: OSRM exige Longitud,Latitud)
        url = f"http://router.project-osrm.org/route/v1/driving/{lon_origen},{lat_origen};{lon_destino},{lat_destino}?overview=false"

        try:
            respuesta = requests.get(url)
            if respuesta.status_code == 200:
                data = respuesta.json()
                if data.get('code') == 'Ok':
                    # OSRM devuelve la distancia en metros y el tiempo en segundos.
                    # Lo convertimos a Kilómetros y Minutos para nuestra IA.
                    distancia_km = round(data['routes'][0]['distance'] / 1000, 2)
                    tiempo_minutos = round(data['routes'][0]['duration'] / 60, 2)

                    # Identificamos qué micros hacen este trayecto
                    llave_tramo = self.grafo._generar_llave(origen, destino)
                    servicios = self.servicios_tramos.get(llave_tramo, ["Caminando/Genérico"])

                    # 3. GUARDAMOS EN EL CACHÉ: Para no tener que consultar esto de nuevo
                    self.grafo.registrar_ruta(origen, destino, distancia_km, tiempo_minutos, servicios)

                    return {
                        "distancia_km": distancia_km,
                        "tiempo_minutos": tiempo_minutos,
                        "servicios": servicios
                    }
            print("❌ OSRM no pudo encontrar una ruta viable entre esos puntos.")
        except Exception as e:
            print(f"❌ Error fatal de conexión a internet: {e}")

        return None