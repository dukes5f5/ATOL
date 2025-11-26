# -*- coding: utf-8 -*-
"""
LicenseManager - License validation for ATOL application.
Adapted from DEFAULT_UIs with per-deployment user key, machine-bound fingerprint,
and master override support.
"""

import hashlib
import platform
import time
from pathlib import Path


class LicenseManager:
    """
    Hardened license manager with:
    - Per-deployment user key (userkey.txt)
    - Machine-bound fingerprint
    - Master override via hashed MASTER_KEY.txt
    - Lock file to prevent resets
    """

    LICENSE_FILE = Path("license.dat")
    USERKEY_FILE = Path("userkey.txt")
    MASTERKEY_FILE = Path("MASTER_KEY.txt")
    LOCK_FILE = Path("license.lock")
    TIMEOUT_DAYS = 7

    # SHA-256 hash of the private master key
    # NOTE: In production, this should be loaded from an external configuration file
    # or environment variable for better security. The current implementation is
    # suitable for development/internal use.
    MASTER_KEY_HASH = "dd4846ec22c9f00d8462bb5cddd7a24d7c72b15d54b4224f5ffd47c1b6c6f4bd"

    def __init__(self):
        self.user_key = self._read_user_key()
        self.fingerprint = self._generate_fingerprint()

    def _read_user_key(self) -> str:
        """Read and validate the user key from userkey.txt."""
        if not self.USERKEY_FILE.exists():
            raise FileNotFoundError("Missing userkey.txt in project root.")
        key = self.USERKEY_FILE.read_text().strip()
        if len(key) != 19 or key.count("-") != 3:
            raise ValueError("userkey.txt must be in format XXXX-XXXX-XXXX-XXXX")
        return key

    def _generate_fingerprint(self) -> str:
        """Generate a machine-bound fingerprint based on system info and user key."""
        sys_info = f"{platform.node()}-{platform.system()}-{platform.machine()}"
        combined = f"{sys_info}|{self.user_key}"
        return hashlib.sha256(combined.encode()).hexdigest()

    def _now(self) -> int:
        """Return the current Unix timestamp."""
        return int(time.time())

    def _read_license(self):
        """Read and parse the license file."""
        if not self.LICENSE_FILE.exists():
            return None
        try:
            data = self.LICENSE_FILE.read_text().strip().split("|")
            return {"fingerprint": data[0], "timestamp": int(data[1])}
        except Exception:
            return None

    def _write_license(self):
        """Write the license file and lock file."""
        data = f"{self.fingerprint}|{self._now()}"
        self.LICENSE_FILE.write_text(data)
        self.LOCK_FILE.write_text("locked")

    def _check_master_key(self) -> bool:
        """Check if the master key file contains a valid master key."""
        if not self.MASTERKEY_FILE.exists():
            return False
        key = self.MASTERKEY_FILE.read_text().strip()
        hashed = hashlib.sha256(key.encode()).hexdigest()
        return hashed == self.MASTER_KEY_HASH

    def check(self) -> bool:
        """
        Validate the license.
        Returns True if:
        - Master key override is valid, OR
        - License file and lock file exist with valid fingerprint and within timeout
        """
        # Master override bypass
        if self._check_master_key():
            return True

        # Hardened: both files must exist
        if not self.LICENSE_FILE.exists() or not self.LOCK_FILE.exists():
            return False

        lic = self._read_license()
        if lic is None:
            return False

        if lic["fingerprint"] != self.fingerprint:
            return False

        elapsed_days = (self._now() - lic["timestamp"]) / (60 * 60 * 24)
        return elapsed_days <= self.TIMEOUT_DAYS

    def initialize(self) -> bool:
        """
        Initialize a new license if none exists.
        Returns True if license was created or already valid.
        """
        if self.check():
            return True
        
        # Create new license
        self._write_license()
        return self.check()
