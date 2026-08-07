import os
import sys
import django
import datetime

# Setup Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from apps.organizations.models import Organization
from apps.properties.models import Project
from apps.customers.models import Customer
from apps.broadcast.models import Campaign

def seed_broadcast_app_campaigns():
    from apps.accounts.models import CustomUser, UserProfile
    user = CustomUser.objects.get(username="check")
    org = UserProfile.objects.get(user=user).organization

    projects = list(Project.objects.all())
    dlf_project = next((p for p in projects if "DLF" in p.name), projects[0] if projects else None)
    prestige_project = next((p for p in projects if "Prestige" in p.name), projects[1] if len(projects) > 1 else None)
    oberoi_project = next((p for p in projects if "Oberoi" in p.name), projects[2] if len(projects) > 2 else None)

    customers = list(Customer.objects.filter(organization=org))
    customer_ids = [c.id for c in customers[:5]] if customers else []

    campaigns_data = [
        {
            "name": "DLF Cyber Horizon Exclusive VIP Launch",
            "subject": "Exclusive Preview: Ultra-Luxury 3 & 4 BHK Residences in Gurugram",
            "status": "Active",
            "target_type": "AI_MATCHED",
            "project": dlf_project,
            "selected_customer_ids": customer_ids,
            "reach": "1450",
            "total_sent": 1450,
            "open_rate": 78.4,
            "click_rate": 46.2,
            "conversion_rate": 18.5,
            "image_url": "https://images.unsplash.com/photo-1545324418-cc1a3fa10c00?w=800&h=500&fit=crop",
            "content": "Discover DLF Cyber Horizon, Gurugram's finest high-rise luxury towers with private sky lounges, infinity pools, and 360 panoramic views.",
        },
        {
            "name": "Prestige Elysian Woods Villa Showcase",
            "subject": "Eco-Friendly Solar-Powered Luxury Villas in Bengaluru",
            "status": "Active",
            "target_type": "SELECTED_CUSTOMERS",
            "project": prestige_project,
            "selected_customer_ids": customer_ids[:3],
            "reach": "890",
            "total_sent": 890,
            "open_rate": 82.1,
            "click_rate": 53.8,
            "conversion_rate": 22.4,
            "image_url": "https://images.unsplash.com/photo-1600596542815-ffad4c1539a9?w=800&h=500&fit=crop",
            "content": "Experience peaceful living surrounded by nature at Prestige Elysian Woods. Private heated pools and 40,000 sq ft clubhouse.",
        },
        {
            "name": "Oberoi Sky City Penthouse Release",
            "subject": "Duplex Sky Penthouses with Sea Views in Borivali East",
            "status": "Scheduled",
            "target_type": "CSV_UPLOAD",
            "project": oberoi_project,
            "selected_customer_ids": [],
            "reach": "2100",
            "total_sent": 2100,
            "open_rate": 65.0,
            "click_rate": 35.4,
            "conversion_rate": 12.1,
            "image_url": "https://images.unsplash.com/photo-1512917774080-9991f1c4c750?w=800&h=500&fit=crop",
            "content": "Panoramic skyline views, smart automation, and direct Metro access at Oberoi Sky City Penthouses.",
        },
        {
            "name": "Godrej Commercial Hub Investor Broadcast",
            "subject": "High Return Grade-A Commercial Spaces in Kharadi Pune",
            "status": "Completed",
            "target_type": "ALL_CUSTOMERS",
            "project": None,
            "selected_customer_ids": [],
            "reach": "3400",
            "total_sent": 3400,
            "open_rate": 59.8,
            "click_rate": 28.9,
            "conversion_rate": 9.4,
            "image_url": "https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?w=800&h=500&fit=crop",
            "content": "Invest in Kharadi's top IT corridor commercial retail and office spaces with guaranteed rental yields up to 8.5% per annum.",
        },
    ]

    for cdata in campaigns_data:
        campaign, created = Campaign.objects.get_or_create(
            name=cdata["name"],
            organization=org,
            defaults={**cdata}
        )
        if not created:
            for k, v in cdata.items():
                setattr(campaign, k, v)
            campaign.save()

        print(f"Broadcast Campaign '{campaign.name}' seeded into apps.broadcast!")

if __name__ == "__main__":
    seed_broadcast_app_campaigns()
