import os
import sys
import django

# Setup Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from apps.organizations.models import Organization
from apps.accounts.models import CustomUser
from apps.properties.models import Project
from apps.knowledge_base.models import ProjectMedia, ProjectAnalytics, ProjectAmenity, ProjectFAQ, ProjectHighlight

def seed():
    org = Organization.objects.first()
    if not org:
        org = Organization.objects.create(name="Nexova Demo Org", slug="nexova-demo")
    
    user = CustomUser.objects.first()
    
    projects_data = [
        {
            "name": "DLF Cyber Horizon",
            "builder": "DLF Homes",
            "property_type": "APARTMENT",
            "status": "ONGOING",
            "city": "Gurugram",
            "state": "Haryana",
            "address": "Golf Course Extension Road, Sector 65",
            "starting_price": 15000000,
            "max_price": 32000000,
            "rera_number": "HRERA-GGM-2024-890",
            "image_url": "https://images.unsplash.com/photo-1545324418-cc1a3fa10c00?w=800&h=500&fit=crop",
            "description": "Ultra luxury 3 & 4 BHK residences with private elevators, infinity pool, and sky deck views. Designed by world-renowned architects.",
            "short_description": "Luxury high-rise apartments in Sector 65 Gurugram.",
            "seo_description": "Buy luxury 3 & 4 BHK apartments in Sector 65 Gurugram at DLF Cyber Horizon.",
            "whatsapp_description": "DLF Cyber Horizon: Premium 3 & 4 BHK Luxury Apartments in Sector 65 Gurugram. Prices starting at ₹1.5 Cr.",
            "ai_processed": True,
            "ai_generated_summary": "DLF Cyber Horizon is a premier ultra-luxury residential high-rise project featuring modern architecture, world-class amenities, and strategic connectivity to Cyber City and Golf Course Road.",
            "ai_generated_highlights": ["Private Elevators for every unit", "Infinity Pool on 45th floor sky lounge", "75% open landscapes & water bodies"],
            "ai_generated_keywords": ["Luxury Apartments", "Gurugram Real Estate", "DLF Homes", "Golf Course Road", "High Return Investment"],
            "ai_generated_tags": ["RERA Approved", "High ROI", "Luxury Living"],
        },
        {
            "name": "Prestige Elysian Woods",
            "builder": "Prestige Group",
            "property_type": "VILLA",
            "status": "UPCOMING",
            "city": "Bengaluru",
            "state": "Karnataka",
            "address": "Bannerghatta Main Road",
            "starting_price": 28000000,
            "max_price": 55000000,
            "rera_number": "PRM/KA/RERA/1251/310/PR/240101",
            "image_url": "https://images.unsplash.com/photo-1600596542815-ffad4c1539a9?w=800&h=500&fit=crop",
            "description": "Exclusive gated community of 4 & 5 BHK luxury villas surrounded by lush greenery, clubhouse, private gardens, and solar power.",
            "short_description": "Premium villa township near Bannerghatta National Park.",
            "seo_description": "Luxury 4 & 5 BHK villas for sale on Bannerghatta Main Road Bengaluru by Prestige Group.",
            "whatsapp_description": "Prestige Elysian Woods: 4 & 5 BHK Independent Luxury Villas in Bengaluru. Starting ₹2.8 Cr.",
            "ai_processed": True,
            "ai_generated_summary": "Prestige Elysian Woods offers eco-friendly ultra-luxury villas in Bengaluru's tech corridor with solar integration and private pools.",
            "ai_generated_highlights": ["Individual Solar Power Backup", "Private Heated Swimming Pools", "Exclusive 40,000 sq ft Clubhouse"],
            "ai_generated_keywords": ["Luxury Villas Bengaluru", "Prestige Group", "Bannerghatta Road", "Gated Community"],
            "ai_generated_tags": ["Eco Friendly", "Gated Community", "Villa Township"],
        },
        {
            "name": "Oberoi Sky City",
            "builder": "Oberoi Realty",
            "property_type": "PENTHOUSE",
            "status": "ONGOING",
            "city": "Mumbai",
            "state": "Maharashtra",
            "address": "Borivali East, Western Express Highway",
            "starting_price": 35000000,
            "max_price": 80000000,
            "rera_number": "P51800001578",
            "image_url": "https://images.unsplash.com/photo-1512917774080-9991f1c4c750?w=800&h=500&fit=crop",
            "description": "Duplex sky penthouses offering 360-degree panoramic skyline and sea views, smart automation, and private plunge pool.",
            "short_description": "Iconic penthouses on Western Express Highway Mumbai.",
            "seo_description": "Duplex Sky Penthouses for sale in Borivali East Mumbai at Oberoi Sky City.",
            "whatsapp_description": "Oberoi Sky City: Duplex Sky Penthouses with 360 Sky Views in Borivali East Mumbai.",
            "ai_processed": True,
            "ai_generated_summary": "Oberoi Sky City stands as a landmark skyscraper offering lavish duplex penthouses with direct Western Express Highway and Metro connectivity.",
            "ai_generated_highlights": ["Direct Metro Connectivity", "Plunge Pool on Sky Deck", "Concierge Service 24/7"],
            "ai_generated_keywords": ["Mumbai Penthouses", "Oberoi Realty", "Borivali East", "Sky City"],
            "ai_generated_tags": ["Sea View", "Metro Connected", "Penthouse"],
        },
        {
            "name": "Godrej Waterfront Commercial",
            "builder": "Godrej Properties",
            "property_type": "COMMERCIAL",
            "status": "DRAFT",
            "city": "Pune",
            "state": "Maharashtra",
            "address": "Kharadi IT Park",
            "starting_price": 9500000,
            "max_price": 45000000,
            "rera_number": "P52100028912",
            "image_url": "https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?w=800&h=500&fit=crop",
            "description": "Grade-A commercial office spaces and high-street retail shops in Kharadi IT Corridor with 100% power backup and EV charging.",
            "short_description": "Prime IT park office spaces in Kharadi Pune.",
            "seo_description": "Grade A commercial office spaces for sale in Kharadi Pune by Godrej Properties.",
            "whatsapp_description": "Godrej Waterfront Commercial: Grade-A IT Offices & Retail Outlets in Kharadi Pune.",
            "ai_processed": False,
            "ai_generated_summary": "",
            "ai_generated_highlights": [],
            "ai_generated_keywords": [],
            "ai_generated_tags": [],
        },
        {
            "name": "Sobha Dream Acres",
            "builder": "Sobha Limited",
            "property_type": "APARTMENT",
            "status": "PAST",
            "city": "Bengaluru",
            "state": "Karnataka",
            "address": "Panathur Main Road, Balagere",
            "starting_price": 6500000,
            "max_price": 14000000,
            "rera_number": "PRM/KA/RERA/1251/310/PR/170915",
            "image_url": "https://images.unsplash.com/photo-1570129477492-45c003edd2be?w=800&h=500&fit=crop",
            "description": "81-acre mega residential township featuring precast technology, 5 clubhouses, and 80% open green space.",
            "short_description": "Completed mega residential township in Balagere.",
            "seo_description": "Sobha Dream Acres completed 1 & 2 BHK apartments in Balagere Bengaluru.",
            "whatsapp_description": "Sobha Dream Acres: Ready to Move 2 BHK Apartments in Balagere Bengaluru.",
            "ai_processed": True,
            "ai_generated_summary": "Sobha Dream Acres is a fully delivered 81-acre township with high rental yield and vibrant community living in Bengaluru east.",
            "ai_generated_highlights": ["81-Acre Land Parcel", "German Precast Construction Quality", "5 Grand Clubhouses"],
            "ai_generated_keywords": ["Ready to Move", "Sobha Limited", "Bengaluru Tech Corridor"],
            "ai_generated_tags": ["Ready to Move", "High Rental Yield"],
        },
    ]

    created_count = 0
    for pdata in projects_data:
        image_url = pdata.pop("image_url", "")
        project, created = Project.objects.get_or_create(
            name=pdata["name"],
            organization=org,
            defaults={**pdata, "image_url": image_url, "created_by": user}
        )
        if not created:
            for k, v in pdata.items():
                setattr(project, k, v)
            project.image_url = image_url
            project.save()

        # Create primary media
        if image_url:
            ProjectMedia.objects.get_or_create(
                organization=org,
                project=project,
                is_primary=True,
                defaults={
                    "media_type": ProjectMedia.MediaType.IMAGE,
                    "file": image_url,
                    "caption": f"{project.name} Cover Image"
                }
            )

        # Create analytics if not exists
        ProjectAnalytics.objects.get_or_create(
            organization=org,
            project=project,
            defaults={
                "interested_customers": 45,
                "ai_recommendations": 128,
                "brochure_downloads": 92,
                "video_views": 340,
                "site_visits": 28,
                "bookings": 12,
                "revenue": float(project.starting_price or 0) * 12,
                "conversion_rate": 8.5
            }
        )

        # Create Amenities
        for amen in [ProjectAmenity.AmenityType.SWIMMING_POOL, ProjectAmenity.AmenityType.GYM, ProjectAmenity.AmenityType.CLUB_HOUSE, ProjectAmenity.AmenityType.SECURITY]:
            ProjectAmenity.objects.get_or_create(
                organization=org,
                project=project,
                amenity_type=amen,
            )

        # Create FAQs
        ProjectFAQ.objects.get_or_create(
            organization=org,
            project=project,
            question="What is the possession date?",
            defaults={"answer": "Possession is scheduled as per RERA timelines."}
        )

        created_count += 1

    print(f"Successfully seeded {created_count} projects!")

if __name__ == "__main__":
    seed()
