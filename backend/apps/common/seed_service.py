import os
import uuid
import datetime
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.db import transaction
from django.conf import settings

# Import scripts exactly once
from scripts import create_app_boilerplate
from scripts import seed_projects
from scripts import seed_customers
from scripts import seed_broadcast_campaigns
from scripts import seed_broadcast_app_campaigns

from apps.organizations.models import Organization
from apps.properties.models import Project, Unit
from apps.contacts.models import Contact
from apps.companies.models import Company
from apps.leads.models import Lead
from apps.pipeline.models import PipelineStage, Deal
from apps.tasks.models import Task
from apps.employees.models import Employee
from apps.documents.models import Document
from apps.notifications.models import Notification
from apps.audit.models import ActivityLog
from apps.accounts.models import UserProfile
from apps.communications.models import BroadcastCampaign

User = get_user_model()

def seed_organization_data(organization: Organization, admin_user: User):
    """
    Seeds the newly verified organization tenant workspace with a rich dataset of realistic real estate CRM objects:
    - Default pipeline stages (New, Contacted, Proposal, Negotiation, Closed Won)
    - Sales Agents (Employees / CustomUser records)
    - Projects & units inventory
    - Contacts & companies
    - Qualified leads & pipeline deals
    - Completed and pending tasks/meetings
    - OCR document manager files
    - Sample workspace notifications & activity audits
    """
    print(f"Seeding database for Organization: {organization.name}...")

    with transaction.atomic():
        # 1. Create pipeline stages
        stages = {}
        stage_names = ["New", "Contacted", "Proposal", "Negotiation", "Closed Won"]
        for idx, s_name in enumerate(stage_names):
            stage = PipelineStage.objects.create(
                organization=organization,
                name=s_name,
                order=idx
            )
            stages[s_name] = stage

        # 2. Create sub-users as Sales Agents
        agents_data = [
            {"username": f"priya_{organization.id}", "email": f"priya_{organization.id}@{organization.name.lower().replace(' ', '')}.com", "first_name": "Priya", "last_name": "Sharma", "title": "Senior Sales Agent"},
            {"username": f"rohan_{organization.id}", "email": f"rohan_{organization.id}@{organization.name.lower().replace(' ', '')}.com", "first_name": "Rohan", "last_name": "Iyer", "title": "Real Estate Broker"}
        ]
        
        seeded_users = []
        for a in agents_data:
            user = User.objects.create(
                username=a["username"],
                email=a["email"],
                first_name=a["first_name"],
                last_name=a["last_name"],
                is_email_verified=True
            )
            user.set_password("Nexova123!")
            user.save()
            
            # Setup profiles
            user_profile, _ = UserProfile.objects.get_or_create(user=user)
            user_profile.organization = organization
            user_profile.role = UserProfile.Roles.AGENT
            user_profile.save()
            
            # Setup employee profile
            Employee.objects.create(
                organization=organization,
                user=user,
                job_title=a["title"],
                phone="+91 98765 43210",
                hire_date=datetime.date.today(),
                status=Employee.Statuses.ACTIVE
            )
            seeded_users.append(user)

        active_users = [admin_user] + seeded_users

        # 3. Create properties/projects & units
        projects_data = [
            {"name": "Oakwood Residency", "desc": "Premium luxury residential apartments in downtown district."},
            {"name": "Skyline Towers", "desc": "Ultra-modern high-rise commercial and residential complex."},
            {"name": "Green Valley", "desc": "Eco-friendly family townhomes surrounding central gardens."},
            {"name": "Riverside Apartments", "desc": "Scenic riverside views with modern high-end amenities."}
        ]
        
        projects = []
        for p in projects_data:
            proj = Project.objects.create(
                organization=organization,
                name=p["name"],
                description=p["desc"]
            )
            projects.append(proj)

        # Create Units
        units_spec = [
            {"name": "Apt 402 - Oakwood", "price": 480000.00, "project": projects[0], "bedrooms": 3, "bathrooms": 3, "area": 1800},
            {"name": "Apt 1105 - Skyline", "price": 890000.00, "project": projects[1], "bedrooms": 4, "bathrooms": 4, "area": 2400},
            {"name": "Villa 12 - Green Valley", "price": 350000.00, "project": projects[2], "bedrooms": 3, "bathrooms": 2, "area": 1500},
            {"name": "Apt 201 - Riverside", "price": 520000.00, "project": projects[3], "bedrooms": 2, "bathrooms": 2, "area": 1200}
        ]
        
        for u in units_spec:
            Unit.objects.create(
                organization=organization,
                project=u["project"],
                name=u["name"],
                address="123 Real Estate Boulevard",
                price=u["price"],
                bedrooms=u["bedrooms"],
                bathrooms=u["bathrooms"],
                area_sqft=u["area"],
                status=Unit.Statuses.AVAILABLE
            )

        # 4. Create Companies
        companies = [
            Company.objects.create(organization=organization, name="Global Tech Corp", website="https://globaltech.com", industry="Technology", address="Tech Hub Zone 1"),
            Company.objects.create(organization=organization, name="Nexus Capital", website="https://nexuscap.com", industry="Finance", address="Commercial Tower 2")
        ]

        # 5. Create Contacts
        contacts_data = [
            {"first_name": "Aarav", "last_name": "Sharma", "email": "aarav.sharma@example.com", "phone": "+91 99009 88776", "status": Contact.Statuses.LEAD, "assigned": active_users[0]},
            {"first_name": "Priya", "last_name": "Mehta", "email": "priya.mehta@example.com", "phone": "+91 98888 77777", "status": Contact.Statuses.ACTIVE, "assigned": active_users[1]},
            {"first_name": "Rohan", "last_name": "Iyer", "email": "rohan.iyer@example.com", "phone": "+91 97777 66666", "status": Contact.Statuses.ACTIVE, "assigned": active_users[2]},
            {"first_name": "Sneha", "last_name": "Kapoor", "email": "sneha.k@example.com", "phone": "+91 96666 55555", "status": Contact.Statuses.LEAD, "assigned": active_users[0]}
        ]

        seeded_contacts = []
        for c in contacts_data:
            contact = Contact.objects.create(
                organization=organization,
                first_name=c["first_name"],
                last_name=c["last_name"],
                email=c["email"],
                phone=c["phone"],
                status=c["status"],
                assigned_to=c["assigned"]
            )
            seeded_contacts.append(contact)

        # 6. Create Leads & Deals
        leads_data = [
            {"title": "Aarav Sharma - Oakwood Residency Buyer", "contact": seeded_contacts[0], "company": companies[0], "budget": 480000.00, "score": 94, "status": Lead.Statuses.QUALIFIED},
            {"title": "Sneha Kapoor - Riverside Investor", "contact": seeded_contacts[3], "company": companies[1], "budget": 520000.00, "score": 78, "status": Lead.Statuses.NEW}
        ]

        for l in leads_data:
            lead = Lead.objects.create(
                organization=organization,
                contact=l["contact"],
                company=l["company"],
                title=l["title"],
                budget=l["budget"],
                score=l["score"],
                status=l["status"],
                notes="Budget & location alignment verified via outbound AI call enrichment."
            )
            
            # Create Deal if Qualified
            if l["status"] == Lead.Statuses.QUALIFIED:
                Deal.objects.create(
                    organization=organization,
                    title=f"Deal - {l['title']}",
                    stage=stages["Proposal"],
                    amount=l["budget"],
                    close_date=datetime.date.today() + datetime.timedelta(days=30),
                    assigned_to=active_users[0],
                    contact=l["contact"],
                    company=l["company"]
                )

        # Create active deal for won/closed charts
        Deal.objects.create(
            organization=organization,
            title="Closed Deal - Priya Mehta Skyline",
            stage=stages["Closed Won"],
            amount=890000.00,
            close_date=datetime.date.today() - datetime.timedelta(days=5),
            assigned_to=active_users[1],
            contact=seeded_contacts[1],
            company=companies[1]
        )

        # 7. Create Tasks (Meetings / Site Visits)
        Task.objects.create(
            organization=organization,
            title="Site Visit: Aarav Sharma - Oakwood Apt 402",
            description="Escort client for physical layout inspection.",
            due_date=timezone.now() + datetime.timedelta(days=1),
            completed=False,
            assigned_to=active_users[0],
            contact=seeded_contacts[0]
        )
        Task.objects.create(
            organization=organization,
            title="Document Review: Skyline Commercial Terms",
            description="Assess Nexus Capital lease requirements.",
            due_date=timezone.now() - datetime.timedelta(days=2),
            completed=True,
            assigned_to=active_users[1],
            contact=seeded_contacts[1]
        )

        # 8. Create Campaigns
        BroadcastCampaign.objects.create(
            organization=organization,
            name="Oakwood Residency Launch",
            status=BroadcastCampaign.Statuses.ACTIVE,
            reach="2.4K",
            date=datetime.date.today() - datetime.timedelta(days=10)
        )
        BroadcastCampaign.objects.create(
            organization=organization,
            name="Skyline Towers Update",
            status=BroadcastCampaign.Statuses.SCHEDULED,
            reach="1.8K",
            date=datetime.date.today() + datetime.timedelta(days=5)
        )
        BroadcastCampaign.objects.create(
            organization=organization,
            name="Green Valley Phase 2",
            status=BroadcastCampaign.Statuses.COMPLETED,
            reach="3.1K",
            date=datetime.date.today() - datetime.timedelta(days=15)
        )
        BroadcastCampaign.objects.create(
            organization=organization,
            name="Riverside Apartments",
            status=BroadcastCampaign.Statuses.DRAFT,
            reach="-",
            date=datetime.date.today() + datetime.timedelta(days=10)
        )

        # 9. Create Documents
        # Build document records in DB and mock files
        docs_specs = [
            {"name": "Oakwood Residency Specifications", "text": "Spec sheet: Oakwood Residency offers luxury apartments with 3 beds, pool access, modern clubhouse, and central district accessibility. Structural designs compliant with seismic zone bounds."},
            {"name": "Market Analysis Report Q2", "text": "Q2 Real estate trends show a 12% rise in downtown residential demands. Average price index per sqft holds at $300. Commercial units demand steady."}
        ]

        # Make sure documents directory exists in media root
        media_doc_dir = os.path.join(settings.MEDIA_ROOT, "documents")
        os.makedirs(media_doc_dir, exist_ok=True)

        for idx, d_spec in enumerate(docs_specs):
            file_name = f"doc_{idx}_{uuid.uuid4().hex[:6]}.txt"
            file_path = os.path.join(media_doc_dir, file_name)
            
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(d_spec["text"])
                
            Document.objects.create(
                organization=organization,
                name=d_spec["name"],
                file=f"documents/{file_name}",
                extracted_text=d_spec["text"],
                version=1
            )

        # 9. Create Notifications & Activity Logs
        Notification.objects.create(
            organization=organization,
            recipient=admin_user,
            title="AI Lead Enrichment Completed",
            message="Lead Aarav Sharma was qualified and enrichment score computed at 94%.",
            notification_type=Notification.Types.SYSTEM
        )

        ActivityLogService.log_activity(
            organization=organization,
            user=admin_user,
            action="organization_seeded",
            target_type="organization",
            target_id=organization.id,
            description=f"Workspace organization '{organization.name}' seeded with demo portfolio items."
        )

        print(f"Seeding completed successfully for {organization.name}.")


class ActivityLogService:
    @staticmethod
    def log_activity(organization, user, action, target_type, target_id=None, description=""):
        return ActivityLog.objects.create(
            organization=organization,
            user=user,
            action=action,
            target_type=target_type,
            target_id=target_id,
            description=description
        )
