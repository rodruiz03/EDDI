#Se usa para leer archivos del tipo Jsonl
import json 
#Utiliza los hash para poder leerlos ademas que son necesarios en los labs para poder analizar la info y crear los archivos de salida
import hashlib
#Se utiliza en los algoritmos para poder llevar un orden debido a que los labs #1 y #2 utilizan como si fueran filtros entonces por eso son importantes
import heapq
#Pone la hora del dia para saber cuando se inicio le programa
import datetime
#Comprueba si esta vacio o que archivos existen en caso uno quiera utilizar otros archivos que los previamente utilizados en los labs
import os
#Mide cuanto tardan los procesos
import time
#Tipos de archivos como listas Diccionarios etc que se utilizan para filtrar y mostrar la info de cada programa
from typing import List, Dict, Any, Optional

class PropertyRecommendationSystem:
    """
    Sistema de recomendación de propiedades para Inmuebles GT
    Labs 1 y 2: Maneja apartamentos, casas y locales comerciales
    """
    
    #Niveles de seguridad por color - cada nivel acepta colores más seguros
    SECURITY_LEVELS = {
        "Red": ["Red"],
        "Orange": ["Red", "Orange"],
        "Yellow": ["Red", "Orange", "Yellow"],
        "Green": ["Red", "Orange", "Yellow", "Green"],
    }
    
    def __init__(self):
        """Inicializa el sistema de recomendación"""
        pass
    
    def validate_services(self, property_services: Dict[str, bool], required_services: List[str]) -> bool:
        """Verifica si una propiedad tiene todos los servicios requeridos"""
        for service in required_services:
            #Verificar que el servicio existe y está disponible
            if service not in property_services or not property_services[service]:
                return False
        return True
    
    def filter_apartments(self, apartments: List[Dict], pet_friendly: bool, budget: float, 
                         services: Dict[str, bool], required_services: List[str]) -> List[str]:
        """Filtra apartamentos por mascotas, presupuesto y servicios"""
        filtered_apartments = []
        
        for apartment in apartments:
            #Verificar política de mascotas
            if apartment.get("isPetFriendly", False) != pet_friendly:
                continue
            
            #Verificar presupuesto
            if apartment.get("price", float('inf')) > budget:
                continue
            
            #Verificar servicios requeridos
            if not self.validate_services(services, required_services):
                continue
                
            filtered_apartments.append(apartment)
        
        #Ordenar por precio ascendente
        filtered_apartments.sort(key=lambda x: x.get("price", 0))
        
        return [apt["id"] for apt in filtered_apartments]
    
    def filter_houses(self, houses: List[Dict], min_danger_level: str, budget: float,
                     services: Dict[str, bool], required_services: List[str]) -> List[str]:
        """Filtra casas por nivel de seguridad, presupuesto y servicios"""
        accepted_colors = self.SECURITY_LEVELS.get(min_danger_level, ["Red"])
        filtered_houses = []
        
        for house in houses:
            #Verificar nivel de seguridad
            house_danger = house.get("zoneDangerous", "Red")
            if house_danger not in accepted_colors:
                continue
            
            #Verificar presupuesto
            if house.get("price", float('inf')) > budget:
                continue
            
            #Verificar servicios requeridos
            if not self.validate_services(services, required_services):
                continue
                
            filtered_houses.append(house)
        
        #Ordenar por precio ascendente
        filtered_houses.sort(key=lambda x: x.get("price", 0))
        
        return [house["id"] for house in filtered_houses]
    
    def filter_premises(self, premises: List[Dict], commercial_activity: str, budget: float,
                       services: Dict[str, bool], required_services: List[str]) -> List[str]:
        """Filtra locales por actividad comercial, presupuesto y servicios"""
        filtered_premises = []
        
        for premise in premises:
            #Verificar actividad comercial permitida
            allowed_activities = premise.get("commercialActivities", [])
            if commercial_activity not in allowed_activities:
                continue
            
            #Verificar presupuesto
            if premise.get("price", float('inf')) > budget:
                continue
            
            #Verificar servicios requeridos
            if not self.validate_services(services, required_services):
                continue
                
            filtered_premises.append(premise)
        
        #Ordenar por precio ascendente
        filtered_premises.sort(key=lambda x: x.get("price", 0))
        
        return [premise["id"] for premise in filtered_premises]

    def recommend_constructions_lab1(self, input1: Dict, input2: Dict) -> List[str]:
        """Lab 1: Sistema de recomendación basado en distancias entre apartamentos"""
        try:
            #Manejar diferentes formatos de entrada
            if isinstance(input1, str):
                try:
                    input1 = json.loads(input1)
                except:
                    print(f"Error: input1 no es JSON válido")
                    return []
            
            if isinstance(input2, str):
                try:
                    input2 = json.loads(input2)
                except:
                    print(f"Error: input2 no es JSON válido")
                    return []
            
            #Validación de tipos de entrada
            if not isinstance(input1, list) or not isinstance(input2, list):
                print(f"Error: Formato de datos incorrecto para Lab1")
                return []
            
            apartments = input1  #Lista de apartamentos con servicios
            required_services = input2   #Lista de servicios requeridos
            
            #Ejecutar algoritmo de recomendación por distancias
            best_apartments = self.find_best_apartments(apartments, required_services)
            
            #Convertir índices a strings
            return [str(idx) for idx in best_apartments]
            
        except Exception as e:
            print(f"Error en recommend_constructions_lab1: {e}")
            import traceback
            traceback.print_exc()
            return []

    def find_distance(self, apartments: List[Dict], start_index: int, requirement: str, n: int) -> int:
        """Encuentra distancia más cercana a un servicio específico"""
        for i in range(1, n):
            #Buscar hacia la derecha
            if start_index + i < n and apartments[start_index + i].get(requirement, False):
                return i
            
            #Buscar hacia la izquierda
            if start_index - i >= 0 and apartments[start_index - i].get(requirement, False):
                return i
        
        return -1  #Servicio no encontrado

    def calculate_apartment_score(self, apartments: List[Dict], apartment_index: int, required_services: List[str]) -> tuple:
        """Calcula puntaje de apartamento basado en distancias a servicios"""
        total_distance = 0
        max_distance = 0
        n = len(apartments)
        apartment = apartments[apartment_index]
        
        for requirement in required_services:
            #Si el apartamento no tiene el servicio, buscar el más cercano
            if not apartment.get(requirement, False):
                distance = self.find_distance(apartments, apartment_index, requirement, n)
                
                #Si no se puede acceder al servicio, apartamento inválido
                if distance == -1:
                    return (False, float('inf'), float('inf'))
                
                total_distance += distance
                max_distance = max(max_distance, distance)
        
        return (True, total_distance, max_distance)

    def find_best_apartments(self, apartments: List[Dict], required_services: List[str]) -> List[int]:
        """Encuentra mejores apartamentos basado en criterios de distancia"""
        if not apartments or not required_services:
            return []
        
        recommendations = []
        min_total_distance = float('inf')
        min_max_distance = float('inf')
        n = len(apartments)
        
        #Evaluar cada apartamento
        for i in range(n):
            is_valid, total_distance, max_distance = self.calculate_apartment_score(
                apartments, i, required_services
            )
            
            if not is_valid:
                continue
            
            #Determinar si es mejor que los actuales
            if (total_distance < min_total_distance or 
                (total_distance == min_total_distance and max_distance < min_max_distance)):
                #Nuevo mejor apartamento
                min_total_distance = total_distance
                min_max_distance = max_distance
                recommendations = [i]
                
            elif total_distance == min_total_distance and max_distance == min_max_distance:
                #Apartamento con mismo puntaje óptimo
                recommendations.append(i)
        
        return recommendations

    def recommend_constructions_lab1_original(self, input1: Dict, input2: Dict) -> List[str]:
        """Versión original Lab 1 para datos con estructura completa"""
        try:
            #Normalizar formato de entrada
            if isinstance(input1, list):
                input1 = input1[0] if input1 else {}
            if isinstance(input2, list):
                input2 = input2[0] if input2 else {}
            
            #Extraer datos estructurados
            services = input1.get("services", {})
            buildings = input1.get("builds", {})
            
            building_type = input2.get("typeBuilder", "")
            budget = input2.get("budget", 0.0)
            required_services = input2.get("requiredServices", [])
            
            #Filtrar según tipo de construcción
            if building_type == "Apartments":
                pet_friendly = input2.get("wannaPetFriendly", False)
                return self.filter_apartments(
                    buildings.get("Apartments", []), 
                    pet_friendly, 
                    budget, 
                    services, 
                    required_services
                )
            
            elif building_type == "Houses":
                min_danger = input2.get("minDanger", "Red")
                return self.filter_houses(
                    buildings.get("Houses", []), 
                    min_danger, 
                    budget, 
                    services, 
                    required_services
                )
            
            elif building_type == "Premises":
                commercial_activity = input2.get("commercialActivity", "")
                return self.filter_premises(
                    buildings.get("Premises", []), 
                    commercial_activity, 
                    budget, 
                    services, 
                    required_services
                )
            
            return []
            
        except Exception as e:
            print(f"Error en recommend_constructions_lab1_original: {e}")
            import traceback
            traceback.print_exc()
            return []

    def filter_apartments_objects(self, apartments: List[Dict], pet_friendly: bool, budget: float) -> List[Dict]:
        """Filtra apartamentos y devuelve objetos completos"""
        filtered_apartments = []
        
        for apartment in apartments:
            #Verificar política de mascotas
            apartment_pet_friendly = apartment.get("isPetFriendly", False)
            if apartment_pet_friendly != pet_friendly:
                continue
            
            #Verificar presupuesto
            price = apartment.get("price", float('inf'))
            if price > budget:
                continue
                
            filtered_apartments.append(apartment)
        
        return filtered_apartments
    
    def filter_houses_objects(self, houses: List[Dict], min_danger_level: str, budget: float) -> List[Dict]:
        """Filtra casas y devuelve objetos completos"""
        accepted_colors = self.SECURITY_LEVELS.get(min_danger_level, ["Red"])
        filtered_houses = []
        
        for house in houses:
            #Verificar nivel de seguridad
            house_danger = house.get("zoneDangerous", "Red")
            if house_danger not in accepted_colors:
                continue
            
            #Verificar presupuesto
            price = house.get("price", float('inf'))
            if price > budget:
                continue
                
            filtered_houses.append(house)
        
        return filtered_houses
    
    def filter_premises_objects(self, premises: List[Dict], commercial_activity: str, budget: float) -> List[Dict]:
        """Filtra locales comerciales y devuelve objetos completos"""
        filtered_premises = []
        
        for premise in premises:
            #Verificar actividades comerciales permitidas
            allowed_activities = premise.get("commercialActivities", [])
            if commercial_activity not in allowed_activities:
                continue
            
            #Verificar presupuesto
            price = premise.get("price", float('inf'))
            if price > budget:
                continue
                
            filtered_premises.append(premise)
        
        return filtered_premises

    def recommend_constructions_lab2(self, input1: Dict, input2: Dict) -> List[str]:
        """Lab 2: Sistema de recomendaciones sin validación de servicios"""
        try:
            #Debug de tipos de datos
            print(f"DEBUG - input1 type: {type(input1)}, input2 type: {type(input2)}")
            
            #Normalización de formatos de entrada
            if isinstance(input1, str):
                try:
                    input1 = json.loads(input1)
                except:
                    print(f"Error: input1 no es JSON válido: {input1}")
                    return []
            
            if isinstance(input2, str):
                try:
                    input2 = json.loads(input2)
                except:
                    print(f"Error: input2 no es JSON válido: {input2}")
                    return []
            
            #Convertir input1 a lista para procesamiento uniforme
            if isinstance(input1, list):
                if not input1:
                    return []
                input1_data = input1
            else:
                input1_data = [input1]
            
            #Normalizar input2 a diccionario
            if isinstance(input2, list):
                if not input2:
                    return []
                input2 = input2[0]
            
            if not isinstance(input2, dict):
                print(f"Error: input2 no es un diccionario: {type(input2)}")
                return []
            
            #Extraer criterios de búsqueda
            building_type = input2.get("typeBuilder", "")
            budget = input2.get("budget", 0.0)
            
            all_properties = []
            
            #Procesar cada dataset de entrada
            for data in input1_data:
                if not isinstance(data, dict):
                    print(f"Error: elemento de input1 no es un diccionario: {type(data)}")
                    continue
                    
                buildings = data.get("builds", {})
                current_properties = []
                
                #Filtrar según tipo de construcción
                if building_type == "Apartments":
                    pet_friendly = input2.get("wannaPetFriendly", False)
                    current_properties = self.filter_apartments_objects(
                        buildings.get("Apartments", []), pet_friendly, budget
                    )
                elif building_type == "Houses":
                    min_danger = input2.get("minDanger", "Red")
                    current_properties = self.filter_houses_objects(
                        buildings.get("Houses", []), min_danger, budget
                    )
                elif building_type == "Premises":
                    commercial_activity = input2.get("commercialActivity", "")
                    current_properties = self.filter_premises_objects(
                        buildings.get("Premises", []), commercial_activity, budget
                    )
                
                all_properties.extend(current_properties)
            
            #Eliminar duplicados basado en ID único
            seen_ids = set()
            unique_properties = []
            for prop in all_properties:
                if prop["id"] not in seen_ids:
                    seen_ids.add(prop["id"])
                    unique_properties.append(prop)
            
            #Ordenar por precio ascendente
            unique_properties.sort(key=lambda x: x.get("price", float('inf')))
            return [prop["id"] for prop in unique_properties]
            
        except Exception as e:
            print(f"Error in recommend_constructions_lab2: {e}")
            import traceback
            traceback.print_exc()
            return []


class InmueblesGTAuction:
    """
    Sistema de subastas para Inmuebles GT - Lab 3
    Maneja clientes, subastas y genera firmas digitales
    """
    
    def __init__(self):
        """Inicializa el sistema de subastas"""
        self.clientes = {}  #DPI -> datos del cliente
        self.subastas = {}  #property_id -> datos de la subasta
    
    def cargar_clientes(self, archivo_json):
        """Carga clientes desde archivo JSON Lines"""
        with open(archivo_json, 'r', encoding='utf-8') as file:
            for line in file:
                if line.strip():  #Ignorar líneas vacías
                    cliente = json.loads(line)
                    self.clientes[cliente['dpi']] = cliente
    
    def cargar_subastas(self, archivo_json):
        """Carga subastas desde archivo JSON Lines"""
        with open(archivo_json, 'r', encoding='utf-8') as file:
            for line in file:
                if line.strip():  #Ignorar líneas vacías
                    subasta = json.loads(line)
                    self.subastas[subasta['property']] = subasta
    
    def buscar_cliente_por_dpi(self, dpi):
        """Busca cliente por su DPI"""
        return self.clientes.get(dpi, None)
    
    def generar_firma_digital(self, datos):
        """Genera firma digital SHA-256 para garantizar integridad"""
        #Ordenar claves para hash determinístico
        datos_json = json.dumps(datos, sort_keys=True)
        hash_obj = hashlib.sha256(datos_json.encode())
        firma = hash_obj.hexdigest()
        return firma
    
    def procesar_subasta(self, propiedad):
        """Procesa subasta individual para una propiedad"""
        if propiedad not in self.subastas:
            return None
        
        subasta = self.subastas[propiedad]
        clientes_ofertas = subasta['customers']
        num_rechazos = subasta['rejection']
        
        #Crear heap máximo con ofertas (valores negativos)
        ofertas = []
        for cliente in clientes_ofertas:
            #Manejar diferentes formatos de presupuesto
            budget_key = 'Budget' if 'Budget' in cliente else 'budget'
            ofertas.append((-cliente[budget_key], cliente['dpi']))
        
        heapq.heapify(ofertas)
        
        #Rechazar las primeras N ofertas más altas
        rechazos = []
        for _ in range(min(num_rechazos, len(ofertas))):
            if not ofertas:
                break
            presupuesto, dpi = heapq.heappop(ofertas)
            presupuesto = -presupuesto  #Convertir de vuelta a positivo
            rechazos.append((dpi, presupuesto))
            print(f"Se rechazó el dpi {dpi} que tenía un presupuesto {presupuesto}")
        
        #Seleccionar ganador: siguiente oferta más alta
        if ofertas:
            presupuesto_ganador, dpi_ganador = heapq.heappop(ofertas)
            presupuesto_ganador = -presupuesto_ganador  #Convertir de vuelta a positivo
            print(f"El ganador de la oferta fue el dpi {dpi_ganador}, con un presupuesto de {presupuesto_ganador}")
            
            #Obtener datos completos del cliente ganador
            cliente_ganador = self.buscar_cliente_por_dpi(dpi_ganador)
            if cliente_ganador:
                #Construir registro de resultado
                resultado = cliente_ganador.copy()
                resultado['property'] = propiedad
                resultado['budget'] = presupuesto_ganador
                resultado['date'] = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ")[:-3]
                
                #Generar firma digital excluyendo el campo signature
                datos_para_firma = {k: v for k, v in resultado.items() if k != 'signature'}
                resultado['signature'] = self.generar_firma_digital(datos_para_firma)
                
                return resultado
        
        return None
    
    def procesar_todas_subastas(self):
        """Procesa todas las subastas cargadas"""
        resultados = []
        for propiedad in self.subastas:
            print(f"\nProcesando subasta para propiedad: {propiedad}")
            resultado = self.procesar_subasta(propiedad)
            if resultado:
                resultados.append(resultado)
        return resultados


class InmueblesGTSystem:
    """Sistema principal que integra todos los laboratorios"""
    
    def __init__(self):
        """Inicializa el sistema principal"""
        self.recommendation_system = PropertyRecommendationSystem()
        self.auction_system = InmueblesGTAuction()
        self.start_time = None  #Para medir tiempo total del programa
    
    def format_time(self, seconds):
        """Formatea tiempo en segundos a formato legible"""
        if seconds < 0.001:
            return f"{seconds * 1000000:.1f}μs"
        elif seconds < 1:
            return f"{seconds * 1000:.1f}ms"
        elif seconds < 60:
            return f"{seconds:.2f}s"
        else:
            minutes = int(seconds // 60)
            remaining_seconds = seconds % 60
            return f"{minutes}m {remaining_seconds:.2f}s"
    
    def mostrar_menu(self):
        """Muestra el menú principal del sistema"""
        print("\n" + "="*60)
        print("    SISTEMA INMUEBLES GT - LABORATORIOS INTEGRADOS")
        print("="*60)
        print("1. Lab #1 - Sistema de recomendaciones (Validación servicios)")
        print("2. Lab #2 - Sistema de recomendaciones (Sin validación servicios)")
        print("3. Lab #3 - Sistema de subastas")
        print("4. Salir")
        print("="*60)
    
    def mostrar_submenu_archivos(self, lab_num):
        """Muestra submenú para selección de archivos"""
        print(f"\n--- OPCIONES DE ARCHIVOS PARA LAB #{lab_num} ---")
        print("1. Usar archivos predeterminados (fábrica)")
        print("2. Especificar archivos personalizados")
        print("3. Volver al menú principal")
        print("-" * 45)
    
    def ejecutar_lab1(self):
        """Ejecuta Lab 1: Sistema de recomendaciones con validación"""
        print("\n--- LAB #1: SISTEMA DE RECOMENDACIONES (CON VALIDACIÓN) ---")
        
        #Selección de archivo de entrada
        while True:
            self.mostrar_submenu_archivos(1)
            opcion = input("\n👉 Seleccione una opción (1-3): ").strip()
            
            if opcion == "1":
                archivo_entrada = "input_1.jsonl"
                print(f"📁 Usando archivo predeterminado: {archivo_entrada}")
                break
            elif opcion == "2":
                archivo_entrada = input("📝 Ingrese el nombre del archivo (.jsonl): ").strip()
                if not archivo_entrada:
                    print("❌ Debe especificar un nombre de archivo")
                    continue
                break
            elif opcion == "3":
                return
            else:
                print("❌ Opción inválida. Seleccione 1, 2 o 3.")
                continue
        
        #Verificar existencia del archivo
        if not os.path.exists(archivo_entrada):
            print(f"❌ Error: No se encontró el archivo '{archivo_entrada}'")
            print(f"📂 Verifique que el archivo esté en la misma carpeta que el programa")
            return
        
        archivo_salida = "solucion1.jsonl"
        
        #Iniciar medición de tiempo
        start_time = time.time()
        print(f"\n🕐 Iniciando procesamiento a las {time.strftime('%H:%M:%S')}")
        
        try:
            print(f"🔄 Procesando archivo: {archivo_entrada}")
            resultados = []
            total_lines = 0
            
            #Contar líneas totales para mostrar progreso
            with open(archivo_entrada, "r", encoding="utf-8") as file:
                total_lines = sum(1 for line in file if line.strip())
            
            print(f"📊 Total de registros a procesar: {total_lines}")
            
            #Procesamiento línea por línea
            with open(archivo_entrada, "r", encoding="utf-8") as file:
                for line_num, line in enumerate(file, 1):
                    try:
                        if not line.strip():
                            continue
                        
                        #Mostrar progreso cada 100 registros
                        if line_num % 100 == 0 or line_num <= 10:
                            elapsed = time.time() - start_time
                            print(f"⏳ Procesando registro {line_num}/{total_lines} - Tiempo transcurrido: {self.format_time(elapsed)}")
                        
                        data = json.loads(line.strip())
                        
                        #Debug para las primeras líneas
                        if line_num <= 3:
                            print(f"DEBUG línea {line_num}:")
                            print(f"  - input1 type: {type(data.get('input1', []))}")
                            print(f"  - input2 type: {type(data.get('input2', []))}")
                            if isinstance(data.get('input1'), list):
                                print(f"  - input1 length: {len(data.get('input1', []))}")
                            if isinstance(data.get('input2'), list):
                                print(f"  - input2 content: {data.get('input2', [])}")
                        
                        #Ejecutar algoritmo de recomendación
                        resultado = self.recommendation_system.recommend_constructions_lab1(
                            data.get("input1", []), 
                            data.get("input2", [])
                        )
                        resultados.append(resultado)
                        
                    except json.JSONDecodeError as e:
                        print(f"⚠️  Error JSON en línea {line_num}: {e}")
                        resultados.append([])
                    except Exception as e:
                        print(f"⚠️  Error procesando línea {line_num}: {e}")
                        resultados.append([])
            
            #Guardar resultados
            print(f"💾 Guardando resultados en {archivo_salida}...")
            with open(archivo_salida, "w", encoding="utf-8") as output_file:
                for resultado in resultados:
                    output_file.write(json.dumps(resultado, separators=(',', ':')) + "\n")
            
            #Calcular tiempo total y estadísticas
            end_time = time.time()
            total_time = end_time - start_time
            
            print(f"\n✅ Lab #1 completado exitosamente!")
            print(f"⏱️  Tiempo total de ejecución: {self.format_time(total_time)}")
            print(f"📁 Archivo generado: {archivo_salida}")
            print(f"📊 Registros procesados: {len(resultados)}")
            print(f"📈 Recomendaciones con resultados: {sum(1 for r in resultados if r)}")
            print(f"⚡ Promedio por registro: {self.format_time(total_time / len(resultados)) if resultados else 'N/A'}")
            
            #Mostrar algunos resultados de ejemplo
            print(f"\n📋 Ejemplos de resultados:")
            for i, resultado in enumerate(resultados[:5]):
                print(f"  Línea {i+1}: {resultado}")
            
        except Exception as e:
            print(f"❌ Error ejecutando Lab #1: {e}")
            import traceback
            traceback.print_exc()
    
    def ejecutar_lab2(self):
        """Ejecuta Lab 2: Sistema de recomendaciones sin validación"""
        print("\n--- LAB #2: SISTEMA DE RECOMENDACIONES (SIN VALIDACIÓN) ---")
        
        #Selección de archivo de entrada
        while True:
            self.mostrar_submenu_archivos(2)
            opcion = input("\n👉 Seleccione una opción (1-3): ").strip()
            
            if opcion == "1":
                archivo_entrada = "input_2.jsonl"
                print(f"📁 Usando archivo predeterminado: {archivo_entrada}")
                break
            elif opcion == "2":
                archivo_entrada = input("📝 Ingrese el nombre del archivo (.jsonl): ").strip()
                if not archivo_entrada:
                    print("❌ Debe especificar un nombre de archivo")
                    continue
                break
            elif opcion == "3":
                return
            else:
                print("❌ Opción inválida. Seleccione 1, 2 o 3.")
                continue
        
        #Verificar existencia del archivo
        if not os.path.exists(archivo_entrada):
            print(f"❌ Error: No se encontró el archivo '{archivo_entrada}'")
            print(f"📂 Verifique que el archivo esté en la misma carpeta que el programa")
            return
        
        archivo_salida = "solucion2.jsonl"
        
        #Iniciar medición de tiempo
        start_time = time.time()
        print(f"\n🕐 Iniciando procesamiento a las {time.strftime('%H:%M:%S')}")
        
        try:
            print(f"🔄 Procesando archivo: {archivo_entrada}")
            resultados = []
            total_lines = 0
            
            #Contar líneas totales
            with open(archivo_entrada, "r", encoding="utf-8") as file:
                total_lines = sum(1 for line in file if line.strip())
            
            print(f"📊 Total de registros a procesar: {total_lines}")
            
            #Procesamiento principal
            with open(archivo_entrada, "r", encoding="utf-8") as file:
                for line_num, line in enumerate(file, 1):
                    try:
                        if not line.strip():
                            continue
                        
                        #Mostrar progreso
                        if line_num % 50 == 0 or line_num <= 5:
                            elapsed = time.time() - start_time
                            print(f"⏳ Procesando registro {line_num}/{total_lines} - Tiempo: {self.format_time(elapsed)}")
                        
                        #Nueva instancia para cada línea
                        recommendation_system = PropertyRecommendationSystem()
                        
                        data = json.loads(line.strip())
                        resultado = recommendation_system.recommend_constructions_lab2(
                            data.get("input1", {}), 
                            data.get("input2", {})
                        )
                        resultados.append(resultado)
                        
                    except json.JSONDecodeError as e:
                        print(f"⚠️  Error JSON en línea {line_num}: {e}")
                        resultados.append([])
                    except Exception as e:
                        print(f"⚠️  Error procesando línea {line_num}: {e}")
                        resultados.append([])
            
            #Guardar resultados
            print(f"💾 Guardando resultados...")
            with open(archivo_salida, "w", encoding="utf-8") as output_file:
                for resultado in resultados:
                    output_file.write(json.dumps(resultado, separators=(',', ':')) + "\n")
            
            #Estadísticas finales
            end_time = time.time()
            total_time = end_time - start_time
            
            print(f"\n✅ Lab #2 completado exitosamente!")
            print(f"⏱️  Tiempo total de ejecución: {self.format_time(total_time)}")
            print(f"📁 Archivo generado: {archivo_salida}")
            print(f"📊 Registros procesados: {len(resultados)}")
            print(f"📈 Recomendaciones con resultados: {sum(1 for r in resultados if r)}")
            print(f"⚡ Promedio por registro: {self.format_time(total_time / len(resultados)) if resultados else 'N/A'}")
            
        except Exception as e:
            print(f"❌ Error ejecutando Lab #2: {e}")
            import traceback
            traceback.print_exc()
    
    def ejecutar_lab3(self):
        """Ejecuta Lab 3: Sistema de subastas con firmas digitales"""
        print("\n--- LAB #3: SISTEMA DE SUBASTAS ---")
        
        #Selección de archivos de entrada
        while True:
            self.mostrar_submenu_archivos(3)
            opcion = input("\n👉 Seleccione una opción (1-3): ").strip()
            
            if opcion == "1":
                archivo_clientes = "input_customer_3.jsonl"
                archivo_subastas = "input_auctions_3.jsonl"
                print(f"📁 Usando archivos predeterminados:")
                print(f"   - Clientes: {archivo_clientes}")
                print(f"   - Subastas: {archivo_subastas}")
                break
            elif opcion == "2":
                print("📝 Especifique los archivos de entrada:")
                archivo_clientes = input("   Archivo de clientes (.jsonl): ").strip()
                archivo_subastas = input("   Archivo de subastas (.jsonl): ").strip()
                
                if not archivo_clientes or not archivo_subastas:
                    print("❌ Debe especificar ambos archivos")
                    continue
                break
            elif opcion == "3":
                return
            else:
                print("❌ Opción inválida. Seleccione 1, 2 o 3.")
                continue
        
        #Verificar existencia de archivos
        archivos_faltantes = []
        if not os.path.exists(archivo_clientes):
            archivos_faltantes.append(archivo_clientes)
        if not os.path.exists(archivo_subastas):
            archivos_faltantes.append(archivo_subastas)
        
        if archivos_faltantes:
            print(f"❌ Error: No se encontraron los siguientes archivos:")
            for archivo in archivos_faltantes:
                print(f"   - {archivo}")
            print(f"📂 Verifique que los archivos estén en la misma carpeta que el programa")
            return
        
        #Iniciar procesamiento con medición de tiempo
        start_time = time.time()
        print(f"\n🕐 Iniciando procesamiento a las {time.strftime('%H:%M:%S')}")
        
        try:
            print(f"🔄 Procesando archivos:")
            print(f"   📋 Cargando clientes desde: {archivo_clientes}")
            
            #Crear nueva instancia del sistema de subastas
            auction_system = InmueblesGTAuction()
            
            #Fase 1: Cargar clientes
            load_start = time.time()
            auction_system.cargar_clientes(archivo_clientes)
            load_clients_time = time.time() - load_start
            print(f"✅ Clientes cargados: {len(auction_system.clientes)} en {self.format_time(load_clients_time)}")
            
            #Fase 2: Cargar subastas
            print(f"   🏷️  Cargando subastas desde: {archivo_subastas}")
            load_start = time.time()
            auction_system.cargar_subastas(archivo_subastas)
            load_auctions_time = time.time() - load_start
            print(f"✅ Subastas cargadas: {len(auction_system.subastas)} en {self.format_time(load_auctions_time)}")
            
            #Fase 3: Procesar subastas
            print(f"\n🔄 Procesando {len(auction_system.subastas)} subastas...")
            process_start = time.time()
            resultados = auction_system.procesar_todas_subastas()
            process_time = time.time() - process_start
            
            #Fase 4: Guardar resultados
            print(f"\n💾 Guardando resultados...")
            save_start = time.time()
            with open('solucion3.jsonl', 'w', encoding='utf-8') as f:
                for resultado in resultados:
                    resultado_formato = {
                        "dpi": resultado["dpi"],
                        "budget": resultado["budget"],
                        "date": resultado["date"],
                        "firstName": resultado["firstName"],
                        "lastName": resultado["lastName"],
                        "birthDate": resultado["birthDate"],
                        "job": resultado["job"],
                        "placeJob": resultado["placeJob"],
                        "salary": resultado["salary"],
                        "property": resultado["property"],
                        "signature": resultado["signature"]
                    }
                    f.write(json.dumps(resultado_formato, separators=(',', ':')) + '\n')
            save_time = time.time() - save_start
            
            #Estadísticas finales
            end_time = time.time()
            total_time = end_time - start_time
            
            print(f"\n✅ Lab #3 completado exitosamente!")
            print(f"⏱️  Tiempo total de ejecución: {self.format_time(total_time)}")
            print(f"   📋 Carga de clientes: {self.format_time(load_clients_time)}")
            print(f"   🏷️  Carga de subastas: {self.format_time(load_auctions_time)}")
            print(f"   🔄 Procesamiento: {self.format_time(process_time)}")
            print(f"   💾 Guardado: {self.format_time(save_time)}")
            print(f"📁 Archivo generado: solucion3.jsonl")
            print(f"🏆 Subastas procesadas exitosamente: {len(resultados)}")
            
            if process_time > 0:
                print(f"⚡ Promedio por subasta: {self.format_time(process_time / len(auction_system.subastas))}")
            
            #Mostrar ejemplo de resultado
            if resultados:
                print(f"\n📋 Ejemplo de resultado:")
                resultado_ejemplo = {
                    "dpi": resultados[0]["dpi"],
                    "budget": resultados[0]["budget"],
                    "property": resultados[0]["property"],
                    "firstName": resultados[0]["firstName"],
                    "lastName": resultados[0]["lastName"]
                }
                print(json.dumps(resultado_ejemplo, indent=2))
            
        except Exception as e:
            print(f"❌ Error ejecutando Lab #3: {e}")
            import traceback
            traceback.print_exc()
    
    def ejecutar(self):
        """Método principal que ejecuta el sistema completo"""
        self.start_time = time.time()
        print("🏠 Bienvenido al Sistema Inmuebles GT")
        print(f"🕐 Sesión iniciada a las {time.strftime('%H:%M:%S')}")
        
        while True:
            self.mostrar_menu()
            
            try:
                opcion = input("\n👉 Seleccione una opción (1-4): ").strip()
                
                if opcion == "1":
                    self.ejecutar_lab1()
                elif opcion == "2":
                    self.ejecutar_lab2()
                elif opcion == "3":
                    self.ejecutar_lab3()
                elif opcion == "4":
                    #Mostrar tiempo total de sesión
                    total_session_time = time.time() - self.start_time
                    print(f"\n⏱️  Tiempo total de sesión: {self.format_time(total_session_time)}")
                    print("👋 ¡Gracias por usar el Sistema Inmuebles GT!")
                    break
                else:
                    print("❌ Opción inválida. Por favor seleccione 1, 2, 3 o 4.")
                
                if opcion in ["1", "2", "3"]:
                    input("\n⏸️  Presione Enter para continuar...")
                    
            except KeyboardInterrupt:
                total_session_time = time.time() - self.start_time
                print(f"\n\n⏱️  Tiempo total de sesión: {self.format_time(total_session_time)}")
                print("👋 ¡Hasta luego!")
                break
            except Exception as e:
                print(f"❌ Error inesperado: {e}")


def main():
    """Función principal del programa"""
    sistema = InmueblesGTSystem()
    sistema.ejecutar()


if __name__ == "__main__":
    main()