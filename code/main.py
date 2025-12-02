# main.py
from fastapi import FastAPI, Depends
from fastapi.responses import FileResponse, HTMLResponse
from sqlalchemy.orm import Session
from fastapi.staticfiles import StaticFiles

from database import SessionLocal
from models import Device

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")


# Dependency: DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()



@app.get("/", response_class=HTMLResponse)
def home_page():
    return FileResponse("static/index.html")

@app.post("/devices/add")
def add_device(
    hostname: str,
    ip_address: str,
    device_type: str = "",
    manufacturer: str = "",
    model: str = "",
    serial_number: str = "",
    location: str = "",
    status: str = "",
    db: Session = Depends(get_db)
):
    device = Device(
        hostname=hostname,
        ip_address=ip_address,
        device_type=device_type,
        manufacturer=manufacturer,
        model=model,
        serial_number=serial_number,
        location=location,
        status=status,
    )

    db.add(device)
    db.commit()
    db.refresh(device)

    return {"message": "Device added", "device_id": device.device_id}


@app.get("/devices")
def get_devices(db: Session = Depends(get_db)):
    devices = db.query(Device).all()
    return devices

# db = SessionLocal()

# device1 = Device(
#     hostname="Switch02",
#     ip_address="192.168.1.11",
#     device_type="Switch",
#     manufacturer="HPE",
#     model="2530-24G",
#     serial_number="654321",
#     location="Office 2",
#     status="active"
# )

# device2 = Device(
#     hostname="Switch02",
#     ip_address="192.168.1.11",
#     device_type="Switch",
#     manufacturer="HPE",
#     model="2530-24G",
#     serial_number="654321",
#     location="Office 2",
#     status="active"
# )

# device3 = Device(
#     hostname="Switch02",
#     ip_address="192.168.1.11",
#     device_type="Switch",
#     manufacturer="HPE",
#     model="2530-24G",
#     serial_number="654321",
#     location="Office 2",
#     status="active"
# )

# db.add(device1)
# db.add(device2)
# db.add(device3)
# db.commit()
# db.refresh(device1)
# db.refresh(device2)
# db.refresh(device3)
# #print(f"Inserted device with ID: {device.device_id}")

# db.close()
