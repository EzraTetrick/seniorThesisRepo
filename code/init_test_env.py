import os
import subprocess
from sqlalchemy.orm import Session
from database import SessionLocal, engine, Base
from models import Device, SNMP_Template, Monitoring_Template

def run_cmd(cmd):
    """Helper to run shell commands as root."""
    subprocess.run(f"sudo {cmd}", shell=True, check=True)

import time

def setup_network_node(name, ip, desc, d_type):
    """Creates the Linux namespace and starts snmpd with shortened names."""
    conf_path = f"/tmp/snmpd-{name}.conf"
    location = "Datacenter"
    contact = "Ezra T"
    
    # 1. Type Mapping & OID Logic
    services = {"switch": 2, "router": 4, "server": 72}.get(d_type.lower(), 72)
    vendor_oid = {
        "switch": ".1.3.6.1.4.1.9", 
        "router": ".1.3.6.1.4.1.9", 
        "server": ".1.3.6.1.4.1.8072"
    }.get(d_type.lower(), ".1.3.6.1.4.1.8072")

    # 2. Short Naming (using IP suffix to ensure uniqueness)
    type_map = {"router": "r", "switch": "sw", "server": "srv"}
    short_type = type_map.get(d_type.lower(), "dev")
    suffix = ip.split('.')[-1]
    
    vh = f"vh{short_type}{suffix}"  # vhsw11
    vn = f"vn{short_type}{suffix}"  # vnsw11

    # 3. Network Setup
    run_cmd(f"ip netns add {name} || true")
    run_cmd(f"ip link add {vh} type veth peer name {vn} || true")
    run_cmd(f"ip link set {vh} master br-test || true")
    run_cmd(f"ip link set {vh} up || true")
    
    try:
        run_cmd(f"ip link set {vn} netns {name}")
    except:
        pass # Already in namespace

    # Critical: Bring up the internal interface and IP
    run_cmd(f"ip netns exec {name} ip link set lo up || true")
    run_cmd(f"ip netns exec {name} ip addr add {ip}/24 dev {vn} || true")
    run_cmd(f"ip netns exec {name} ip link set {vn} up || true")

    # 4. Write SNMP Config
    with open(conf_path, "w") as f:
        f.write(f"agentAddress udp:{ip}:161\n")
        f.write(f"rocommunity public 192.168.0.0/24\n")
        f.write(f"sysDescr {desc}\n")
        f.write(f"sysLocation {location}\n")
        f.write(f"sysContact {contact}\n")
        f.write(f"sysName {name}\n")
        f.write(f"sysServices {services}\n")
        f.write(f"sysObjectID {vendor_oid}\n")
            
    # 5. Start SNMPD
    # Kill any existing snmpd using this PID file to free the port
    run_cmd(f"[ -f /tmp/snmpd-{name}.pid ] && kill $(cat /tmp/snmpd-{name}.pid) 2>/dev/null || true")
    
    # Small pause to let the kernel release the port and settle the interface
    time.sleep(0.5) 

    # Launch snmpd
    run_cmd(f"ip netns exec {name} snmpd -C -c {conf_path} -p /tmp/snmpd-{name}.pid")
    print(f"-> {name} is live at {ip}")

def init_db():
    # ... (Database setup code) ...

    # 1. Ensure the virtual bridge (switch) exists
    print("Initializing virtual bridge...")
    run_cmd("ip link add name br-test type bridge || true")
    run_cmd("ip addr add 192.168.0.1/24 dev br-test || true")
    run_cmd("ip link set br-test up")
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    # 1. Check for existing SNMP Template
    snmp_tmp = db.query(SNMP_Template).filter_by(template_name="Standard v2c").first()
    if not snmp_tmp:
        snmp_tmp = SNMP_Template(
            template_name="Standard v2c",
            version="v2c",
            community="public"
        )
        db.add(snmp_tmp)
        db.commit()
        db.refresh(snmp_tmp)

    # 2. Check for existing Monitoring Template
    mon_tmp = db.query(Monitoring_Template).filter_by(template_name="Default Monitor").first()
    if not mon_tmp:
        mon_tmp = Monitoring_Template(
            template_name="Default Monitor",
            description="Standard monitoring for test nodes",
            monitoring_interval=60,
            ping_count=4,
            timeout=2,
            retry_attempts=3,
            retry_ping_count=2,
            retry_timeout=5,
            retry_interval=30,
            retry_before_alert=2
        )
        db.add(mon_tmp)
        db.commit()
        db.refresh(mon_tmp)

    # 3. Create Devices (only if they don't exist)
    device_types = [("switch", "SW"), ("router", "RT"), ("server", "SRV")]
    
    count = 1
    for d_type, prefix in device_types:
        for i in range(1, 3):
            hostname = f"{prefix}-{i:02d}"
            ip = f"192.168.0.{10 + count}"
            
            # Check if device already in DB
            exists = db.query(Device).filter_by(hostname=hostname).first()
            if not exists:
                new_device = Device(
                    hostname=hostname,
                    ip_address=ip,
                    device_type=d_type,
                    status="Online",
                    snmp_template_id=snmp_tmp.template_id,
                    monitoring_template_id=mon_tmp.template_id
                )
                db.add(new_device)
                print(f"Adding {hostname} to DB and Network...")
                setup_network_node(hostname, ip, f"Virtual {d_type.capitalize()}", d_type)
            
            count += 1

    db.commit()
    db.close()

if __name__ == "__main__":
    init_db()