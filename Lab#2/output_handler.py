import json

def save_recommendations(recommendations, output_file):
    """
    Guarda la lista de recomendaciones en un archivo.
    Cada línea del archivo es un JSON con la lista de IDs recomendados.
    """
    with open(output_file, "w", encoding="utf-8") as file:
        for rec in recommendations:
            file.write(json.dumps(rec) + "\n")
