from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
import uuid
from datetime import datetime, timezone, time
import httpx
import random
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# OneSignal Configuration
ONESIGNAL_APP_ID = os.environ.get('ONESIGNAL_APP_ID')
ONESIGNAL_REST_API_KEY = os.environ.get('ONESIGNAL_REST_API_KEY')
WORDPRESS_SITE_URL = os.environ.get('WORDPRESS_SITE_URL', 'https://ccodelearner.com')

# Scheduler
scheduler = AsyncIOScheduler()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Define Models
class NotificationLog(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    post_title: str
    post_excerpt: str
    post_url: str
    sent_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    status: str  # success, failed
    error_message: Optional[str] = None
    recipient_count: Optional[int] = None

class ScheduleSettings(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: "schedule_config")
    enabled: bool = True
    schedule_time: str  # Format: "HH:MM" (24-hour format)
    timezone: str = "UTC"
    last_updated: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ScheduleSettingsUpdate(BaseModel):
    enabled: Optional[bool] = None
    schedule_time: Optional[str] = None
    timezone: Optional[str] = None

class ManualTriggerResponse(BaseModel):
    success: bool
    message: str
    notification_id: Optional[str] = None

# WordPress API Functions
async def fetch_random_wordpress_post():
    """Fetch a random published post from WordPress site"""
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Fetch all posts
            response = await client.get(
                f"{WORDPRESS_SITE_URL}/wp-json/wp/v2/posts",
                params={
                    "per_page": 100,
                    "status": "publish",
                    "_fields": "id,title,excerpt,link"
                }
            )
            response.raise_for_status()
            posts = response.json()
            
            if not posts:
                logger.warning("No posts found on WordPress site")
                return None
            
            # Select a random post
            random_post = random.choice(posts)
            
            return {
                "title": random_post["title"]["rendered"],
                "excerpt": random_post["excerpt"]["rendered"][:150],  # Limit excerpt length
                "url": random_post["link"]
            }
    except Exception as e:
        logger.error(f"Error fetching WordPress posts: {str(e)}")
        return None

# OneSignal API Functions
async def send_onesignal_notification(post_title: str, post_excerpt: str, post_url: str):
    """Send push notification via OneSignal"""
    try:
        # Clean HTML tags from excerpt
        import re
        clean_excerpt = re.sub('<[^<]+?>', '', post_excerpt).strip()
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            headers = {
                "Content-Type": "application/json; charset=utf-8",
                "Authorization": f"Basic {ONESIGNAL_REST_API_KEY}"
            }
            
            payload = {
                "app_id": ONESIGNAL_APP_ID,
                "included_segments": ["All"],
                "headings": {"en": post_title},
                "contents": {"en": clean_excerpt},
                "url": post_url
            }
            
            response = await client.post(
                "https://onesignal.com/api/v1/notifications",
                headers=headers,
                json=payload
            )
            response.raise_for_status()
            result = response.json()
            
            logger.info(f"OneSignal notification sent: {result}")
            return {
                "success": True,
                "recipient_count": result.get("recipients", 0),
                "error_message": None
            }
    except Exception as e:
        logger.error(f"Error sending OneSignal notification: {str(e)}")
        return {
            "success": False,
            "recipient_count": 0,
            "error_message": str(e)
        }

# Notification Task
async def send_scheduled_notification():
    """Main task to fetch post and send notification"""
    logger.info("Starting scheduled notification task...")
    
    # Fetch random post
    post = await fetch_random_wordpress_post()
    if not post:
        logger.error("Failed to fetch WordPress post")
        return
    
    # Send notification
    result = await send_onesignal_notification(
        post["title"],
        post["excerpt"],
        post["url"]
    )
    
    # Log to database
    notification_log = NotificationLog(
        post_title=post["title"],
        post_excerpt=post["excerpt"],
        post_url=post["url"],
        status="success" if result["success"] else "failed",
        error_message=result["error_message"],
        recipient_count=result["recipient_count"]
    )
    
    doc = notification_log.model_dump()
    doc['sent_at'] = doc['sent_at'].isoformat()
    await db.notification_logs.insert_one(doc)
    
    logger.info(f"Notification task completed. Status: {notification_log.status}")

# API Routes
@api_router.get("/")
async def root():
    return {"message": "OneSignal Push Notification Service"}

@api_router.post("/notifications/trigger", response_model=ManualTriggerResponse)
async def manual_trigger_notification():
    """Manually trigger a notification"""
    try:
        await send_scheduled_notification()
        
        # Get the last notification from DB
        last_notification = await db.notification_logs.find_one(
            {},
            {"_id": 0},
            sort=[("sent_at", -1)]
        )
        
        return ManualTriggerResponse(
            success=True,
            message="Notification sent successfully",
            notification_id=last_notification.get("id") if last_notification else None
        )
    except Exception as e:
        logger.error(f"Error in manual trigger: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/notifications/logs", response_model=List[NotificationLog])
async def get_notification_logs():
    """Get all notification logs"""
    logs = await db.notification_logs.find(
        {},
        {"_id": 0}
    ).sort("sent_at", -1).to_list(100)
    
    # Convert ISO string timestamps back to datetime objects
    for log in logs:
        if isinstance(log['sent_at'], str):
            log['sent_at'] = datetime.fromisoformat(log['sent_at'])
    
    return logs

@api_router.get("/schedule/settings", response_model=ScheduleSettings)
async def get_schedule_settings():
    """Get current schedule settings"""
    settings = await db.schedule_settings.find_one(
        {"id": "schedule_config"},
        {"_id": 0}
    )
    
    if not settings:
        # Create default settings
        default_settings = ScheduleSettings(
            schedule_time="09:00",
            timezone="UTC",
            enabled=True
        )
        doc = default_settings.model_dump()
        doc['last_updated'] = doc['last_updated'].isoformat()
        await db.schedule_settings.insert_one(doc)
        return default_settings
    
    if isinstance(settings['last_updated'], str):
        settings['last_updated'] = datetime.fromisoformat(settings['last_updated'])
    
    return ScheduleSettings(**settings)

@api_router.put("/schedule/settings", response_model=ScheduleSettings)
async def update_schedule_settings(settings_update: ScheduleSettingsUpdate):
    """Update schedule settings and reschedule job"""
    current_settings = await get_schedule_settings()
    
    # Update fields
    if settings_update.enabled is not None:
        current_settings.enabled = settings_update.enabled
    if settings_update.schedule_time is not None:
        current_settings.schedule_time = settings_update.schedule_time
    if settings_update.timezone is not None:
        current_settings.timezone = settings_update.timezone
    
    current_settings.last_updated = datetime.now(timezone.utc)
    
    # Save to database
    doc = current_settings.model_dump()
    doc['last_updated'] = doc['last_updated'].isoformat()
    await db.schedule_settings.update_one(
        {"id": "schedule_config"},
        {"$set": doc},
        upsert=True
    )
    
    # Reschedule the job
    await reschedule_notification_job()
    
    return current_settings

@api_router.get("/schedule/status")
async def get_schedule_status():
    """Get current schedule status"""
    settings = await get_schedule_settings()
    
    job = scheduler.get_job("daily_notification")
    next_run = None
    if job:
        next_run = job.next_run_time.isoformat() if job.next_run_time else None
    
    return {
        "enabled": settings.enabled,
        "schedule_time": settings.schedule_time,
        "timezone": settings.timezone,
        "next_run": next_run,
        "scheduler_running": scheduler.running
    }

async def reschedule_notification_job():
    """Remove and recreate the scheduled job with updated settings"""
    settings = await get_schedule_settings()
    
    # Remove existing job if it exists
    if scheduler.get_job("daily_notification"):
        scheduler.remove_job("daily_notification")
    
    # Add new job if enabled
    if settings.enabled:
        hour, minute = map(int, settings.schedule_time.split(":"))
        trigger = CronTrigger(hour=hour, minute=minute, timezone=settings.timezone)
        
        scheduler.add_job(
            send_scheduled_notification,
            trigger=trigger,
            id="daily_notification",
            name="Daily WordPress Post Notification",
            replace_existing=True
        )
        logger.info(f"Scheduled job set for {settings.schedule_time} {settings.timezone}")
    else:
        logger.info("Scheduled job disabled")

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    """Initialize scheduler on startup"""
    scheduler.start()
    await reschedule_notification_job()
    logger.info("Application started and scheduler initialized")

@app.on_event("shutdown")
async def shutdown_db_client():
    """Cleanup on shutdown"""
    scheduler.shutdown()
    client.close()
    logger.info("Application shutdown complete")