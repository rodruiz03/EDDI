import json
import time
import csv

class SearchBar:
    def __init__(self):
        # Utilizamos un diccionario para almacenar las personas por UID (búsqueda O(1))
        self.people_by_id = {}
        # Utilizamos un diccionario para almacenar las personas por nombre completo
        # Cada nombre puede tener múltiples personas asociadas
        self.people_by_name = {}
        # Contadores para INSERT y DELETE
        self.insert_count = 0
        self.delete_count = 0
    
    def load_from_csv(self, file_path):
        """Carga la bitácora desde un archivo CSV."""
        start_time = time.time()
        
        # Reiniciamos los contadores y estructuras si se carga un nuevo archivo
        self.people_by_id.clear()
        self.people_by_name.clear()
        self.insert_count = 0
        self.delete_count = 0
        
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                # Saltamos la primera línea (encabezados)
                next(file)
                for line in file:
                    if line.strip():  # Verificar que la línea no esté vacía
                        parts = line.strip().split(';')
                        if len(parts) == 2:
                            action, person_json = parts
                            self.process_action(action, person_json)
            
            end_time = time.time()
            load_time = end_time - start_time
            
            print(f"\nEstadísticas de carga:")
            print(f"Tiempo de carga inicial: {load_time:.6f} segundos")
            print(f"Operaciones INSERT realizadas: {self.insert_count}")
            print(f"Operaciones DELETE realizadas: {self.delete_count}")
            print(f"Total teórico (INSERT - DELETE): {self.insert_count - self.delete_count}")
            print(f"Total real de personas cargadas: {len(self.people_by_id)}")
            
            # Verificación de integridad
            if self.insert_count - self.delete_count == len(self.people_by_id):
                print("✅ La cantidad de registros coincide con las operaciones realizadas")
            else:
                print("⚠️ ¡Alerta! La cantidad de registros no coincide con las operaciones")
            
            return True, load_time
        
        except FileNotFoundError:
            print(f"Error: No se encontró el archivo {file_path}")
            return False, 0
        except Exception as e:
            print(f"Error al cargar el archivo: {e}")
            return False, 0
    
    def process_action(self, action, person_json):
        """Procesa una acción (INSERT o DELETE) para una persona."""
        try:
            person = json.loads(person_json)
            # Verificamos que la persona tenga los campos necesarios
            if 'firstName' not in person or 'lastName' not in person or 'uid' not in person:
                print(f"Error: Datos de persona incompletos: {person}")
                return
                
            full_name = f"{person['firstName'].lower()} {person['lastName'].lower()}"
            
            if action == "INSERT":
                # Incrementar contador de INSERT
                self.insert_count += 1
                
                # Guardar en el diccionario por UID
                self.people_by_id[person['uid']] = person
                
                # Guardar en el diccionario por nombre completo
                if full_name not in self.people_by_name:
                    self.people_by_name[full_name] = []
                self.people_by_name[full_name].append(person)
                
            elif action == "DELETE":
                # Incrementar contador de DELETE
                self.delete_count += 1
                
                # Eliminar del diccionario por UID
                if person['uid'] in self.people_by_id:
                    deleted_person = self.people_by_id.pop(person['uid'])
                    
                    # Eliminar del diccionario por nombre completo
                    if full_name in self.people_by_name:
                        self.people_by_name[full_name] = [p for p in self.people_by_name[full_name] 
                                                         if p['uid'] != person['uid']]
                        # Si la lista queda vacía, eliminar la clave
                        if not self.people_by_name[full_name]:
                            del self.people_by_name[full_name]
        
        except json.JSONDecodeError:
            print(f"Error al decodificar JSON: {person_json}")
        except Exception as e:
            print(f"Error inesperado: {e}")
    
    def search_by_full_name(self, first_name, last_name):
        """
        Busca personas por nombre completo.
        Retorna una lista de personas que coinciden o None si no hay coincidencias.
        """
        start_time = time.time()
        
        full_name = f"{first_name.lower()} {last_name.lower()}"
        result = self.people_by_name.get(full_name, None)
        
        end_time = time.time()
        search_time = end_time - start_time
        
        print(f"Tiempo de búsqueda por nombre completo: {search_time:.6f} segundos")
        return result
    
    def search_by_id(self, uid):
        """
        Busca una persona por su UID.
        Retorna la persona encontrada o None si no existe.
        """
        start_time = time.time()
        
        result = self.people_by_id.get(uid, None)
        
        end_time = time.time()
        search_time = end_time - start_time
        
        print(f"Tiempo de búsqueda por UID: {search_time:.6f} segundos")
        return result

def main():
    search_bar = SearchBar()
    
    # Solicitar la ruta del archivo hasta que se cargue correctamente
    archivo_cargado = False
    while not archivo_cargado:
        print("\nCargando datos desde la bitácora...")
        file_path = input("Ingrese la ruta del archivo CSV (por defecto 'bitacora.csv'): ") or 'bitacora.csv'
        
        archivo_cargado, load_time = search_bar.load_from_csv(file_path)
        
        if not archivo_cargado:
            print("No se pudo cargar el archivo. Por favor, verifique la ruta e intente nuevamente.")
    
    # Menú interactivo
    while True:
        print("\n=== SISTEMA DE BÚSQUEDA ===")
        print("1. Buscar por nombre completo")
        print("2. Buscar por UID")
        print("3. Salir")
        option = input("Seleccione una opción: ")
        
        if option == '1':
            first_name = input("Ingrese el primer nombre: ")
            last_name = input("Ingrese el apellido: ")
            
            results = search_bar.search_by_full_name(first_name, last_name)
            
            if results:
                print(f"\nSe encontraron {len(results)} resultados:")
                for person in results:
                    # Mostrar resultado en formato JSON compacto
                    print(json.dumps(person, separators=(',', ':')))
            else:
                print("\nNo se encontraron resultados.")
        
        elif option == '2':
            uid = input("Ingrese el UID a buscar: ")
            
            result = search_bar.search_by_id(uid)
            
            if result:
                print("\nPersona encontrada:")
                # Mostrar resultado en formato JSON compacto
                print(json.dumps(result, separators=(',', ':')))
            else:
                print("\nNo se encontró ninguna persona con ese UID.")
        
        elif option == '3':
            print("¡Hasta luego! Saliendo del programa...")
            break
        
        else:
            print("Opción no válida. Intente nuevamente.")

if __name__ == "__main__":
    main()