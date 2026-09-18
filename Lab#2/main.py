import json
import os

class RecomendadorApartamentos:
    def __init__(self):
        # Rutas de archivos
        self.ruta_entrada = None
        self.ruta_salida = None
        # Datos cargados
        self.datos_casos = []
    
    def configurar_rutas(self, ruta_entrada, ruta_salida):
        """Configura las rutas de archivos de entrada y salida"""
        self.ruta_entrada = ruta_entrada
        self.ruta_salida = ruta_salida
    
    def cargar_datos(self, archivo_entrada):
        """Carga los datos desde un archivo JSON Lines"""
        self.datos_casos = []
        try:
            with open(archivo_entrada, 'r', encoding='utf-8') as file:
                for line_number, line in enumerate(file, 1):
                    if line.strip():  # Verificar que la línea no esté vacía
                        try:
                            data = json.loads(line)
                            self.datos_casos.append(data)
                        except json.JSONDecodeError:
                            print(f"Error al decodificar la línea {line_number} del archivo JSONL.")
            
            print(f"Se cargaron {len(self.datos_casos)} casos exitosamente.")
            return True
            
        except FileNotFoundError:
            print(f"Error: No se encontró el archivo {archivo_entrada}")
            return False
        except Exception as e:
            print(f"Error inesperado al cargar datos: {e}")
            return False
    
    def find_recommendations(self, input1, input2):
        """
        Encuentra las mejores recomendaciones de apartamentos basadas en los requerimientos.
        Mantiene la lógica original del algoritmo.
        """
        recommendations = []
        min_total_distance = float('inf')
        min_max_distance = float('inf')
        n = len(input1)

        for i in range(n):
            total_distance = 0
            max_distance = 0
            valid_apartment = True
            apartment = input1[i]

            for requirement in input2:
                if not apartment.get(requirement, False):
                    distance = self.find_distance(input1, i, requirement, n)
                    
                    if distance == -1:
                        valid_apartment = False
                        break
                    
                    total_distance += distance
                    max_distance = max(max_distance, distance)

            if valid_apartment:
                if (total_distance < min_total_distance or 
                    (total_distance == min_total_distance and max_distance < min_max_distance)):
                    min_total_distance = total_distance
                    min_max_distance = max_distance
                    recommendations = [i]  
                elif total_distance == min_total_distance and max_distance == min_max_distance:
                    recommendations.append(i)  

        return recommendations

    def find_distance(self, input1, start_index, requirement, n):
        """
        Encuentra la distancia más cercana a un requerimiento específico.
        Mantiene la lógica original del algoritmo.
        """
        for i in range(1, n):
            if start_index + i < n and input1[start_index + i].get(requirement, False):
                return i

            if start_index - i >= 0 and input1[start_index - i].get(requirement, False):
                return i

        return -1  
    
    def procesar_caso(self, caso_data):
        """Procesa un caso individual y retorna las recomendaciones"""
        input1 = caso_data.get("input1", [])
        input2 = caso_data.get("input2", [])
        
        if not input1 or not input2:
            print("Advertencia: Caso con datos incompletos encontrado.")
            return []
        
        best_apartments = self.find_recommendations(input1, input2)
        return best_apartments
    
    def procesar_todos_casos(self):
        """Procesa todos los casos cargados y retorna los resultados"""
        resultados = []
        
        print(f"\nProcesando {len(self.datos_casos)} casos...")
        
        for i, caso in enumerate(self.datos_casos):
            print(f"Procesando caso {i + 1}/{len(self.datos_casos)}")
            resultado = self.procesar_caso(caso)
            resultados.append(resultado)
        
        return resultados
    
    def guardar_resultados(self, resultados, archivo_salida):
        """Guarda los resultados en un archivo JSON Lines"""
        try:
            with open(archivo_salida, 'w', encoding='utf-8') as file:
                for resultado in resultados:
                    file.write(json.dumps(resultado) + "\n")
            
            print(f"Resultados guardados exitosamente en: {archivo_salida}")
            return True
            
        except Exception as e:
            print(f"Error al guardar resultados: {e}")
            return False
    
    def ejecutar_procesamiento_completo(self):
        """Ejecuta el procesamiento completo desde la carga hasta el guardado"""
        if not self.ruta_entrada or not self.ruta_salida:
            print("Error: No se han configurado las rutas de entrada y salida.")
            return False
        
        # Cargar datos
        if not self.cargar_datos(self.ruta_entrada):
            return False
        
        # Procesar casos
        resultados = self.procesar_todos_casos()
        
        # Guardar resultados
        if self.guardar_resultados(resultados, self.ruta_salida):
            print(f"\nProcesamiento completado exitosamente.")
            print(f"Se procesaron {len(resultados)} casos.")
            return True
        
        return False

# Función principal
def main():
    """Función principal que ejecuta el programa"""
    # Crear instancia del recomendador
    recomendador = RecomendadorApartamentos()
    
    # Configurar archivos (puedes modificar estos nombres fácilmente)
    archivo_entrada = "input_challenge.jsonl"  # Archivo JSONL de entrada
    archivo_salida = "resultados.jsonl"        # Archivo JSONL de salida
    
    recomendador.configurar_rutas(archivo_entrada, archivo_salida)
    
    try:
        # Ejecutar procesamiento completo
        exito = recomendador.ejecutar_procesamiento_completo()
        
        if exito:
            print("\n¡Programa ejecutado correctamente!")
        else:
            print("\nEl programa terminó con errores.")
            
    except Exception as e:
        print(f"Error inesperado en la ejecución principal: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

