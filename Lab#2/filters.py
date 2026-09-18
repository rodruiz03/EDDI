def filter_by_services(global_services, required_services):
    """Verifica que todos los servicios requeridos estén disponibles."""
    return all(global_services.get(service, False) for service in required_services)

def filter_apartments(apartments, pet_pref, budget):
    filtered = []
    for apt in apartments:
        if pet_pref is not None and apt.get("isPetFriendly") != pet_pref:
            continue
        if apt["price"] > budget:
            continue
        filtered.append(apt)
    return filtered

def filter_houses(houses, min_danger, budget):
    danger_mapping = {
        "Red": ["Red"],
        "Orange": ["Red", "Orange"],
        "Yellow": ["Red", "Orange", "Yellow"],
        "Green": ["Red", "Orange", "Yellow", "Green"]
    }
    allowed_levels = danger_mapping.get(min_danger, [])
    filtered = []
    for house in houses:
        if house.get("zoneDangerous") not in allowed_levels:
            continue
        if house["price"] > budget:
            continue
        filtered.append(house)
    return filtered

def filter_premises(premises, required_activity, budget):
    filtered = []
    for premise in premises:
        if required_activity not in premise.get("commercialActivities", []):
            continue
        if premise["price"] > budget:
            continue
        filtered.append(premise)
    return filtered
