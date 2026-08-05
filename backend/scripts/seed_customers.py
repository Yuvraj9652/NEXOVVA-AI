import os
import sys
import django

# Setup Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from apps.organizations.models import Organization
from apps.accounts.models import CustomUser
from apps.customers.models import Customer, CustomerAddress, CustomerRequirement, CustomerSource

def seed_customers():
    org = Organization.objects.first()
    if not org:
        org = Organization.objects.create(name="Nexova Demo Org", slug="nexova-demo")
    
    user = CustomUser.objects.first()

    customers_data = [
        {
            "first_name": "Sarinah",
            "last_name": "Shah",
            "phone": "8980133121",
            "email": "sarinah.shah@example.com",
            "lead_status": "NEW",
            "priority": "HIGH",
            "company": "Tech Corp",
            "occupation": "Product Manager",
            "city": "Gurugram",
            "state": "Haryana",
            "property_type": "APARTMENT",
            "budget_min": 15000000,
            "budget_max": 35000000,
            "purpose": "SELF_USE",
            "preferred_city": "Gurugram",
        },
        {
            "first_name": "Yuvraj",
            "last_name": "Labana",
            "phone": "7878596585",
            "email": "yuvraj.labana@example.com",
            "lead_status": "NEW",
            "priority": "HIGH",
            "company": "Labana Group",
            "occupation": "Entrepreneur",
            "city": "Bengaluru",
            "state": "Karnataka",
            "property_type": "VILLA",
            "budget_min": 25000000,
            "budget_max": 60000000,
            "purpose": "INVESTMENT",
            "preferred_city": "Bengaluru",
        },
        {
            "first_name": "Neel",
            "last_name": "Patel",
            "phone": "8734071590",
            "email": "neel.patel@example.com",
            "lead_status": "NEW",
            "priority": "MEDIUM",
            "company": "Capital Ventures",
            "occupation": "Investment Banker",
            "city": "Mumbai",
            "state": "Maharashtra",
            "property_type": "PENTHOUSE",
            "budget_min": 30000000,
            "budget_max": 80000000,
            "purpose": "SELF_USE",
            "preferred_city": "Mumbai",
        },
        {
            "first_name": "Ananya",
            "last_name": "Sharma",
            "phone": "9820112233",
            "email": "ananya.sharma@example.com",
            "lead_status": "HOT",
            "priority": "HIGH",
            "company": "Apex Retail",
            "occupation": "Business Owner",
            "city": "Pune",
            "state": "Maharashtra",
            "property_type": "COMMERCIAL",
            "budget_min": 10000000,
            "budget_max": 45000000,
            "purpose": "INVESTMENT",
            "preferred_city": "Pune",
        },
        {
            "first_name": "Rohan",
            "last_name": "Verma",
            "phone": "9910223344",
            "email": "rohan.v@example.com",
            "lead_status": "WARM",
            "priority": "MEDIUM",
            "company": "Global Solutions",
            "occupation": "Software Architect",
            "city": "Noida",
            "state": "Uttar Pradesh",
            "property_type": "APARTMENT",
            "budget_min": 8000000,
            "budget_max": 18000000,
            "purpose": "SELF_USE",
            "preferred_city": "Gurugram",
        },
        {
            "first_name": "Priya",
            "last_name": "Nair",
            "phone": "9744556677",
            "email": "priya.nair@example.com",
            "lead_status": "CONTACTED",
            "priority": "LOW",
            "company": "Horizon Health",
            "occupation": "Surgeon",
            "city": "Kochi",
            "state": "Kerala",
            "property_type": "VILLA",
            "budget_min": 20000000,
            "budget_max": 40000000,
            "purpose": "SELF_USE",
            "preferred_city": "Bengaluru",
        },
        {
            "first_name": "Vikramaditya",
            "last_name": "Singh",
            "phone": "9876543210",
            "email": "vikram.singh@example.com",
            "lead_status": "VISITED",
            "priority": "HIGH",
            "company": "Royal Heritage",
            "occupation": "Hotelier",
            "city": "Jaipur",
            "state": "Rajasthan",
            "property_type": "VILLA",
            "budget_min": 35000000,
            "budget_max": 75000000,
            "purpose": "INVESTMENT",
            "preferred_city": "Jaipur",
        },
        {
            "first_name": "Kavya",
            "last_name": "Reddy",
            "phone": "9123456789",
            "email": "kavya.reddy@example.com",
            "lead_status": "BOOKED",
            "priority": "HIGH",
            "company": "Deccan Pharma",
            "occupation": "Research Director",
            "city": "Hyderabad",
            "state": "Telangana",
            "property_type": "APARTMENT",
            "budget_min": 18000000,
            "budget_max": 32000000,
            "purpose": "SELF_USE",
            "preferred_city": "Hyderabad",
        },
        {
            "first_name": "Aarav",
            "last_name": "Mehta",
            "phone": "9811223344",
            "email": "aarav.m@example.com",
            "lead_status": "CLOSED",
            "priority": "MEDIUM",
            "company": "Textile India",
            "occupation": "Industrialist",
            "city": "Ahmedabad",
            "state": "Gujarat",
            "property_type": "PLOT",
            "budget_min": 12000000,
            "budget_max": 28000000,
            "purpose": "INVESTMENT",
            "preferred_city": "Ahmedabad",
        },
        {
            "first_name": "Ishita",
            "last_name": "Sen",
            "phone": "9833445566",
            "email": "ishita.sen@example.com",
            "lead_status": "NEW",
            "priority": "HIGH",
            "company": "Creative Media",
            "occupation": "Art Director",
            "city": "Kolkata",
            "state": "West Bengal",
            "property_type": "APARTMENT",
            "budget_min": 9000000,
            "budget_max": 22000000,
            "purpose": "SELF_USE",
            "preferred_city": "Mumbai",
        },
    ]

    for cdata in customers_data:
        city = cdata.pop("city")
        state = cdata.pop("state")
        property_type = cdata.pop("property_type")
        budget_min = cdata.pop("budget_min")
        budget_max = cdata.pop("budget_max")
        purpose = cdata.pop("purpose")
        preferred_city = cdata.pop("preferred_city")

        customer, created = Customer.objects.get_or_create(
            phone=cdata["phone"],
            organization=org,
            defaults={**cdata, "created_by": user}
        )

        if not created:
            for k, v in cdata.items():
                setattr(customer, k, v)
            customer.save()

        CustomerAddress.objects.update_or_create(
            customer=customer,
            defaults={"organization": org, "city": city, "state": state, "country": "India"}
        )

        CustomerRequirement.objects.update_or_create(
            customer=customer,
            defaults={
                "organization": org,
                "property_type": property_type,
                "budget_min": budget_min,
                "budget_max": budget_max,
                "purpose": purpose,
                "preferred_city": preferred_city,
            }
        )

        CustomerSource.objects.update_or_create(
            customer=customer,
            defaults={"organization": org, "source_type": Customer.SourceType.EXISTING_CUSTOMER}
        )

        print(f"Customer {customer.first_name} {customer.last_name} ({customer.phone}) seeded!")

if __name__ == "__main__":
    seed_customers()
