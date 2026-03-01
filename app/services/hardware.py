from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any, Dict, List, Optional, Tuple
import time
import logging

import psutil

# Models
@dataclass(frozen=True)
class CpuInfo:
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
    
@dataclass(frozen=True)
class MemoryInfo:
    total: int
    avalible: int
    used: int
    percent: float
    swap_total: int
    swap_used: int
    swap_percent: float

@dataclass(frozen=True)
class DiskPartitionInfo:
    device: str
    mountpoint: str
    fstype: str
    total: int
    used: int
    free: int
    percent: float
    
@dataclass(frozen=True)
class NetIoInfo:
    bytes_sent: int
    bytes_recv: int
    packets_sent: int
    packets_recv: int
    errin: int
    errout: int
    dropin: int
    dropout: int
    
@dataclass(frozen=True)
class TemperatureReading:
    name: str
    label: str
    current: float
    high: Optional[float]
    critical: Optional[float]
    

# Funciones

class HardwareReader:
    
    def __init__(self, cpu_interval: float = 0.2) -> None:
        self.cpu_interval = cpu_interval
        
    
    # CPU
    def get_cpu_usage(self) -> CpuInfo:
        usage = psutil.cpu_percent(interval=self.cpu_interval)
        per_core = psutil.cpu_percent(interval=None, percpu=True)
        
        freq = None
        
        try:
            freq = psutil.cpu_freq()
            
        except Exception:
            freq = None
            
        cores_physical = None
        
        try:
            cores_physical = psutil.cpu_count(logical=False)
            
        except Exception:
            cores_physical = None
            
        cores_logical = psutil.cpu_count(logical=True) or 0
        
        load1 = load5 = load15 = None
        
        try:
            la = psutil.getloadavg()
            load1, load5, load15 = la[0], la[1], la[2]
            
        except Exception:
            pass
        
        return CpuInfo(
            usage_percent=float(usage),
            per_core_percent=[float(x) for x in per_core],
            freq_current_mhz=float(freq.current) if freq else None,
            freq_min_mhz=float(freq.min) if freq else None,
            freq_max_mhz=float(freq.max) if freq else None,
            cores_physical=cores_physical,
            cores_logical=int(cores_logical),
            load_avg_1=load1,
            load_avg_5=load5,
            load_avg_15=load15
        )
        
    # Memoria
    def get_memory(self) -> MemoryInfo:
        vm = psutil.virtual_memory()
        sm = psutil.swap_memory()
        
        return MemoryInfo(
            total=int(vm.total),
            avalible=int(vm.available),
            used=int(vm.used),
            percent=float(vm.percent),
            swap_total=int(sm.total),
            swap_used=int(sm.used),
            swap_percent=float(sm.percent)
        )
        
    # Disco
    def get_disks(self, include_all: bool = False) -> List[DiskPartitionInfo]:
        partitions = psutil.disk_partitions(all=include_all)
        results: List[DiskPartitionInfo] = []
        
        for p in partitions:
            try:
                usage = psutil.disk_usage(p.mountpoint)
                
            except PermissionError:
                logging.error("Error de Permisos")
                continue
            except FileNotFoundError:
                logging.error("Archivo no encontrado")
                continue
            
            results.append(
                DiskPartitionInfo(
                    device=p.device,
                    mountpoint=p.mountpoint,
                    fstype=p.fstype,
                    total=int(usage.total),
                    used=int(usage.used),
                    free=int(usage.free),
                    percent=float(usage.percent)
                )
            )
            
        return results
    
    def get_disk_io(self) -> Dict[str, Any]:
        io = psutil.disk_io_counters()
        
        if not io:
            logging.info("No se obtuvo el io")
            return {}
        
        return {
            "read_count": int(io.read_count),
            "write_count": int(io.write_count),
            "read_bytes": int(io.read_bytes),
            "write_bytes": int(io.write_bytes),
            "read_time_ms": int(io.read_time),
            "write_time_ms": int(io.write_time)
        }
        
    # Red
    def get_network_io(self, per_nic: bool = False) -> Dict[str, NetIoInfo] | NetIoInfo:
        if per_nic:
            by_nic = psutil.net_io_counters(pernic=True)
            out: Dict[str, NetIoInfo] = {}
            
            for nic, c in by_nic.items():
                out[nic] = NetIoInfo(
                    bytes_sent=int(c.bytes_sent),
                    bytes_recv=int(c.bytes_recv),
                    packets_sent=int(c.packets_sent),
                    packets_recv=int(c.packets_recv),
                    errin=int(c.errin),
                    errout=int(c.errout),
                    dropin=int(c.dropin),
                    dropout=int(c.dropout)
                )
                
            return out
        
        c = psutil.net_io_counters()
        
        return NetIoInfo(
            bytes_sent=int(c.bytes_sent),
            bytes_recv=int(c.bytes_recv),
            packets_sent=int(c.packets_sent),
            packets_recv=int(c.packets_recv),
            errin=int(c.errin),
            errout=int(c.errout),
            dropin=int(c.dropin),
            dropout=int(c.dropout)
        )
        
    # Temperatura
    def get_temperatures(self) -> List[TemperatureReading]:
        temps: List[TemperatureReading] = []
        
        if not hasattr(psutil, "sensors_temperatures"):
            return temps
        
        try:
            data = psutil.sensors_temperatures(fahrenheit=False) or {}
            
        except Exception:
            logging.error("Error al obtener la temperatura")
            return temps
        
        for sensor_name, entries in data.items():
            for e in entries:
                temps.append(
                    TemperatureReading(
                        name=str(sensor_name),
                        label=str(e.label or ""),
                        current=float(e.current) if e.current is not None else float("nan"),
                        high=float(e.high) if e.high is not None else None,
                        critical=float(e.critical) if e.critical is not None else None
                    )
                )
                
        return temps
    
    # Snapshot
    def snapshot(self) -> Dict[str, Any]:
        cpu = self.get_cpu_usage()
        mem = self.get_memory()
        disks = self.get_disks()
        temp = self.get_temperatures()
        
        return {
            "ts": time.time(),
            "cpu": asdict(cpu),
            "memory": asdict(mem),
            "disks": [asdict(d) for d in disks],
            "disk_io": self.get_disk_io(),
            "temps": [asdict(t) for t in temp],
            "network": asdict(self.get_network_io(per_nic=False))
        }
        
    # Helper
    def bytes_to_human(n: int) -> str:
        units = ["B", "KB", "MB", "GB", "TB", "PB"]
        x = float(n)
        
        for u in units:
            if x < 1024.0:
                return f"{x:.1f} {u}"
            
            x /= 1024.0
            
        return f"{x:.1f} EB"
        

