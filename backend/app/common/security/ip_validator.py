"""IP validator and SSRF defense utilities.

Strictly blocks all private, loopback, link-local, multicast, and reserved IP ranges.
"""

from __future__ import annotations

import ipaddress
import socket
from typing import Sequence

# Forbidden CIDR blocks
BLOCKED_NETWORKS: tuple[ipaddress.IPv4Network | ipaddress.IPv6Network, ...] = (
    ipaddress.ip_network("0.0.0.0/8"),
    ipaddress.ip_network("10.0.0.0/8"),
    ipaddress.ip_network("100.64.0.0/10"),
    ipaddress.ip_network("127.0.0.0/8"),
    ipaddress.ip_network("169.254.0.0/16"),  # Cloud instance metadata (169.254.169.254)
    ipaddress.ip_network("172.16.0.0/12"),
    ipaddress.ip_network("192.0.0.0/24"),
    ipaddress.ip_network("192.0.2.0/24"),
    ipaddress.ip_network("192.88.99.0/24"),
    ipaddress.ip_network("192.168.0.0/16"),
    ipaddress.ip_network("198.18.0.0/15"),
    ipaddress.ip_network("198.51.100.0/24"),
    ipaddress.ip_network("203.0.113.0/24"),
    ipaddress.ip_network("224.0.0.0/4"),    # Multicast
    ipaddress.ip_network("240.0.0.0/4"),    # Reserved
    ipaddress.ip_network("255.255.255.255/32"),
    # IPv6 blocks
    ipaddress.ip_network("::/128"),
    ipaddress.ip_network("::1/128"),         # IPv6 Loopback
    ipaddress.ip_network("fc00::/7"),        # Unique Local Address
    ipaddress.ip_network("fe80::/10"),       # Link Local
    ipaddress.ip_network("ff00::/8"),        # Multicast
)


class SSRFValidationError(ValueError):
    """Raised when an outbound URL resolves to a disallowed or private IP."""

    pass


def is_ip_allowed(ip_str: str) -> bool:
    """Checks whether an IP address is a safe, public, routable IP."""
    try:
        ip = ipaddress.ip_address(ip_str)
    except ValueError:
        return False

    if (
        ip.is_private
        or ip.is_loopback
        or ip.is_link_local
        or ip.is_multicast
        or ip.is_reserved
        or ip.is_unspecified
    ):
        return False

    for network in BLOCKED_NETWORKS:
        if ip in network:
            return False

    return True


def resolve_and_validate_hostname(hostname: str) -> list[str]:
    """Resolves DNS for a hostname and verifies all resolved IP addresses are safe.

    Raises SSRFValidationError if any resolved address is private or link-local.
    """
    clean_host = hostname.strip().lower()
    if clean_host in ("localhost", "127.0.0.1", "::1", "0.0.0.0"):
        raise SSRFValidationError(f"Hostname '{hostname}' resolves to forbidden loopback target")

    # Direct IP string check
    try:
        ip_direct = ipaddress.ip_address(clean_host)
        if not is_ip_allowed(str(ip_direct)):
            raise SSRFValidationError(f"Direct IP target '{clean_host}' is a forbidden private address")
        return [str(ip_direct)]
    except ValueError:
        pass

    # Resolve via socket
    try:
        addr_info = socket.getaddrinfo(clean_host, None)
    except socket.gaierror as err:
        raise SSRFValidationError(f"Could not resolve host '{clean_host}': {err}")

    resolved_ips: list[str] = []
    for family, socktype, proto, canonname, sockaddr in addr_info:
        ip_addr = sockaddr[0]
        if not is_ip_allowed(ip_addr):
            raise SSRFValidationError(
                f"SSRF Alert: Host '{clean_host}' resolved to forbidden address '{ip_addr}'"
            )
        resolved_ips.append(ip_addr)

    if not resolved_ips:
        raise SSRFValidationError(f"No valid IP addresses resolved for '{clean_host}'")

    return list(set(resolved_ips))
