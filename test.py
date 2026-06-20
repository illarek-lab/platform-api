import asyncio
import importlib
import os
import sys
from pathlib import Path

def get_available_projects():
    # Detect absolute path of repo root
    repo_root = Path(__file__).resolve().parent
    projects_dir = repo_root / "src" / "app" / "projects"
    
    if not projects_dir.exists():
        return []
        
    projects = []
    for entry in os.listdir(projects_dir):
        entry_path = projects_dir / entry
        if entry_path.is_dir() and entry != "__pycache__" and entry != "layout_example":
            projects.append(entry)
    return projects

async def test_postgres(student_code: str):
    print("Testing PostgreSQL (Neon)...")
    try:
        module = importlib.import_module(f"app.projects.{student_code}.infra.db.postgres")
        engine = module.engine
        from sqlalchemy import text
        async with engine.connect() as conn:
            res = await conn.execute(text("SELECT 1"))
            await conn.commit()
            print("✔ PostgreSQL: Connection Successful!")
    except Exception as e:
        print(f"❌ PostgreSQL: Connection Failed! Error: {e}")

async def test_mongo(student_code: str):
    print("Testing MongoDB (Atlas)...")
    try:
        module = importlib.import_module(f"app.projects.{student_code}.infra.db.mongo")
        database = module.database
        # Send a ping command to verify connection
        res = await database.command("ping")
        if res.get("ok") == 1.0:
            print("✔ MongoDB: Connection Successful!")
        else:
            print(f"❌ MongoDB: Ping failed, response: {res}")
    except Exception as e:
        print(f"❌ MongoDB: Connection Failed! Error: {e}")

async def test_s3(student_code: str):
    print("Testing Object Storage (Supabase S3)...")
    try:
        module = importlib.import_module(f"app.projects.{student_code}.infra.clients.storage")
        storage_client = module.storage_client
        # Generate a test upload presigned URL to verify keys
        url = await storage_client.get_upload_url("test_verify.txt", "text/plain", expires_in=60)
        if url.startswith("http"):
            print("✔ Object Storage: Connection & Key Validation Successful!")
        else:
            print(f"❌ Object Storage: Presigned URL generation failed, response: {url}")
    except Exception as e:
        print(f"❌ Object Storage: Connection Failed! Error: {e}")

async def test_google(student_code: str):
    print("Testing Google Auth configuration & connectivity...")
    try:
        module = importlib.import_module(f"app.projects.{student_code}.infra.settings")
        settings = module.settings
        
        client_id = getattr(settings, "GOOGLE_CLIENT_ID", "")
        client_secret = getattr(settings, "GOOGLE_CLIENT_SECRET", "")
        
        # Check if they are configured
        if not client_id or "your-google-client-id" in client_id:
            print("❌ Google Auth: GOOGLE_CLIENT_ID is not configured (or uses placeholder).")
            return
        if not client_secret or "your-google-client-secret" in client_secret:
            print("❌ Google Auth: GOOGLE_CLIENT_SECRET is not configured (or uses placeholder).")
            return
            
        if not client_id.endswith(".apps.googleusercontent.com"):
            print("⚠ Google Auth: GOOGLE_CLIENT_ID does not end with '.apps.googleusercontent.com'. Check if it is correct.")
            
        # Test outgoing connection to Google OAuth APIs
        import httpx
        async with httpx.AsyncClient() as client:
            res = await client.get("https://oauth2.googleapis.com/tokeninfo")
            # Google will return 400 Bad Request (missing parameter) if reachable, which is expected
            if res.status_code in (200, 400):
                print("✔ Google Auth: Connection to Google APIs Successful & Config looks valid!")
            else:
                print(f"❌ Google Auth: Failed to reach Google API. Status: {res.status_code}")
    except Exception as e:
        print(f"❌ Google Auth: Connection/Configuration validation failed! Error: {e}")

async def main():
    print("=== STARTING CONNECTION VERIFICATION ===")
    
    # Automatically append 'src' folder to sys.path
    repo_root = Path(__file__).resolve().parent
    src_dir = str(repo_root / "src")
    if src_dir not in sys.path:
        sys.path.insert(0, src_dir)
        
    projects = get_available_projects()
    
    if not projects:
        print("No student projects found under src/app/projects/.")
        student_code = input("Please enter the student code to test manually (e.g., c22200002): ").strip()
    else:
        print("Available student projects:")
        for idx, proj in enumerate(projects, 1):
            print(f"[{idx}] {proj}")
        
        choice = input(f"Select project to test (1-{len(projects)}) [Default: 1]: ").strip()
        if not choice:
            student_code = projects[0]
        else:
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(projects):
                    student_code = projects[idx]
                else:
                    print("Invalid choice, using first project.")
                    student_code = projects[0]
            except ValueError:
                # If they typed the project name directly
                student_code = choice
                
    print(f"\nRunning tests for project: {student_code}")
    print("=" * 40)
    await test_postgres(student_code)
    print("-" * 40)
    await test_mongo(student_code)
    print("-" * 40)
    await test_s3(student_code)
    print("-" * 40)
    await test_google(student_code)

if __name__ == "__main__":
    asyncio.run(main())