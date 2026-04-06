from fastapi import FastAPI, Depends, Request, Form
from fastapi.responses import FileResponse, HTMLResponse
from sqlalchemy.orm import Session
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from database import Base, engine
from models import Device, SNMP_Template, Monitoring_Template
from fastapi.responses import RedirectResponse
from snmp import *
import asyncio
from monitor import ping
from database import SessionLocal
from models import Device

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

    if gather_snmp_info:
        # Create SNMP instance
        snmp_device = SNMP(ip=ip_address, version=version)

        # Query hostname via SNMP
        hostname = str(await snmp_device.get_hostname())
        sys_location = await snmp_device.get_sys_location()
        sys_contact = await snmp_device.get_sys_contact()
        status = "Unknown"

    # # If SNMP fails, or we did not query SNMP info, fallback to IP as hostname
    # if not hostname:
    #     hostname = ip_address
    #     status = "Offline"

    # Insert into DB
    new_device = Device(
        hostname=hostname,
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

@app.on_event("startup")
async def start_device_monitor():
    pass
    # asyncio.create_task(monitor_devices())

async def monitor_devices():
    db = SessionLocal()
    while True:
        devices = db.query(Device).all()

        for device in devices:
            device_monitoring_template = db.query(Monitoring_Template).filter(Monitoring_Template.template_id == device.monitoring_template_id).first()
            
            
            online = await ping(device.ip_address, de)  # your async ping function
            if online and device.status != "Online":
                device.status = "Online"
                db.commit()
            elif not online and device.status != "Offline":
                device.status = "Offline"
                db.commit()
            print(f"{device.hostname} is {device.status}")
        await asyncio.sleep(10)  # interval