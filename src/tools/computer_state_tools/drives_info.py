import psutil
from langchain.tools import tool


@tool
def get_disk_info() -> dict:
    """Get information about all drives on the system.

    Returns:
        dict: A dictionary where keys are drive letters and values are dictionaries with 'total', 'used', and 'free' space in GB.
    """
    drives = {}
    partitions = psutil.disk_partitions()

    for partition in partitions:
        try:
            usage = psutil.disk_usage(partition.mountpoint)
            drives[partition.device] = {
                "total": round(usage.total / (1024 ** 3), 2),  # Convert to GB
                "used": round(usage.used / (1024 ** 3), 2),    # Convert to GB
                "free": round(usage.free / (1024 ** 3), 2)     # Convert to GB
            }
        except Exception as e:
            drives[partition.device] = {"error": str(e)}

    return drives
