import pandas as pd
import numpy as np

def calcular_riesgo_inventario(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calcula el riesgo de quiebre de stock basado en proyecciones.
    
    Args:
        df (pd.DataFrame): DataFrame que debe contener al menos las columnas 
                           'Inventory Level' y 'Demand Forecast'.
                           
    Returns:
        pd.DataFrame: DataFrame original con nuevas columnas añadidas:
                      'risk_score', 'risk_category' y 'alert_message'.
                      El DataFrame resultante está ordenado por 'risk_score' descendente.
    """
    # Creamos una copia para no alterar el DataFrame original
    df_result = df.copy()
    
    # 1. Calcular la métrica de riesgo de quiebre de stock
    # Fórmula: risk_score = Demand Forecast / Inventory Level
    # Utilizamos np.where para evitar división por cero en caso de que el inventario sea 0
    df_result['risk_score'] = np.where(
        df_result['Inventory Level'] > 0, 
        df_result['Demand Forecast'] / df_result['Inventory Level'], 
        float('inf')  # Si el inventario es 0 y hay demanda, el riesgo es infinito (máximo)
    )
    
    # 2. Clasificar este riesgo en una nueva columna categórica
    # Reglas: Bajo < 0.7 | Medio [0.7, 1.0] | Alto > 1.0
    condiciones = [
        df_result['risk_score'] < 0.7,
        (df_result['risk_score'] >= 0.7) & (df_result['risk_score'] <= 1.0),
        df_result['risk_score'] > 1.0
    ]
    categorias = ['Bajo', 'Medio', 'Alto']
    df_result['risk_category'] = np.select(condiciones, categorias, default='Desconocido')
    
    # 3. Generar un ranking ordenado de los productos más críticos
    # Ordenamos por la métrica de riesgo de mayor a menor
    df_result = df_result.sort_values(by='risk_score', ascending=False).reset_index(drop=True)
    
    # 4. Lógica para generar mensajes de alerta automáticos para productos con riesgo 'Alto'
    def generar_alerta(row):
        if row['risk_category'] == 'Alto':
            return (f"¡ALERTA CRÍTICA! Alta probabilidad de quiebre de stock. "
                    f"La demanda proyectada ({row['Demand Forecast']}) supera "
                    f"el inventario actual ({row['Inventory Level']}).")
        return "Niveles normales/óptimos."

    df_result['alert_message'] = df_result.apply(generar_alerta, axis=1)
    
    return df_result
