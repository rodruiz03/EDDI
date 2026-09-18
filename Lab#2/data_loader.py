import json

def load_jsonl(file_path):
    """Lee un archivo JSONL y retorna una lista de diccionarios."""
    data = []
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            line = line.strip()
            if line:
                try:
                    data.append(json.loads(line))
                except json.JSONDecodeError as e:
                    print(f"Error leyendo línea: {line}\n{e}")
    return data
