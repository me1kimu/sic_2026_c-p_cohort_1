import heapq
import itertools
from transformers import pipeline

class MotorIA:
    def __init__(self, motor_logico, hf_token=None):
        self.motor = motor_logico
        print("⏳ [Hugging Face Local] Descargando pesos neuronales a la RAM...")
        print("   (Esto tomará unos 2 minutos solo la primera vez).")

        # Descargamos el modelo TinyLlama directamente desde el HUB de Hugging Face a nuestra RAM
        self.generador = pipeline("text-generation", model="TinyLlama/TinyLlama-1.1B-Chat-v1.0")
        print("✅ [Hugging Face Local] ¡IA cargada e instanciada con éxito!")

    # ==========================================
    # LÓGICA MATEMÁTICA (DIJKSTRA)
    # ==========================================
    def calcular_ruta_optima(self, origen, destino, criterio="tiempo_minutos", es_destino_final=True):
        grafo = self.motor.grafo

        if origen not in grafo.paraderos or destino not in grafo.paraderos:
            return None, "Error: Origen o destino no registrados."

        costos = {nodo: float('inf') for nodo in grafo.paraderos}
        previos = {nodo: None for nodo in grafo.paraderos}
        costos[origen] = 0
        pq = [(0, origen)]

        while pq:
            costo_actual, actual = heapq.heappop(pq)
            if actual == destino: break
            if costo_actual > costos[actual]: continue

            for vecino in grafo.obtener_vecinos(actual):
                datos_arista = self.motor.procesar_ruta(actual, vecino)
                if not datos_arista: continue
                nuevo_costo = costo_actual + datos_arista[criterio]

                if nuevo_costo < costos[vecino]:
                    costos[vecino] = nuevo_costo
                    previos[vecino] = actual
                    heapq.heappush(pq, (nuevo_costo, vecino))

        if costos[destino] == float('inf'): return None, "Ruta imposible."

        # Reconstruimos los paraderos por los que pasamos
        ruta_nodos = []
        paso = destino
        while paso is not None:
            ruta_nodos.insert(0, paso)
            paso = previos[paso]


        # Ahora que sabemos el camino, sumamos ambas cosas sin importar el criterio
        total_tiempo = 0.0
        total_dist_km = 0.0

        for i in range(len(ruta_nodos) - 1):
            datos = self.motor.grafo.consultar_cache(ruta_nodos[i], ruta_nodos[i+1])
            if datos:
                total_tiempo += datos["tiempo_minutos"]
                total_dist_km += datos["distancia_km"]
        # --------------------------------------------------------

        return {
            "ruta_nodos": ruta_nodos,
            "total_tiempo_minutos": round(total_tiempo, 2), # Aquí devolvemos el total exacto
            "total_distancia_km": round(total_dist_km, 2),  # Aquí devolvemos el total exacto
            "itinerario": self._generar_itinerario(ruta_nodos, es_destino_final)
        }, "Éxito"

    def _generar_itinerario(self, ruta_nodos, es_destino_final=True):
        if not ruta_nodos or len(ruta_nodos) < 2:
            return []

        itinerario_humano = []
        micro_actual = None

        for i in range(len(ruta_nodos) - 1):
            origen_tramo = ruta_nodos[i]
            destino_tramo = ruta_nodos[i+1]

            datos = self.motor.grafo.consultar_cache(origen_tramo, destino_tramo)
            micros_disponibles = datos.get("servicios", ["Caminando"]) if datos else ["Caminando"]

            if micro_actual not in micros_disponibles:
                micro_actual = micros_disponibles[0]
                if i == 0:
                    itinerario_humano.append(f"🟢 SUBIR: En paradero {origen_tramo}, toma la opción [{micro_actual}].")
                else:
                    itinerario_humano.append(f"🔄 TRANSBORDO: Bájate en {origen_tramo} y cambia a [{micro_actual}].")

            itinerario_humano.append(f"   -> Viajando hacia {destino_tramo}...")

        if es_destino_final:
            itinerario_humano.append(f"🔴 BAJAR: Llegaste a tu destino en {ruta_nodos[-1]}.")
        else:
            itinerario_humano.append(f"📍 PARADA INTERMEDIA: Llegaste a {ruta_nodos[-1]}.")

        return itinerario_humano

    # ==========================================
    # MÚLTIPLES PARADAS (hasta 2 paradas intermedias opcionales)
    # Prueba todos los órdenes posibles entre las paradas seleccionadas
    # y se queda con el de menor costo según el criterio pedido.
    # ==========================================
    def calcular_ruta_multiparada(self, origen, destino, paradas_intermedias, criterio="tiempo_minutos"):
        """
        Calcula la ruta óptima pasando obligatoriamente por las paradas_intermedias dadas
        (0, 1 o 2 paradas). Prueba cada orden posible entre ellas y devuelve el mejor.
        """
        # Filtramos vacíos/None, duplicados y paradas iguales al origen/destino
        paradas_validas = list(dict.fromkeys(
            p for p in paradas_intermedias if p and p not in (origen, destino)
        ))

        mejor_resultado = None
        mejor_costo = float('inf')

        # Con 0, 1 o 2 paradas intermedias esto son como máximo 2 combinaciones (2!)
        for orden in itertools.permutations(paradas_validas):
            secuencia = [origen] + list(orden) + [destino]
            tiempo_total = 0.0
            distancia_total = 0.0
            itinerario_completo = []
            ruta_nodos_completa = []
            valido = True

            for i in range(len(secuencia) - 1):
                sub_origen = secuencia[i]
                sub_destino = secuencia[i + 1]
                es_ultimo_tramo = (i == len(secuencia) - 2)

                resultado, _ = self.calcular_ruta_optima(
                    sub_origen, sub_destino, criterio, es_destino_final=es_ultimo_tramo
                )

                if not resultado:
                    valido = False
                    break

                tiempo_total += resultado["total_tiempo_minutos"]
                distancia_total += resultado["total_distancia_km"]

                # Evitamos duplicar el nodo de unión entre tramos consecutivos
                nodos_tramo = resultado["ruta_nodos"]
                if ruta_nodos_completa and nodos_tramo and ruta_nodos_completa[-1] == nodos_tramo[0]:
                    ruta_nodos_completa.extend(nodos_tramo[1:])
                else:
                    ruta_nodos_completa.extend(nodos_tramo)

                itinerario_completo.extend(resultado["itinerario"])

            if not valido:
                continue

            costo_total = tiempo_total if criterio == "tiempo_minutos" else distancia_total

            if costo_total < mejor_costo:
                mejor_costo = costo_total
                mejor_resultado = {
                    "ruta_nodos": ruta_nodos_completa,
                    "total_tiempo_minutos": round(tiempo_total, 2),
                    "total_distancia_km": round(distancia_total, 2),
                    "itinerario": itinerario_completo,
                    "orden_paradas": list(orden)
                }

        if mejor_resultado is None:
            return None, "Ruta imposible: no se pudo conectar el origen, las paradas intermedias y el destino."

        return mejor_resultado, "Éxito"

    # ==========================================
    # LÓGICA COGNITIVA (IA LOCAL DE HUGGING FACE)
    # ==========================================
    def evaluar_estrategia_logistica(self, origen, destino, contexto_usuario):
        """Orquestador principal. Usa la IA que descargamos en la memoria RAM."""
        ruta_tiempo, _ = self.calcular_ruta_optima(origen, destino, "tiempo_minutos")
        ruta_distancia, _ = self.calcular_ruta_optima(origen, destino, "distancia_km")

        if not ruta_tiempo or not ruta_distancia:
            return "❌ No se pudo calcular la ruta. Verifica el GTFS."

        prompt_analisis = f"""[INST] Eres un experto Analista Logístico de transporte. Responde en un párrafo corto.
Cliente viaja de {origen} a {destino}.
Su contexto es: "{contexto_usuario}".

OPCIÓN A (Rápida): {ruta_tiempo.get('total_tiempo_minutos')} min, {ruta_tiempo.get('total_distancia_km')} km.
OPCIÓN B (Corta): {ruta_distancia.get('total_tiempo_minutos')} min, {ruta_distancia.get('total_distancia_km')} km.

Recomienda cuál debe tomar justificando tu respuesta de acuerdo a su contexto. [/INST]"""

        # Formato de "Prompt" especial que exige TinyLlama para pensar
        prompt_formateado = f"<|system|>\nEres un analista logístico útil y conciso. Responde en español.</s>\n<|user|>\n{prompt_analisis}</s>\n<|assistant|>\n"

        try:
            # Aquí le decimos a nuestro modelo local que escriba la respuesta
            resultado = self.generador(prompt_formateado, max_new_tokens=200, temperature=0.3, return_full_text=False)
            texto_generado = resultado[0]['generated_text']

            informe_final = f"### 🤖 Análisis Logístico (IA Local Hugging Face)\n{texto_generado}\n\n"
            informe_final += f"**Ruta Sugerida (Matemática):**\n"
            informe_final += chr(10).join(['* ' + paso for paso in ruta_tiempo.get('itinerario', [])])
            return informe_final

        except Exception as e:
            return f"❌ Error en la IA Local: {e}"

    def evaluar_estrategia_logistica_multiparada(self, origen, parada_1, parada_2, destino, contexto_usuario):
        """
        Igual que evaluar_estrategia_logistica, pero acepta hasta 2 paradas intermedias
        opcionales. Prueba todos los órdenes posibles entre las paradas seleccionadas
        y usa el de menor costo para cada criterio (tiempo y distancia).
        """
        paradas_intermedias = [p for p in (parada_1, parada_2) if p and p != "Ninguna"]

        ruta_tiempo, msg_tiempo = self.calcular_ruta_multiparada(origen, destino, paradas_intermedias, "tiempo_minutos")
        ruta_distancia, _ = self.calcular_ruta_multiparada(origen, destino, paradas_intermedias, "distancia_km")

        if not ruta_tiempo or not ruta_distancia:
            return f"❌ No se pudo calcular la ruta con esas paradas. ({msg_tiempo})"

        paradas_texto = " → ".join(paradas_intermedias) if paradas_intermedias else "Sin paradas intermedias (viaje directo)"
        orden_tiempo_texto = " → ".join(ruta_tiempo.get('orden_paradas', [])) or "directo"
        orden_distancia_texto = " → ".join(ruta_distancia.get('orden_paradas', [])) or "directo"

        prompt_analisis = f"""[INST] Eres un experto Analista Logístico de transporte. Responde en un párrafo corto.
Cliente viaja de {origen} a {destino}, pasando obligatoriamente por: {paradas_texto}.
Su contexto es: "{contexto_usuario}".

OPCIÓN A (Rápida): orden de paradas {orden_tiempo_texto}, {ruta_tiempo.get('total_tiempo_minutos')} min, {ruta_tiempo.get('total_distancia_km')} km.
OPCIÓN B (Corta): orden de paradas {orden_distancia_texto}, {ruta_distancia.get('total_tiempo_minutos')} min, {ruta_distancia.get('total_distancia_km')} km.

Recomienda cuál debe tomar justificando tu respuesta de acuerdo a su contexto. [/INST]"""

        prompt_formateado = f"<|system|>\nEres un analista logístico útil y conciso. Responde en español.</s>\n<|user|>\n{prompt_analisis}</s>\n<|assistant|>\n"

        try:
            resultado = self.generador(prompt_formateado, max_new_tokens=200, temperature=0.3, return_full_text=False)
            texto_generado = resultado[0]['generated_text']

            informe_final = f"### 🤖 Análisis Logístico (IA Local Hugging Face)\n{texto_generado}\n\n"
            informe_final += f"**Paradas intermedias seleccionadas:** {paradas_texto}\n\n"
            informe_final += f"**Ruta Sugerida (Matemática, orden: {orden_tiempo_texto}):**\n"
            informe_final += chr(10).join(['* ' + paso for paso in ruta_tiempo.get('itinerario', [])])
            return informe_final

        except Exception as e:
            return f"❌ Error en la IA Local: {e}"
