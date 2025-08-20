import json
import random
from datetime import datetime, timedelta
import uuid

PRODUCTS = [
    ("Basic Energy Saver", "Electricity"),
    ("Premium Energy Saver", "Electricity"),
    ("Broadband Saver", "Broadband"),
    ("Eco Power Flex", "Electricity"),
    ("Home Bundle Max", "Bundle")
]

SUPPLIERS = ["EnergyCo Denmark", "Nordic Power", "EcoEnergy Solutions"]

DISCOUNTS = [
    {"description": "5% off electricity bill with broadband bundle", "discount_type": "percentage", "value": 5},
    {"description": "10 EUR monthly loyalty discount", "discount_type": "fixed", "value": 10},
    {"description": "First month free broadband", "discount_type": "fixed", "value": 30}
]

def random_date_pair():
    start = datetime(2024, random.randint(1, 12), random.randint(1, 28))
    end = start + timedelta(days=random.randint(30, 365))
    return start.date().isoformat(), end.date().isoformat()

def random_contract(customer_id):
    product, product_type = random.choice(PRODUCTS)
    start_date, end_date = random_date_pair()
    monthly_rate = round(random.uniform(20, 120), 2)
    
    additional_products = []
    if random.random() < 0.4:  # 40% chance to add an extra
        add_prod, add_type = random.choice(PRODUCTS[1:])
        additional_products.append({
            "product": add_prod,
            "monthly_rate": round(random.uniform(10, 40), 2),
            "currency": "EUR",
            "discounts": random.sample(DISCOUNTS, k=random.randint(0, 2))
        })
    
    return {
        "group_id": customer_id,
        "customer_id": customer_id,
        "contract_id": f"CTR-{uuid.uuid4().hex[:8].upper()}",
        "product": product,
        "product_type": product_type,
        "start_date": start_date,
        "end_date": end_date,
        "renewal_date": None,
        "status": random.choice(["active", "expired", "pending"]),
        "monthly_rate": monthly_rate,
        "currency": "EUR",
        "additional_products": additional_products,
        "discounts": random.sample(DISCOUNTS, k=random.randint(0, 1)),
        "terms": f"Standard {product_type} supply terms v{random.randint(1,3)}.{random.randint(0,9)}",
        "supplier": random.choice(SUPPLIERS),
        "source": "data/contracts.json",
        "last_updated": datetime.utcnow().isoformat() + "Z",
        "validity_flag": True,
        "version": random.randint(1, 3)
    }

if __name__ == "__main__":
    # Generate 10 random contracts for test
    customer_ids = [f"CUST{str(i).zfill(3)}" for i in range(1, 6)]
    contracts = [random_contract(random.choice(customer_ids)) for _ in range(10)]
    
    with open("contracts_generated.json", "w") as f:
        json.dump(contracts, f, indent=2)
    
    print("Generated", len(contracts), "contracts -> contracts_generated.json")
