import os
from pysnmp.hlapi import *
from pysnmp.hlapi.v3arch.asyncio import (
    SnmpEngine,
    UsmUserData,
    CommunityData,
    UdpTransportTarget,
    ContextData,
    ObjectType,
    ObjectIdentity,
    set_cmd,
    walk_cmd,
    get_cmd,
    Integer,
)

from pysnmp.hlapi.v3arch.asyncio.auth import (
    USM_AUTH_NONE, 
    USM_PRIV_NONE,
    USM_AUTH_HMAC96_SHA,
    USM_AUTH_HMAC96_MD5,
    USM_AUTH_HMAC192_SHA256,
    USM_PRIV_CBC56_DES,
    USM_PRIV_CFB128_AES,
    USM_PRIV_CFB192_AES,
    USM_PRIV_CFB256_AES
    )

ENABLE = 1
DISABLE = 2

INT_DESC_BASE_OID     = "1.3.6.1.2.1.2.2.1.2"
ADMIN_STATUS_BASE_OID = "1.3.6.1.2.1.2.2.1.7"
POE_STATUS_BASE_OID   = "1.3.6.1.2.1.105.1.1.1.3.5"
CDP_INT_DESC_OID      = "1.3.6.1.4.1.9.9.23.1.2.1.1.8"
MAC_ENTRIES_OID       = "1.3.6.1.2.1.17.4.3.1.2"
HOSTNAME              = "1.3.6.1.2.1.1.5.0"
SYS_LOCATION          = "1.3.6.1.2.1.1.6.0"
SYS_CONTACT           = "1.3.6.1.2.1.1.4.0"


class SNMP:
    def __init__(self, ip, version="v3", community="public", 
                 username=None, auth_pass=None, priv_pass=None, 
                 auth_proto="none", priv_proto="none"):
        self.ip = ip
        self.version = version
        self.community=community
        self.snmpEngine = SnmpEngine()

        if version == "v3":
            auth_protocols = {
                "none": USM_AUTH_NONE,
                "md5": USM_AUTH_HMAC96_MD5,
                "sha": USM_AUTH_HMAC96_SHA,
                "sha256": USM_AUTH_HMAC192_SHA256
            }

            priv_protocols = {
                "none": USM_PRIV_NONE,
                "des": USM_PRIV_CBC56_DES,
                "aes128": USM_PRIV_CFB128_AES,
                "aes192": USM_PRIV_CFB192_AES,
                "aes256": USM_PRIV_CFB256_AES
            }

            self.auth_or_community = UsmUserData(
                userName=username,
                authKey=auth_pass,
                authProtocol=auth_protocols.get(auth_proto),
                privKey=priv_pass,
                privProtocol=priv_protocols.get(priv_proto)
            )
        elif version == "v2c":
            self.auth_or_community = CommunityData(community, mpModel=1)  # v2c
        else:
            raise ValueError("version must be 'v2c' or 'v3'")

    async def walk(self, oid_base):
        target = await UdpTransportTarget.create((self.ip, 161))
        results = []

        async for (
            errorIndication,
            errorStatus,
            errorIndex,
            varBinds,
        ) in walk_cmd(
            self.snmpEngine,
            self.auth_or_community,  # v2c or v3
            target,
            ContextData(),
            ObjectType(ObjectIdentity(oid_base)),
            lexicographicMode=False,
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
                for oid, value in varBinds:
                    results.append((str(oid), value.prettyPrint()))

        return results

    async def get(self, oid):
        target = await UdpTransportTarget.create((self.ip, 161))
        iterator = get_cmd(
            self.snmpEngine,
            self.auth_or_community,
            target,
            ContextData(),
            ObjectType(ObjectIdentity(oid)),
        )

        errorIndication, errorStatus, errorIndex, varBinds = await iterator

        if errorIndication:
            print(errorIndication)
            return None

        if errorStatus:
            print(
                "{} at {}".format(
                    errorStatus.prettyPrint(),
                    errorIndex and varBinds[int(errorIndex) - 1][0] or "?",
                )
            )
            return None

        return [varBind[1] for varBind in varBinds]

    async def set_interface_status(self, interface_oid, base_oid, status):
        index = int(interface_oid.split(".")[-1])
        target = await UdpTransportTarget.create((self.ip, 161))
        oid = f"{base_oid}.{index}"

        iterator = set_cmd(
            self.snmpEngine,
            self.auth_or_community,
            target,
            ContextData(),
            ObjectType(ObjectIdentity(oid), Integer(status)),
        )

        errorIndication, errorStatus, errorIndex, varBinds = await iterator

        if errorIndication:
            print("Error:", errorIndication)
        elif errorStatus:
            print(f"{errorStatus.prettyPrint()} at {varBinds[int(errorIndex) - 1][0]}")
        else:
            print(f"Interface {index} set to {status}")

    async def walk_cdp_info(self):
        return await self.walk(CDP_INT_DESC_OID)

    async def walk_mac_entries(self):
        return await self.walk(MAC_ENTRIES_OID)

    async def walk_ifdesc(self):
        return await self.walk(INT_DESC_BASE_OID)

    async def get_hostname(self):
        results = await self.get(HOSTNAME)
        return str(results[0]) if results else None
    
    async def get_sys_location(self):
        results = await self.get(SYS_LOCATION)
        return str(results[0]) if results else None
    
    async def get_sys_contact(self):
        results = await self.get(SYS_CONTACT)
        return str(results[0]) if results else None

    def decode_hex_string(self, hex_string):
        if hex_string.startswith("0x"):
            hex_string = hex_string[2:]
        try:
            return bytes.fromhex(hex_string).decode("ascii", errors="ignore")
        except ValueError:
            return hex_string

    def close(self):
        self.snmpEngine.close_dispatcher()
