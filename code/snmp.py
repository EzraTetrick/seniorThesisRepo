import os
from pysnmp.hlapi.v3arch.asyncio import *
from pysnmp.hlapi.v3arch.asyncio import SnmpEngine, UsmUserData, UdpTransportTarget, ContextData, ObjectType, ObjectIdentity, set_cmd, walk_cmd, Integer

ENABLE = 1
DISABLE = 2
INT_DESC_BASE_OID = "1.3.6.1.2.1.2.2.1.2"
ADMIN_STATUS_BASE_OID = "1.3.6.1.2.1.2.2.1.7"
POE_STATUS_BASE_OID =   "1.3.6.1.2.1.105.1.1.1.3.5"
CDP_INT_DESC_OID = "1.3.6.1.4.1.9.9.23.1.2.1.1.8"
MAC_ENTRIES_OID = "1.3.6.1.2.1.17.4.3.1.2"
HOSTNAME = "1.3.6.1.2.1.1.5.0"

class SNMP:
    def __init__(self, ip):
        self.ip = ip
        self.snmpEngine = SnmpEngine()
        self.auth = UsmUserData(
            userName=os.environ["USER"],
            authKey=os.environ["AUTH_KEY"],
            authProtocol=usmHMACSHAAuthProtocol,
            privKey=os.environ["PRIV_KEY"],
            privProtocol=usmAesCfb128Protocol
        )

    async def walk(self, oid_base):
        #print(f"user: {self.auth.userName}, priv: {self.auth.privacy_key}, auth: {self.auth.authentication_key}")
        target = await UdpTransportTarget.create((self.ip, 161))
        results = []

        async for (errorIndication, errorStatus, errorIndex, varBinds) in walk_cmd(
            self.snmpEngine,
            self.auth,
            target,
            ContextData(),
            ObjectType(ObjectIdentity(oid_base)),
            lexicographicMode = False,
        ):
            if errorIndication:
                print("Error:", errorIndication)
                break
            elif errorStatus:
                print(
                    "{} at {}".format(
                        errorStatus.prettyPrint(),
                        errorIndex and varBinds[int(errorIndex) - 1][0] or "?",
                    )
                )
                break
            else:
                for varBind in varBinds:
                    oid = str(varBind[0])
                    value = varBind[1].prettyPrint()
                    #print(f"{oid}, {ifDescr}")
                    results.append((oid, value))
                    #print(f"{oid}, {varBind[1]}")

        return results
    

    async def get(self, oid):
        target = await UdpTransportTarget.create((self.ip, 161))
        results = []

        iterator = get_cmd(
            self.snmpEngine,
            self.auth,
            target,
            ContextData(),
            ObjectType(ObjectIdentity(oid)),
        )
        errorIndication, errorStatus, errorIndex, varBinds = await iterator

        if errorIndication:
            print(errorIndication)

        elif errorStatus:
            print(
                "{} at {}".format(
                    errorStatus.prettyPrint(),
                    errorIndex and varBinds[int(errorIndex) - 1][0] or "?",
                )
            )
        else:
            for varBind in varBinds:
                results.append(" = ".join([x.prettyPrint() for x in varBind]))

        return results
    
    async def set_interface_status(self, interface_oid, base_oid, status):
        index = int(interface_oid.split(".")[-1])
        target = await UdpTransportTarget.create((self.ip, 161))

        oid = f"{base_oid}.{index}"

        print(f"setting status of {oid} to {status}...")

        iterator = set_cmd(
            self.snmpEngine,
            self.auth,
            target,
            ContextData(),
            ObjectType(ObjectIdentity(oid), Integer(status))
        )

        errorIndication, errorStatus, errorIndex, varBinds = await iterator

        if errorIndication:
            print(f"Error: {errorIndication}")
        elif errorStatus:
            print(f"{errorStatus.prettyPrint()} at {varBinds[int(errorIndex)-1][0]}")
        else:
            print(f"Interface {index} disabled successfully.")

    async def walk_cdp_info(self):
        results = await self.walk(oid_base=CDP_INT_DESC_OID)

        # clean_cdp_info = []

        # for cdp_info in results:
        #     desc_index = cdp_info[0].split(".")[-1]
        #     if desc_index == '1':
        #         interface_index = cdp_info[0].split(".")[-2]
        #         cdp_desc = self.decode_hex_string(cdp_info[1])
        #         clean_cdp_info.append((interface_index, cdp_desc))

        return results

    async def walk_mac_entries(self):
        results = await self.walk(oid_base=MAC_ENTRIES_OID)
        return results
    
    async def walk_ifdesc(self):
        results = await self.walk(oid_base=INT_DESC_BASE_OID)
        return results
    
    async def get_hostname(self):
        results = await self.get(oid=HOSTNAME)
        if results:
            return results[0]
        return None

    def decode_hex_string(self, hex_string):
        if hex_string.startswith("0x"):
            hex_string = hex_string[2:]
        try:
            # Convert hex to bytes and then decode to a string
            return bytes.fromhex(hex_string).decode('ascii', errors='ignore')
        except ValueError:
            # If conversion fails, return the original string
            return hex_string

    def close(self):
        self.snmpEngine.close_dispatcher()