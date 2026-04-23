from fastapi import FastAPI, Depends, Request, Form, HTTPException
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from database import Base, engine, SessionLocal
from models import Device, SNMP_Template, Monitoring_Template
from snmp import *
import asyncio
from monitor import ping

app = FastAPI()

Base.metadata.create_all(bind=engine)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/", response_class=HTMLResponse)
def home_page(request: Request, db: Session = Depends(get_db)):
    devices = db.query(Device).all()
    return templates.TemplateResponse("index.html", {"request": request, "devices": devices})



@app.get("/manage_devices", response_class=HTMLResponse)
def manage_device_page(request: Request, db: Session = Depends(get_db)):
    snmp_templates = db.query(SNMP_Template).all()
    devices = db.query(Device).all()
    monitoring_templates = db.query(Monitoring_Template).all()
    return templates.TemplateResponse("manage_devices.html",
                                    {"request": request,
                                    "snmp_templates": snmp_templates,
                                    "monitoring_templates": monitoring_templates, 
                                    "devices": devices})


@app.get("/monitoring_templates", response_class=HTMLResponse)
def add_template_page(request: Request, db: Session = Depends(get_db)):
    monitoring_templates = db.query(Monitoring_Template).all()
    return templates.TemplateResponse("monitoring_templates.html", {"request": request, "monitoring_templates": monitoring_templates})


@app.post("/add_monitoring_template", response_class=HTMLResponse)
async def add_monitoring_template(
    request: Request,
    db: Session = Depends(get_db),
    template_name: str = Form(...),
    description: str = Form(...),
    monitoring_interval: int | None = Form(None),
    ping_count: int | None = Form(None),
    timeout: int | None = Form(None),
    retry_attempts: int | None = Form(None),
    retry_ping_count: int | None = Form(None),
    retry_timeout: int | None = Form(None),
    retry_interval: int | None = Form(None),
    retry_before_alert: int | None = Form(None)                            
    ):
    new_template = Monitoring_Template(
       template_name = template_name,
       description = description,
       monitoring_interval = monitoring_interval,
       ping_count = ping_count,
       timeout = timeout,
       retry_attempts = retry_attempts,
       retry_ping_count = retry_ping_count,
       retry_timeout = retry_timeout,
       retry_interval = retry_interval,
       retry_before_alert = retry_before_alert
    )

    db.add(new_template)
    db.commit()
    db.refresh(new_template)

    return RedirectResponse(url="/", status_code=303)


@app.get("/snmp_templates", response_class=HTMLResponse)
def add_snmp_template_page(request: Request, db: Session = Depends(get_db)):
    snmp_templates = db.query(SNMP_Template).all()
    return templates.TemplateResponse("snmp_templates.html", {"request": request, "snmp_templates": snmp_templates})


@app.post("/add_device", response_class=HTMLResponse)
async def add_device(
    request: Request,
    ip_address: str = Form(...),
    hostname: str = Form(...),
    version: str = Form("v2c"),
    snmp_template_id: int = Form(...),
    monitoring_template_id: int = Form(...),
    gather_snmp_info: bool = Form(False),

    db: Session = Depends(get_db)
):
    template = db.query(SNMP_Template).filter(SNMP_Template.template_id == snmp_template_id)

    sys_location = None
    sys_contact = None
    status = "Unknown"
    snmp_hostname = hostname

    if gather_snmp_info:
        # Create SNMP instance
        snmp_device = SNMP(ip=ip_address, version=version)

        # Query hostname via SNMP
        snmp_hostname = str(await snmp_device.get_hostname())
        sys_location = await snmp_device.get_sys_location()
        sys_contact = await snmp_device.get_sys_contact()
        status = "Unknown"
    
        if not snmp_hostname:
            snmp_hostname = hostname

    # Insert into DB
    new_device = Device(
        hostname=snmp_hostname,
        ip_address=ip_address,
        location=sys_location,
        contact=sys_contact,
        status=status,
        snmp_template_id=snmp_template_id,
        monitoring_template_id=monitoring_template_id
    )

    db.add(new_device)
    db.commit()
    db.refresh(new_device)

    # Optionally render page or redirect
    return RedirectResponse(url="/", status_code=303)

@app.post("/remove_device")
def remove_device(
    device_id: int = Form(...),
    db: Session = Depends(get_db)
):
    device = db.query(Device).filter(Device.device_id == device_id).first()
    if device:
        db.delete(device)
        db.commit()

    return RedirectResponse(url="/", status_code=303)

@app.post("/modify_device")
def modify_device(
    device_id: int = Form(...),
    hostname: str = Form(...),
    ip_address: str = Form(...),
    mac_address: str = Form(...),
    device_type: str = Form(...),
    manufacturer: str = Form(...),
    model: str = Form(...),
    serial_number: str = Form(...),
    location: str = Form(...),
    contact: str = Form(...),
    db: Session = Depends(get_db)
):
    #print("Modifying device:", device_id, hostname, ip_address)
    device = db.query(Device).filter(Device.device_id == device_id).first()
    if device:
        device.hostname = hostname
        device.ip_address = ip_address
        device.device_type = device_type
        device.manufacturer = manufacturer
        device.model = model
        device.serial_number = serial_number
        device.location = location
        device.mac_address = mac_address
        device.contact = contact
        db.commit()
    else:
        print("Device not found")

    return RedirectResponse(url="/manage_devices", status_code=303)

@app.post("/remove_snmp_template")
def remove_template(
    template_id: int = Form(...),
    db: Session = Depends(get_db)
):
    template = db.query(SNMP_Template).filter(SNMP_Template.template_id == template_id).first()
    if template:
        db.delete(template)
        db.commit()

    return RedirectResponse(url="/", status_code=303)

@app.post("/add_snmp_template")
def add_snmp_template(
    request: Request,
    template_name: str = Form(...),
    description: str = Form(""),
    version: str = Form(...),
    community: str | None = Form(None),
    username: str | None = Form(None),
    auth_pass: str | None = Form(None),
    priv_pass: str | None = Form(None),
    auth_proto: str | None = Form("none"),
    priv_proto: str | None = Form("none"),
    db: Session = Depends(get_db)
):
    new_template = SNMP_Template(
        template_name=template_name,
        description=description,
        version=version,
        community=community,
        username=username,
        auth_pass=auth_pass,
        priv_pass=priv_pass,
        auth_proto=auth_proto,
        priv_proto=priv_proto
    )

    db.add(new_template)
    db.commit()
    db.refresh(new_template)

    snmp_templates = db.query(SNMP_Template).all()

    return templates.TemplateResponse(
        "snmp_templates.html",
        {"request": request, "snmp_templates": snmp_templates}
    )

@app.get("/device_status")
def get_device_status(db: Session = Depends(get_db)):
    devices = db.query(Device).all()
    return [
        {
            "hostname": d.hostname,
            "ip_address": d.ip_address,
            "status": d.status
        } for d in devices
    ]

@app.get("/refresh/{device_id}")
async def refresh_device(device_id: int, db: Session = Depends(get_db)):
    # 1. Fetch device and template
    device = db.query(Device).filter(Device.device_id == device_id).first()
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")

    snmp_template = db.query(SNMP_Template).filter(
        SNMP_Template.template_id == device.snmp_template_id
    ).first()

    if not snmp_template:
        raise HTTPException(status_code=400, detail="Device has no associated SNMP template")

    try:
        # 2. Initialize your SNMP manager and pull everything at once
        # Assuming your SNMP class takes (ip, version, community)
        snmp_device = None
        
        if not snmp_template.community:
            raise HTTPException(status_code=400, detail="Device has no associated SNMP community")
        
        snmp_device = SNMP(
            device.ip_address, 
            version=snmp_template.version,
            community=snmp_template.community
        )

        info = await snmp_device.get_all_system_info()
        if not info:
            raise Exception("No SNMP data returned")

        # 3. Update the database if we got a valid dictionary back
        device.hostname = str(info.get("hostname"))
        device.location = str(info.get("location"))
        device.contact = str(info.get("contact"))
        device.manufacturer = str(info.get("manufacturer"))
        
        # # Map description to model, truncating to prevent DB column overflow
        # if info.get("description"):
        #     device.model = info["description"][:100]
        
        # Mark as online since the gather was successful
        device.status = "Online"
        
        db.commit()
        return {"success": True, "message": f"Refreshed {device.hostname}", "data": info}

    except Exception as e:
        # Network error or SNMP timeout
        device.status = "Offline"
        db.commit()
        return {"success": False, "message": f"SNMP Error: {str(e)}"}

@app.on_event("startup")
async def start_device_monitor():
    asyncio.create_task(monitor_devices())

# async def monitor_devices():
#     db = SessionLocal()
#     while True:
#         devices = db.query(Device).all()
#         print(f"Monitoring {len(devices)} devices...")

#         for device in devices:
#             monitoring_template = db.query(Monitoring_Template).filter(Monitoring_Template.template_id == device.monitoring_template_id).first()
            
#             if monitoring_template:
#                 online = await ping(device.ip_address, monitoring_template.ping_count, monitoring_template.timeout)  # your async ping function
#                 num_failed_attempts = 0

#                 if online:
#                     print(f"{device.hostname} is {device.status}")
#                     if device.status != "Online":
#                         device.status = "Online"
#                         db.commit()

#                 else:
#                     print(f"{device.hostname} is {device.status}")
#                     for attempt in range(monitoring_template.retry_attempts):
#                         num_failed_attempts += 1
#                         print(f"{device.hostname} has failed {num_failed_attempts} ping attempts.")
                        
#                         print(f"{device.hostname} is {device.status}")
#                         if num_failed_attempts == monitoring_template.retry_before_alert:
#                             print(f"{device.hostname} has exceeded retry attempts. Marking as Offline.")
#                             device.status = "Offline"
#                             db.commit()
                        
#                         print(f"Waiting for {monitoring_template.retry_interval} seconds before retrying...")
#                         await asyncio.sleep(monitoring_template.retry_interval)  # retry interval
                        
#                         recovered = await ping(device.ip_address, monitoring_template.retry_ping_count, monitoring_template.retry_timeout)
#                         if recovered:
#                             print(f"{device.hostname} has recovered after {num_failed_attempts} failed attempts.")
#                             break

#                     if device.status != "Offline":
#                         device.status = "Offline"
#                         db.commit()

#                 print(f"Waiting for {monitoring_template.monitoring_interval} seconds before next check...")      
#                 await asyncio.sleep(monitoring_template.monitoring_interval)  # interval

#             else:
#                 device.status = "Unknown"
#                 online = False
#                 db.commit()

import asyncio

async def monitor_single_device(device_id, db_factory):
    """
    Independent worker for each device. 
    Uses the device's specific interval and retry variables.
    """
    while True:
        db = db_factory()
        try:
            # 1. Fetch current device and template state
            device = db.query(Device).filter(Device.device_id == device_id).first()
            if not device:
                break # Device was deleted from DB

            mt = db.query(Monitoring_Template).filter(
                Monitoring_Template.template_id == device.monitoring_template_id
            ).first()

            if not mt:
                print(f"Device {device.hostname} has no monitoring template. Retrying in 30s...")
                await asyncio.sleep(30) # Wait for a template to be assigned
                continue

            # 2. Perform the Primary Ping
            online = await ping(device.ip_address, mt.ping_count, mt.timeout)
            
            if online:
                print(f"{device.hostname} is Online")
                if device.status != "Online":
                    device.status = "Online"
                    db.commit()
                # Use YOUR variable: monitoring_interval
                print(f"Waiting for {mt.monitoring_interval}s before next check...")
                await asyncio.sleep(mt.monitoring_interval)
            
            else:
                # 3. Handle Failure and Retries
                print(f"{device.hostname} primary ping failed. Entering retry cycle...")
                num_failed_attempts = 0
                recovered = False

                for attempt in range(mt.retry_attempts):
                    num_failed_attempts += 1
                    print(f"{device.hostname} attempt {num_failed_attempts} failed.")

                    # Use YOUR variable: retry_before_alert
                    if num_failed_attempts == mt.retry_before_alert:
                        print(f"Alert: Marking {device.hostname} as Offline.")
                        device.status = "Offline"
                        db.commit()

                    # Use YOUR variable: retry_interval
                    print(f"Waiting {mt.retry_interval}s before retry...")
                    await asyncio.sleep(mt.retry_interval)

                    # Use YOUR variables: retry_ping_count and retry_timeout
                    recovered = await ping(device.ip_address, mt.retry_ping_count, mt.retry_timeout)
                    
                    if recovered:
                        print(f"{device.hostname} recovered after {num_failed_attempts} attempts.")
                        device.status = "Online"
                        db.commit()
                        break

                # If we finish the loop without recovery, ensure status is Offline
                if not recovered:
                    if device.status != "Offline":
                        device.status = "Offline"
                        db.commit()
                
                # After a failure cycle, wait the standard interval before starting over
                await asyncio.sleep(mt.monitoring_interval)

        except Exception as e:
            print(f"Error monitoring {device_id}: {e}")
            await asyncio.sleep(10) # Prevent rapid-fire errors
        finally:
            db.close()

async def monitor_devices():
    """Main Orchestrator: Launches a concurrent task for every device."""
    active_tasks = {}

    while True:
        db = SessionLocal()
        devices = db.query(Device).all()
        db.close()

        for device in devices:
            if device.device_id not in active_tasks:
                print(f"Starting concurrent monitor for: {device.hostname}")
                # Create a task that runs independently
                task = asyncio.create_task(monitor_single_device(device.device_id, SessionLocal))
                active_tasks[device.device_id] = task

        # Check for new devices every 30 seconds
        await asyncio.sleep(30)

