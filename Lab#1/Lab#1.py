import json
from typing import List, Dict, Any, Optional

class ApartmentRecommendationSystem:
    """
    Sistema de recomendación de apartamentos basado en distancias a servicios
    Encuentra los mejores apartamentos considerando la distancia a servicios requeridos
    """
    
    def __init__(self):
        """Inicializa el sistema de recomendación"""
        pass
    
    def find_distance(self, apartments: List[Dict], start_index: int, requirement: str, n: int) -> int:
        """
        Encuentra la distancia más cercana a un servicio requerido desde un apartamento específico
        
        Args:
            apartments: Lista de apartamentos con sus servicios
            start_index: Índice del apartamento de referencia
            requirement: Servicio requerido a buscar
            n: Número total de apartamentos
            
        Returns:
            int: Distancia al servicio más cercano, -1 si no se encuentra
        """
        for i in range(1, n):
            # Buscar hacia la derecha
            if start_index + i < n and apartments[start_index + i].get(requirement, False):
                return i
            
            # Buscar hacia la izquierda
            if start_index - i >= 0 and apartments[start_index - i].get(requirement, False):
                return i
        
        return -1  # No se encontró el servicio
    
    def calculate_apartment_score(self, apartments: List[Dict], apartment_index: int, required_services: List[str]) -> tuple:
        """
        Calcula el puntaje de un apartamento basado en las distancias a servicios requeridos
        
        Args:
            apartments: Lista de apartamentos
            apartment_index: Índice del apartamento a evaluar
            required_services: Lista de servicios requeridos
            
        Returns:
            tuple: (es_válido, distancia_total, distancia_máxima)
        """
        total_distance = 0
        max_distance = 0
        n = len(apartments)
        apartment = apartments[apartment_index]
        
        for requirement in required_services:
            if not apartment.get(requirement, False):
                distance = self.find_distance(apartments, apartment_index, requirement, n)
                
                if distance == -1:
                    return (False, float('inf'), float('inf'))  # Apartamento no válido
                
                total_distance += distance
                max_distance = max(max_distance, distance)
        
        return (True, total_distance, max_distance)
    
    def find_best_apartments(self, apartments: List[Dict], required_services: List[str]) -> List[int]:
        """
        Encuentra los mejores apartamentos basado en criterios de distancia
        
        Args:
            apartments: Lista de apartamentos con sus servicios
            required_services: Lista de servicios requeridos
            
        Returns:
            List[int]: Lista de índices de los mejores apartamentos
        """
        if not apartments or not required_services:
            return []
        
        recommendations = []
        min_total_distance = float('inf')
        min_max_distance = float('inf')
        n = len(apartments)
        
        # Evaluar cada apartamento
        for i in range(n):
            is_valid, total_distance, max_distance = self.calculate_apartment_score(
                apartments, i, required_services
            )
            
            if not is_valid:
                continue
            
            # Determinar si este apartamento es mejor que los actuales
            if (total_distance < min_total_distance or 
                (total_distance == min_total_distance and max_distance < min_max_distance)):
                # Nuevo mejor apartamento encontrado
                min_total_distance = total_distance
                min_max_distance = max_distance
                recommendations = [i]
                
            elif total_distance == min_total_distance and max_distance == min_max_distance:
                # Apartamento con el mismo puntaje que los mejores
                recommendations.append(i)
        
        return recommendations
    
    def process_recommendation_request(self, apartments: List[Dict], required_services: List[str]) -> List[int]:
        """
        Procesa una solicitud de recomendación de apartamentos
        
        Args:
            apartments: Lista de apartamentos (input1)
            required_services: Lista de servicios requeridos (input2)
            
        Returns:
            List[int]: Lista de índices de apartamentos recomendados
        """
        try:
            # Validar datos de entrada
            if not isinstance(apartments, list) or not isinstance(required_services, list):
                return []
            
            if not apartments:
                return []
            
            if not required_services:
                return list(range(len(apartments)))  # Si no hay requisitos, todos son válidos
            
            # Encontrar los mejores apartamentos
            best_apartments = self.find_best_apartments(apartments, required_services)
            
            return best_apartments
            
        except Exception as e:
            print(f"Error procesando recomendación: {e}")
            return []

def process_recommendation_file(input_file_path: str, output_file_path: str, debug_mode: bool = False):
    """
    Procesa un archivo JSONL con datos de entrada y genera recomendaciones de apartamentos
    
    Args:
        input_file_path: Ruta del archivo de entrada
        output_file_path: Ruta del archivo de salida
        debug_mode: Si True, muestra información de depuración
    """
    output_results = []
    
    try:
        # Intentar con diferentes codificaciones
        encodings = ["utf-8", "latin-1"]
        
        for encoding in encodings:
            try:
                with open(input_file_path, "r", encoding=encoding) as input_file:
                    for line_num, line in enumerate(input_file, 1):
                        try:
                            line = line.strip()
                            if not line:  # Saltar líneas vacías
                                continue
                            
                            # Crear nueva instancia para cada línea
                            recommendation_system = ApartmentRecommendationSystem()
                            
                            if debug_mode:
                                print(f"\n--- Procesando línea {line_num} ---")
                            
                            data = json.loads(line)
                            
                            # Extraer datos de entrada
                            apartments = data.get("input1", [])
                            required_services = data.get("input2", [])
                            
                            if debug_mode:
                                print(f"Apartamentos: {len(apartments)}")
                                print(f"Servicios requeridos: {required_services}")
                            
                            # Procesar recomendación
                            result = recommendation_system.process_recommendation_request(
                                apartments, required_services
                            )
                            
                            output_results.append(result)
                            
                            if debug_mode:
                                print(f"Resultado línea {line_num}: {result}")
                            
                        except json.JSONDecodeError as e:
                            print(f"Error de JSON en línea {line_num}: {e}")
                            output_results.append([])
                        except Exception as e:
                            print(f"Error procesando línea {line_num}: {e}")
                            output_results.append([])
                break
            except UnicodeDecodeError:
                continue
        else:
            raise ValueError(f"No se pudo leer el archivo con ninguna codificación")
    
    except FileNotFoundError:
        print(f"Archivo de entrada no encontrado: {input_file_path}")
        return
    
    # Guardar resultados
    try:
        with open(output_file_path, "w", encoding="utf-8") as output_file:
            for result in output_results:
                output_file.write(json.dumps(result, separators=(',', ':')) + "\n")
        
        print(f"\nRecomendaciones generadas correctamente en: {output_file_path}")
        print(f"Total de recomendaciones procesadas: {len(output_results)}")
        
        # Mostrar estadísticas
        non_empty_results = sum(1 for result in output_results if result)
        print(f"Recomendaciones con resultados: {non_empty_results}")
        print(f"Recomendaciones vacías: {len(output_results) - non_empty_results}")
        
    except Exception as e:
        print(f"Error guardando resultados: {e}")

def main():
    """Función principal del programa"""
    # Configurar rutas de archivos
    archivo_entrada = "input_challenge.jsonl"  # Archivo JSONL de entrada
    archivo_salida = "resultados.jsonl"    # Archivo JSONL de salida
    
    # Procesar archivo de recomendaciones
    process_recommendation_file(archivo_entrada, archivo_salida, debug_mode=False)

if __name__ == "__main__":
    main()