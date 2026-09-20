"""Disk Insight — safe local disk usage analysis."""

from .core import FileRecord, ScanResult, export_json, fingerprint, human_size, scan

__all__ = ["FileRecord", "ScanResult", "export_json", "fingerprint", "human_size", "scan"]
__version__ = "1.0.0"
