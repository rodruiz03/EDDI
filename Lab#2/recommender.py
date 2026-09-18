from filters import filter_by_services, filter_apartments, filter_houses, filter_premises

def recommend(client_data):
    map_data = client_data["input1"]
    if isinstance(map_data, list):
        map_data = map_data[0]
    client_prefs = client_data["input2"]

    # Depuración: muestra los servicios y requerimientos
    print("Servicios globales:", map_data["services"])
    print("Servicios requeridos:", client_prefs["requiredServices"])

    if not filter_by_services(map_data["services"], client_prefs["requiredServices"]):
        print("Registro descartado por servicios globales.")
        return []

    type_builder = client_prefs["typeBuilder"]
    constructions = map_data["builds"].get(type_builder, [])
    budget = client_prefs["budget"]

    filtered = []
    if type_builder == "Apartments":
        pet_pref = client_prefs.get("wannaPetFriendly")
        filtered = filter_apartments(constructions, pet_pref, budget)
    elif type_builder == "Houses":
        min_danger = client_prefs.get("minDanger")
        filtered = filter_houses(constructions, min_danger, budget)
    elif type_builder == "Premises":
        required_activity = client_prefs.get("commercialActivity")
        filtered = filter_premises(constructions, required_activity, budget)
    else:
        print("Tipo de construcción no válido:", type_builder)
        return []

    if not filtered:
        print("No se encontraron construcciones válidas para", type_builder)
    else:
        print("Construcciones encontradas:", filtered)

    filtered.sort(key=lambda x: x["price"])
    return [item["id"] for item in filtered]
