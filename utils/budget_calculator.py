from datetime import timedelta

COST_LEVEL = {
    "low": 0.6,
    "medium": 1.0,
    "high": 1.6
}

BASE_HOTEL_PER_NIGHT = 50.0
BASE_FOOD_PER_PERSON_PER_DAY = 20.0
BASE_TRANSPORT_PER_PERSON = 25.0

def calculate_budget(trip, activities):
    """Return breakdown dict for given trip and list of Activity objects."""
    days = (trip.end_date - trip.start_date).days
    if days <= 0:
        days = 1
    level = COST_LEVEL.get(trip.budget_preference, 1.0)

    hotel = days * BASE_HOTEL_PER_NIGHT * level
    food = days * trip.travelers * BASE_FOOD_PER_PERSON_PER_DAY * level
    transport = trip.travelers * BASE_TRANSPORT_PER_PERSON * level
    activities_cost = sum(a.cost for a in activities) if activities else 0.0

    subtotal = hotel + food + transport + activities_cost
    misc = subtotal * 0.10
    total = subtotal + misc

    per_person = total / trip.travelers if trip.travelers else total
    per_day = total / days

    return {
        "days": days,
        "hotel": round(hotel,2),
        "food": round(food,2),
        "transport": round(transport,2),
        "activities": round(activities_cost,2),
        "misc": round(misc,2),
        "total": round(total,2),
        "per_person": round(per_person,2),
        "per_day": round(per_day,2),
    }
