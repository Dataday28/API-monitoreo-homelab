from pydantic import BaseModel
from typing import List, Optional, Any, Dict

class CpuInfo(BaseModel):
    usage_percent: float
    per_core_percent: List[float]
    freq_current_mhz: Optional[float]
    freq_min_mhz: Optional[float]
    freq_max_mhz: Optional[float]
    cores_physical: Optional[int]
    cores_logical: int
    load_avg_1: Optional[float]
    load_avg_5: Optional[float]
    load_avg_15: Optional[float]
    
class MemoryInfo(BaseModel):
    total: int
    avalible: int
    used: int
    percent: float
    swap_total: int
    swap_used: int
    swap_percent: float

class DiskPartitionInfo(BaseModel):
    device: str
    mountpoint: str
    fstype: str
    total: int
    used: int
    free: int
    percent: float
    
class NetIoInfo(BaseModel):
    bytes_sent: int
    bytes_recv: int
    packets_sent: int
    packets_recv: int
    errin: int
    errout: int
    dropin: int
    dropout: int
    
class TemperatureReading(BaseModel):
    name: str
    label: str
    current: float
    high: Optional[float]
    critical: Optional[float]
    
class SystemMetricsSnapshot(BaseModel):
    cpu: CpuInfo
    memory: MemoryInfo
    disks: List[DiskPartitionInfo]
    disk_io: Dict[str, Any]
    temps: List[TemperatureReading] = []
    network: NetIoInfo