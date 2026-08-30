"""
NetSage AI deterministic rule checker.
This script checks common lab configuration mistakes using structured case evidence.
It is intentionally deterministic and does not replace human review.
"""

import re
import ipaddress
from collections import defaultdict

def check_duplicate_ips(text):
    ips = re.findall(r'\b(?:\d{1,3}\.){3}\d{1,3}\b', text)
    counts = defaultdict(int)
    for ip in ips:
        try:
            ipaddress.ip_address(ip)
            counts[ip] += 1
        except ValueError:
            pass
    return [ip for ip, count in counts.items() if count > 1]

def check_gateway_mismatch(ip_text):
    m = re.search(r'IPv4(?: Address)?:\s*(\S+).*?Mask:\s*(\S+).*?Gateway:\s*(\S+)', ip_text, re.I | re.S)
    if not m:
        return False, "IP/gateway pattern not found"
    ip, mask, gw = m.groups()
    try:
        network = ipaddress.ip_network(f"{ip}/{mask}", strict=False)
        return ipaddress.ip_address(gw) not in network, f"IP={ip}, network={network}, gateway={gw}"
    except ValueError:
        return False, "Invalid IP or mask"

def check_interface_down(text):
    return bool(re.search(r'(administratively down|disabled|shutdown)', text, re.I))

def check_missing_vlan(text, vlan_id):
    return not bool(re.search(rf'\bVLAN\s+{vlan_id}\b', text, re.I))

def check_missing_route(text, destination):
    return not bool(re.search(re.escape(destination), text))

def run_checks(case):
    evidence = case.get("show_outputs", "")
    findings = []

    duplicates = check_duplicate_ips(evidence)
    if duplicates:
        findings.append(("HIGH", f"Possible duplicate IP(s): {', '.join(duplicates)}"))

    mismatch, detail = check_gateway_mismatch(evidence)
    if mismatch:
        findings.append(("HIGH", f"Gateway mismatch detected: {detail}"))

    if check_interface_down(evidence):
        findings.append(("HIGH", "Disabled/shutdown interface evidence detected"))

    # Common known VLAN checks based on the expected fault text.
    fault = case.get("expected_fault", "").lower()
    vlan_match = re.search(r'vlan\s+(\d+)', fault)
    if "missing" in fault and vlan_match:
        vlan_id = vlan_match.group(1)
        if check_missing_vlan(evidence, vlan_id):
            findings.append(("HIGH", f"Expected VLAN {vlan_id} appears absent from supplied evidence"))

    if "missing route" in fault.lower() or "route" in fault.lower() and "missing" in fault.lower():
        findings.append(("HIGH", "Case indicates a missing routing entry; verify with show ip route"))

    return findings

if __name__ == "__main__":
    sample = {
        "show_outputs": """ipconfig
IPv4 Address: 192.168.10.25
Mask: 255.255.255.0
Gateway: 192.168.20.1
show interfaces status
Fa0/5 disabled""",
        "expected_fault": "Wrong default gateway; interface is disabled"
    }
    results = run_checks(sample)
    print("NetSage AI Rule Checker")
    print("=======================")
    if not results:
        print("No deterministic faults detected.")
    else:
        for severity, finding in results:
            print(f"[{severity}] {finding}")
