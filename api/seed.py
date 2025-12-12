import uuid
from .database import SessionLocal, engine, Base
from .models import Tenant, User

def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    
    try:
        # Check if tenant exists
        if db.query(Tenant).filter(Tenant.name == "Demo Corp").first():
            print("Database already seeded.")
            return

        # Create Tenant
        tenant = Tenant(name="Demo Corp")
        db.add(tenant)
        db.flush()  # to get tenant.id

        # Create User
        user = User(
            email="analyst@example.com", 
            full_name="Alice Analyst", 
            role="analyst",
            tenant_id=tenant.id
        )
        db.add(user)
        
        db.commit()
        print(f"Seeded Tenant: {tenant.name} ({tenant.id})")
        print(f"Seeded User: {user.email}")
        
    except Exception as e:
        print(f"Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed()
