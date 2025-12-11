# Senior Thesis Repo: Ezra Tetrick
<!--This repository is provided to help you build your senior thesis project. You will edit it to store your specification documents, code, and weekly checkins.

First, fork this repo (this makes a copy of it associated with your account) and then clone it to your machine (this makes a copy of your fork on your personal machine). You can then use an editor and a GitHub client to manage the repository.

### Markdown
This file is called README.md. It is a [Markdown file](https://en.wikipedia.org/wiki/Markdown). Markdown is a simple way to format documents. When a Markdown-ready viewer displays the contents of a file, it formats it to look like HTML. However, Markdown is significantly easier to write than HTML. VSCode supports displaying Markdown in a preview window. GitHub uses Markdown extensively including in every repo's description file, ```README.md```.

All Markdown files end with the extension ```.md```. There is a Markdown tutorial [here](https://www.markdowntutorial.com/) and a Markdown cheatsheet [here](https://www.markdownguide.org/cheat-sheet/).

#### Images
If you would like to add images to a Markdown file, place them in the ```docs/images/``` directory in this repo and reference them using markdown like this:

```
![alt text](relative/path/to/image)
```

Here is how to add the Carthage logo to a Markdown file (you can see the image in the repo right now):

```
![Carthage Firebird Logo](docs/images/firebirdLogo.jpg)
```
![Carthage Firebird Logo](docs/images/firebirdLogo.jpg)

This ensures that images are correctly linked and displayed when viewing the documentation on GitHub or any Markdown-supported platform.

## Code
The ```code``` directory is used to store your code. You can put it all in one directory or you can create subdirectories.

I have added a ```main.cpp``` file to get you started. Feel free to remove it.

If you have any questions feel free to ask me! I'll answer professor questions, customer questions, and give advice if asked.

# Sample Spec

Below is an example of a project specification.
-->

# Software Requirements Specification for Vendor Neutral Network Monitoring System (VeNNM)

## Introduction

### Purpose
The purpose of this document is to outline the functional and non-functional requirements of the Vendor Neutral Network Monitoring System (VeNNM). The system is designed to provide one place to monitor and manage network devices from any vendor. This specification serves as a contract between the system stakeholders and the developers to ensure that the system meets the needs of its users while adhering to policies and technical constraints.

The key goals of the new system are:
- To display a dashboard for managed devices
- To create an inventory of devices from any vendor.
- To gather information from devices.
- To provide monitoring services for devices using standardized protocols such as SNMP and ICMP.
- To provide alerting services for monitored devices.

### Scope
This system is intended to provide a vendor-neutral, web-based application to manage and monitor network devices. The system will handle:
- Creating an inventory of network devices.
- Monitoring network devices.
- Gathering information from managed devices.
- Configuring alerting for managed devices.
- Displaying a dashboard of monitored devices.

### Definitions, Acronyms, and Abbreviations
- **SNMP**: Simple Network Management Protocol — an application layer protocol used to monitor and manage network devices.
- **ICMP**: Internet Control Message Protocol — used to send error messages and operational information about network connectivity, acting as a diagnostic and control mechanism for network devices.
- **ping**: A common ICMP utility used to check if a device is online.
- **Postgres**: Relational database system used to store device inventory, monitoring data, and alerts.
- **FastAPI**: Python-based web framework used to build the application frontend and API.

## Overview
The Vendor Neutral Network Monitoring System (VeNNM) is a web-based platform designed to provide centralized monitoring and management of devices from any vendor. It serves as the primary interface for administrators and operators to oversee device health, performance, and alerts.

### System Features:
1. **Secure Login**: Ensures that only authorized users have access to the system, with user authentication and role-based permissions.
2. **Device Inventory**: Allows administrators to add, edit, or remove devices from the system, storing vendor-neutral information such as IP, hostname, SNMP credentials, and tags.
3. **Device Monitoring**: Provides polling and active checks of device availability and health using ICMP (ping) and SNMP.
4. **Data Collection**: Gathers performance metrics such as uptime, interface statistics, and CPU/memory utilization from devices where available.
5. **Alerting**: Supports rule-based alerting, with notifications for device downtime or threshold breaches (e.g., interface utilization above a set level).
6. **Dashboards**: Displays device health summaries, alert status, and performance graphs.
7. **Extensibility**: Supports future integration of additional monitoring protocols or vendor-specific collectors.

The system is designed with scalability in mind, allowing it to handle many devices and polling tasks. It will store device and monitoring data in PostgreSQL and use FastAPI to provide a secure, responsive interface.

The following sections detail the specific use cases that the system will support, describing how administrators and operators will interact with VeNNM during typical operations.

## Use Cases

### Use Case 1.1: Secure Login
- **Users**: Administrator or Operator  
- **Overview**: Users use credentials to verify their identity.

**Typical Course of Events**:
1. Page prompts for username and password.
2. User enters their credentials and clicks "login."
3. System verifies that the username and password are correct.
4. User is granted access based on their role.

---

### Use Case 1.2: Add a Device to Inventory
- **Actors**: Administrator  
- **Overview**: Administrator adds a network device to the system.

**Typical Course of Events**:
1. User navigates to the inventory menu.
2. User selects "Add Device."
3. System displays "Add Device" form.
4. User enters device details (IP, hostname, SNMP settings, tags).
5. System verifies entry and saves the device to the inventory.

**Alternative Courses**:

---

### Use Case 1.3: Monitor Device Availability
- **Actors**: Operator and Administrator
- **Overview**: Operator monitors if devices are online.

**Typical Course of Events**:
2. The system periodically pings devices in the inventory.
3. Device availability is displayed in the dashboard.
4. All users can view detailed device status.

**Alternative Courses**:

---

### Use Case 1.4: View Device Metrics
- **Actors**: Operator and Administrator
- **Overview**: User views collected metrics from a device.

**Typical Course of Events**:
1. User selects a device from the inventory.
2. System displays available metrics (uptime, interfaces, CPU/memory).
3. Operator views charts of historical data.

**Alternative Courses**:

---

### Use Case 1.5: Configure Alerts
- **Actors**: Administrator  
- **Overview**: Administrator creates alert rules for devices.

**Typical Course of Events**:
1. Administrator navigates to the Alerting menu.
2. Administrator selects "Create Alert Rule."
3. System displays alert configuration form.
4. Administrator enters rule details (e.g., device offline, threshold > 80%).
5. System validates and saves the alert rule.
6. Alerts are triggered automatically when conditions are met.

**Alternative Courses**:

---

### Use Case 1.6: Respond to Alerts
- **Actors**: Operators and Administrators 
- **Overview**: Users acknowledge and resolve alerts.

**Typical Course of Events**:
1. User navigates to the Alerts menu
2. User views a list of active alerts.
3. User selects an alert to acknowledge.
4. System marks the alert as acknowledged and records the operator’s ID.
5. Alert is marked resolved when the condition clears.

---

**Alternative Courses**:
