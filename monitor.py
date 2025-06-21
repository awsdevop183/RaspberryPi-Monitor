#!/usr/bin/env python3
"""
Raspberry Pi Ultra Modern Web System Monitor
A stunning, interactive web-based system monitoring application for Raspberry Pi
Access via browser at http://your_pi_ip:8080
"""

from flask import Flask, render_template, jsonify
import psutil
import subprocess
import json
import socket
from datetime import datetime
import threading
import time
import os

app = Flask(__name__)

class RPiMonitor:
    def __init__(self):
        self.data = {}
        self.monitoring = True
        self.update_data()
        
    def get_cpu_temperature(self):
        """Get CPU temperature for Raspberry Pi"""
        try:
            # Try Raspberry Pi thermal zone
            with open('/sys/class/thermal/thermal_zone0/temp', 'r') as f:
                temp = float(f.read()) / 1000.0
                return temp
        except:
            try:
                # Try vcgencmd for RPi
                result = subprocess.run(['vcgencmd', 'measure_temp'], 
                                     capture_output=True, text=True)
                if result.returncode == 0:
                    temp_str = result.stdout.strip()
                    temp = float(temp_str.split('=')[1].split("'")[0])
                    return temp
            except:
                pass
        return None

    def format_bytes(self, bytes_value):
        """Format bytes to human readable format"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_value < 1024.0:
                return f"{bytes_value:.1f} {unit}"
            bytes_value /= 1024.0
        return f"{bytes_value:.1f} PB"

    def get_uptime(self):
        """Get system uptime"""
        boot_time = psutil.boot_time()
        uptime_seconds = time.time() - boot_time
        uptime_days = uptime_seconds // 86400
        uptime_hours = (uptime_seconds % 86400) // 3600
        uptime_minutes = (uptime_seconds % 3600) // 60
        
        if uptime_days > 0:
            return f"{int(uptime_days)}d {int(uptime_hours)}h {int(uptime_minutes)}m"
        else:
            return f"{int(uptime_hours)}h {int(uptime_minutes)}m"

    def get_system_info(self):
        """Get system information"""
        try:
            with open('/proc/cpuinfo', 'r') as f:
                cpu_info = f.read()
                model_line = [line for line in cpu_info.split('\n') if 'Model' in line]
                model = model_line[0].split(':')[1].strip() if model_line else "Unknown"
        except:
            model = "Unknown"
        
        return {
            'hostname': socket.gethostname(),
            'model': model,
            'os': f"{psutil.os.name} {psutil.sys.platform}",
            'python_version': psutil.sys.version.split()[0],
            'boot_time': datetime.fromtimestamp(psutil.boot_time()).strftime("%Y-%m-%d %H:%M:%S"),
            'uptime': self.get_uptime()
        }

    def get_cpu_info(self):
        """Get CPU information"""
        cpu_percent = psutil.cpu_percent(interval=1)
        core_percentages = psutil.cpu_percent(percpu=True, interval=None)
        cpu_freq = psutil.cpu_freq()
        
        return {
            'usage': cpu_percent,
            'cores': core_percentages,
            'count': psutil.cpu_count(),
            'freq': {
                'current': cpu_freq.current if cpu_freq else 0,
                'min': cpu_freq.min if cpu_freq else 0,
                'max': cpu_freq.max if cpu_freq else 0,
            } if cpu_freq else None
        }

    def get_memory_info(self):
        """Get memory information"""
        memory = psutil.virtual_memory()
        swap = psutil.swap_memory()
        
        return {
            'virtual': {
                'total': memory.total,
                'available': memory.available,
                'used': memory.used,
                'free': memory.free,
                'percent': memory.percent,
                'total_fmt': self.format_bytes(memory.total),
                'available_fmt': self.format_bytes(memory.available),
                'used_fmt': self.format_bytes(memory.used),
                'free_fmt': self.format_bytes(memory.free)
            },
            'swap': {
                'total': swap.total,
                'used': swap.used,
                'free': swap.free,
                'percent': swap.percent,
                'total_fmt': self.format_bytes(swap.total),
                'used_fmt': self.format_bytes(swap.used),
                'free_fmt': self.format_bytes(swap.free)
            }
        }

    def get_storage_info(self):
        """Get storage information"""
        partitions = psutil.disk_partitions()
        storage_info = []
        
        for partition in partitions:
            try:
                partition_usage = psutil.disk_usage(partition.mountpoint)
                percent = (partition_usage.used / partition_usage.total) * 100
                
                storage_info.append({
                    'device': partition.device,
                    'mountpoint': partition.mountpoint,
                    'fstype': partition.fstype,
                    'total': partition_usage.total,
                    'used': partition_usage.used,
                    'free': partition_usage.free,
                    'percent': percent,
                    'total_fmt': self.format_bytes(partition_usage.total),
                    'used_fmt': self.format_bytes(partition_usage.used),
                    'free_fmt': self.format_bytes(partition_usage.free)
                })
            except PermissionError:
                continue
                
        return storage_info

    def get_network_info(self):
        """Get network information"""
        net_io = psutil.net_io_counters()
        
        # Get network interfaces
        addrs = psutil.net_if_addrs()
        interfaces = []
        for interface_name, interface_addresses in addrs.items():
            for address in interface_addresses:
                if str(address.family) == 'AddressFamily.AF_INET':
                    interfaces.append({
                        'name': interface_name,
                        'ip': address.address
                    })
        
        return {
            'bytes_sent': net_io.bytes_sent,
            'bytes_recv': net_io.bytes_recv,
            'packets_sent': net_io.packets_sent,
            'packets_recv': net_io.packets_recv,
            'bytes_sent_fmt': self.format_bytes(net_io.bytes_sent),
            'bytes_recv_fmt': self.format_bytes(net_io.bytes_recv),
            'interfaces': interfaces
        }

    def get_temperature_info(self):
        """Get temperature information"""
        temp = self.get_cpu_temperature()
        if temp is not None:
            if temp > 70:
                status = "Critical"
                status_class = "danger"
            elif temp > 60:
                status = "Warning"
                status_class = "warning"
            elif temp > 45:
                status = "Warm"
                status_class = "info"
            else:
                status = "Cool"
                status_class = "success"
                
            return {
                'temperature': temp,
                'status': status,
                'status_class': status_class
            }
        return {'temperature': None, 'status': 'Unknown', 'status_class': 'secondary'}

    def get_process_info(self):
        """Get top processes information"""
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'username', 'status']):
            try:
                processes.append(proc.info)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        
        # Sort by CPU usage and take top 15
        processes.sort(key=lambda x: x['cpu_percent'] or 0, reverse=True)
        return processes[:15]

    def update_data(self):
        """Update all system data"""
        self.data = {
            'system': self.get_system_info(),
            'cpu': self.get_cpu_info(),
            'memory': self.get_memory_info(),
            'storage': self.get_storage_info(),
            'network': self.get_network_info(),
            'temperature': self.get_temperature_info(),
            'processes': self.get_process_info(),
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

# Initialize monitor
monitor = RPiMonitor()

def update_monitor_data():
    """Background thread to update monitor data"""
    while monitor.monitoring:
        monitor.update_data()
        time.sleep(2)

# Start background monitoring
monitor_thread = threading.Thread(target=update_monitor_data, daemon=True)
monitor_thread.start()

@app.route('/')
def index():
    """Main dashboard page"""
    return INDEX_HTML

@app.route('/api/data')
def get_data():
    """API endpoint to get system data"""
    return jsonify(monitor.data)

# Ultra Modern HTML Template
INDEX_HTML = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🍓 Raspberry Pi Ultra Monitor</title>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        :root {
            --primary-bg: #0a0a0f;
            --secondary-bg: #1a1a2e;
            --card-bg: #16213e;
            --accent-1: #00f5ff;
            --accent-2: #ff006e;
            --accent-3: #8338ec;
            --accent-4: #3a86ff;
            --success: #06ffa5;
            --warning: #ffb700;
            --danger: #ff3838;
            --text-primary: #ffffff;
            --text-secondary: #a0a9c7;
            --glass-bg: rgba(22, 33, 62, 0.3);
            --glow: 0 0 30px rgba(0, 245, 255, 0.3);
        }

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Inter', 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, var(--primary-bg) 0%, var(--secondary-bg) 50%, #0e1b3c 100%);
            color: var(--text-primary);
            min-height: 100vh;
            padding: 20px;
            overflow-x: hidden;
            position: relative;
        }

        body::before {
            content: '';
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: 
                radial-gradient(circle at 20% 20%, rgba(0, 245, 255, 0.1) 0%, transparent 50%),
                radial-gradient(circle at 80% 80%, rgba(255, 0, 110, 0.1) 0%, transparent 50%),
                radial-gradient(circle at 50% 50%, rgba(131, 56, 236, 0.05) 0%, transparent 50%);
            pointer-events: none;
            z-index: -1;
        }

        .container {
            max-width: 1600px;
            margin: 0 auto;
            position: relative;
            z-index: 1;
        }

        .header {
            text-align: center;
            margin-bottom: 40px;
            padding: 40px;
            background: var(--glass-bg);
            border-radius: 25px;
            backdrop-filter: blur(20px);
            border: 1px solid rgba(0, 245, 255, 0.2);
            box-shadow: var(--glow);
            position: relative;
            overflow: hidden;
        }

        .header h1 {
            font-size: 3.5rem;
            margin-bottom: 15px;
            background: linear-gradient(45deg, var(--accent-1), var(--accent-2), var(--accent-3));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            font-weight: 800;
            letter-spacing: -2px;
            text-shadow: 0 0 30px rgba(0, 245, 255, 0.5);
        }

        .header-subtitle {
            font-size: 1.4rem;
            color: var(--text-secondary);
            margin-bottom: 20px;
        }

        .status-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-top: 30px;
        }

        .status-item {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 10px;
            padding: 15px;
            background: rgba(255, 255, 255, 0.05);
            border-radius: 15px;
            border: 1px solid rgba(0, 245, 255, 0.3);
        }

        .status-indicator {
            width: 12px;
            height: 12px;
            border-radius: 50%;
            background: var(--success);
            animation: pulse 2s infinite;
            box-shadow: 0 0 10px var(--success);
        }

        @keyframes pulse {
            0%, 100% { opacity: 1; transform: scale(1); }
            50% { opacity: 0.7; transform: scale(1.1); }
        }

        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 25px;
            margin-bottom: 25px;
        }

        .card {
            background: var(--glass-bg);
            border-radius: 20px;
            padding: 30px;
            backdrop-filter: blur(20px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
            position: relative;
            overflow: hidden;
        }

        .card:hover {
            transform: translateY(-10px);
            box-shadow: 0 20px 60px rgba(0, 245, 255, 0.3);
            border-color: var(--accent-1);
        }

        .card-header {
            display: flex;
            align-items: center;
            gap: 15px;
            margin-bottom: 25px;
            padding-bottom: 15px;
            border-bottom: 2px solid rgba(0, 245, 255, 0.3);
        }

        .card-icon {
            font-size: 2rem;
            background: linear-gradient(45deg, var(--accent-1), var(--accent-4));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }

        .card-title {
            font-size: 1.5rem;
            font-weight: 700;
            color: var(--text-primary);
            letter-spacing: -0.5px;
        }

        .big-metric {
            text-align: center;
            margin-bottom: 25px;
        }

        .big-metric-value {
            font-size: 4rem;
            font-weight: 900;
            background: linear-gradient(45deg, var(--accent-1), var(--accent-2));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin-bottom: 10px;
        }

        .big-metric-label {
            color: var(--text-secondary);
            font-size: 1rem;
            text-transform: uppercase;
            letter-spacing: 2px;
            font-weight: 500;
        }

        .progress-container {
            margin: 20px 0;
        }

        .progress-bar {
            width: 100%;
            height: 12px;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 10px;
            overflow: hidden;
        }

        .progress-fill {
            height: 100%;
            border-radius: 10px;
            transition: all 0.8s ease;
        }

        .progress-fill.normal {
            background: linear-gradient(90deg, var(--success), var(--accent-4));
        }

        .progress-fill.warning {
            background: linear-gradient(90deg, var(--warning), var(--accent-2));
        }

        .progress-fill.danger {
            background: linear-gradient(90deg, var(--danger), var(--accent-2));
        }

        .metric {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
            padding: 12px 0;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }

        .metric-label {
            color: var(--text-secondary);
            font-size: 1rem;
            font-weight: 500;
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .metric-value {
            color: var(--text-primary);
            font-weight: 700;
            font-size: 1.1rem;
            background: linear-gradient(45deg, var(--accent-1), var(--accent-4));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }

        .core-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(90px, 1fr));
            gap: 15px;
            margin-top: 20px;
        }

        .core-item {
            background: rgba(255, 255, 255, 0.05);
            padding: 15px;
            border-radius: 12px;
            text-align: center;
            border: 1px solid rgba(0, 245, 255, 0.2);
            transition: all 0.3s ease;
        }

        .core-item:hover {
            background: rgba(0, 245, 255, 0.1);
            transform: translateY(-3px);
        }

        .core-label {
            font-size: 0.8rem;
            color: var(--text-secondary);
            margin-bottom: 8px;
            text-transform: uppercase;
        }

        .core-value {
            font-weight: 800;
            font-size: 1.1rem;
            background: linear-gradient(45deg, var(--accent-1), var(--accent-3));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }

        .status-badge {
            padding: 8px 16px;
            border-radius: 20px;
            font-size: 0.9rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 1px;
            border: 1px solid;
        }

        .status-success { 
            background: rgba(6, 255, 165, 0.2);
            color: var(--success);
            border-color: var(--success);
        }
        .status-warning { 
            background: rgba(255, 183, 0, 0.2);
            color: var(--warning);
            border-color: var(--warning);
        }
        .status-danger { 
            background: rgba(255, 56, 56, 0.2);
            color: var(--danger);
            border-color: var(--danger);
        }
        .status-info { 
            background: rgba(58, 134, 255, 0.2);
            color: var(--accent-4);
            border-color: var(--accent-4);
        }

        .process-table {
            width: 100%;
            border-collapse: collapse;
        }

        .process-table th {
            background: rgba(0, 245, 255, 0.1);
            color: var(--accent-1);
            padding: 15px;
            text-align: left;
            font-weight: 700;
        }

        .process-table td {
            padding: 12px 15px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
            color: var(--text-primary);
        }

        .process-table tr:hover td {
            background: rgba(0, 245, 255, 0.1);
        }

        .storage-item {
            background: rgba(255, 255, 255, 0.03);
            border-radius: 15px;
            padding: 20px;
            margin-bottom: 20px;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }

        .storage-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
        }

        .storage-path {
            font-weight: 700;
            color: var(--accent-1);
            font-size: 1.1rem;
        }

        .storage-type {
            background: rgba(131, 56, 236, 0.2);
            color: var(--accent-3);
            padding: 4px 12px;
            border-radius: 10px;
            font-size: 0.8rem;
        }

        .network-interface {
            background: rgba(255, 255, 255, 0.03);
            border-radius: 12px;
            padding: 15px;
            margin-bottom: 15px;
            border: 1px solid rgba(0, 245, 255, 0.2);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .interface-name {
            font-weight: 700;
            color: var(--accent-1);
        }

        .interface-ip {
            color: var(--text-secondary);
            font-family: 'Consolas', monospace;
        }

        .last-update {
            text-align: center;
            color: var(--text-secondary);
            font-size: 1rem;
            margin-top: 30px;
            padding: 20px;
            background: var(--glass-bg);
            border-radius: 15px;
            backdrop-filter: blur(20px);
            border: 1px solid rgba(255, 255, 255, 0.1);
        }

        @media (max-width: 768px) {
            .grid {
                grid-template-columns: 1fr;
            }
            
            .header h1 {
                font-size: 2.5rem;
            }
            
            .big-metric-value {
                font-size: 2.5rem;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🍓 Raspberry Pi Ultra Monitor</h1>
            <div class="header-subtitle">Real-time System Performance Dashboard</div>
            <div class="status-grid">
                <div class="status-item">
                    <i class="fas fa-server"></i>
                    <span>Host: <strong id="hostname">--</strong></span>
                    <div class="status-indicator"></div>
                </div>
                <div class="status-item">
                    <i class="fas fa-clock"></i>
                    <span>Last Update: <strong id="header_update">--</strong></span>
                </div>
            </div>
        </div>

        <div class="grid">
            <!-- System Info Card -->
            <div class="card">
                <div class="card-header">
                    <i class="fas fa-microchip card-icon"></i>
                    <div class="card-title">System Information</div>
                </div>
                <div class="metric">
                    <span class="metric-label"><i class="fas fa-desktop"></i>Model:</span>
                    <span class="metric-value" id="model">--</span>
                </div>
                <div class="metric">
                    <span class="metric-label"><i class="fab fa-linux"></i>OS:</span>
                    <span class="metric-value" id="os">--</span>
                </div>
                <div class="metric">
                    <span class="metric-label"><i class="fab fa-python"></i>Python:</span>
                    <span class="metric-value" id="python">--</span>
                </div>
                <div class="metric">
                    <span class="metric-label"><i class="fas fa-power-off"></i>Boot Time:</span>
                    <span class="metric-value" id="boot_time">--</span>
                </div>
                <div class="metric">
                    <span class="metric-label"><i class="fas fa-hourglass-half"></i>Uptime:</span>
                    <span class="metric-value" id="uptime">--</span>
                </div>
            </div>

            <!-- CPU Card -->
            <div class="card">
                <div class="card-header">
                    <i class="fas fa-tachometer-alt card-icon"></i>
                    <div class="card-title">CPU Performance</div>
                </div>
                <div class="big-metric">
                    <div class="big-metric-value" id="cpu_usage">0%</div>
                    <div class="big-metric-label">CPU Usage</div>
                </div>
                <div class="progress-container">
                    <div class="progress-bar">
                        <div class="progress-fill normal" id="cpu_progress"></div>
                    </div>
                </div>
                <div class="metric">
                    <span class="metric-label"><i class="fas fa-microchip"></i>Cores:</span>
                    <span class="metric-value" id="cpu_cores_count">--</span>
                </div>
                <div class="core-grid" id="cpu_cores"></div>
            </div>

            <!-- Memory Card -->
            <div class="card">
                <div class="card-header">
                    <i class="fas fa-memory card-icon"></i>
                    <div class="card-title">Memory Usage</div>
                </div>
                <div class="big-metric">
                    <div class="big-metric-value" id="memory_usage">0%</div>
                    <div class="big-metric-label">Memory Usage</div>
                </div>
                <div class="progress-container">
                    <div class="progress-bar">
                        <div class="progress-fill normal" id="memory_progress"></div>
                    </div>
                </div>
                <div class="metric">
                    <span class="metric-label"><i class="fas fa-hdd"></i>Total:</span>
                    <span class="metric-value" id="memory_total">--</span>
                </div>
                <div class="metric">
                    <span class="metric-label"><i class="fas fa-chart-pie"></i>Used:</span>
                    <span class="metric-value" id="memory_used">--</span>
                </div>
                <div class="metric">
                    <span class="metric-label"><i class="fas fa-battery-full"></i>Available:</span>
                    <span class="metric-value" id="memory_available">--</span>
                </div>
            </div>

            <!-- Temperature Card -->
            <div class="card">
                <div class="card-header">
                    <i class="fas fa-thermometer-half card-icon"></i>
                    <div class="card-title">System Temperature</div>
                </div>
                <div class="big-metric">
                    <div class="big-metric-value" id="temperature">--°C</div>
                    <div class="big-metric-label">CPU Temperature</div>
                </div>
                <div class="progress-container">
                    <div class="progress-bar">
                        <div class="progress-fill normal" id="temp_progress"></div>
                    </div>
                </div>
                <div style="text-align: center; margin-top: 20px;">
                    <span class="status-badge status-success" id="temp_status">Normal</span>
                </div>
            </div>

            <!-- Network Card -->
            <div class="card">
                <div class="card-header">
                    <i class="fas fa-network-wired card-icon"></i>
                    <div class="card-title">Network Activity</div>
                </div>
                <div class="metric">
                    <span class="metric-label"><i class="fas fa-upload"></i>Bytes Sent:</span>
                    <span class="metric-value" id="bytes_sent">--</span>
                </div>
                <div class="metric">
                    <span class="metric-label"><i class="fas fa-download"></i>Bytes Received:</span>
                    <span class="metric-value" id="bytes_recv">--</span>
                </div>
                <div class="metric">
                    <span class="metric-label"><i class="fas fa-paper-plane"></i>Packets Sent:</span>
                    <span class="metric-value" id="packets_sent">--</span>
                </div>
                <div class="metric">
                    <span class="metric-label"><i class="fas fa-inbox"></i>Packets Received:</span>
                    <span class="metric-value" id="packets_recv">--</span>
                </div>
                <div id="network_interfaces"></div>
            </div>

            <!-- Storage Card -->
            <div class="card">
                <div class="card-header">
                    <i class="fas fa-hard-drive card-icon"></i>
                    <div class="card-title">Storage Usage</div>
                </div>
                <div id="storage_info"></div>
            </div>
        </div>

        <!-- Processes Card (Full Width) -->
        <div class="card">
            <div class="card-header">
                <i class="fas fa-tasks card-icon"></i>
                <div class="card-title">Top Processes (CPU Usage)</div>
            </div>
            <table class="process-table">
                <thead>
                    <tr>
                        <th>PID</th>
                        <th>Name</th>
                        <th>User</th>
                        <th>Status</th>
                        <th>CPU%</th>
                        <th>Memory%</th>
                    </tr>
                </thead>
                <tbody id="process_tbody">
                </tbody>
            </table>
        </div>

        <div class="last-update">
            <i class="fas fa-sync-alt"></i> Last updated: <span id="last_update">--</span>
        </div>
    </div>

    <script>
        function updateProgressBar(element, percentage) {
            element.style.width = percentage + '%';
            
            element.className = 'progress-fill';
            if (percentage > 80) {
                element.classList.add('danger');
            } else if (percentage > 60) {
                element.classList.add('warning');
            } else {
                element.classList.add('normal');
            }
        }

        function updateData() {
            fetch('/api/data')
                .then(response => response.json())
                .then(data => {
                    // System Info
                    document.getElementById('hostname').textContent = data.system.hostname;
                    document.getElementById('model').textContent = data.system.model;
                    document.getElementById('os').textContent = data.system.os;
                    document.getElementById('python').textContent = data.system.python_version;
                    document.getElementById('boot_time').textContent = data.system.boot_time;
                    document.getElementById('uptime').textContent = data.system.uptime;

                    // CPU Info
                    document.getElementById('cpu_usage').textContent = data.cpu.usage.toFixed(1) + '%';
                    document.getElementById('cpu_cores_count').textContent = data.cpu.count;
                    updateProgressBar(document.getElementById('cpu_progress'), data.cpu.usage);

                    // CPU Cores
                    const coresContainer = document.getElementById('cpu_cores');
                    coresContainer.innerHTML = '';
                    data.cpu.cores.forEach((core, index) => {
                        const coreDiv = document.createElement('div');
                        coreDiv.className = 'core-item';
                        coreDiv.innerHTML = `
                            <div class="core-label">Core ${index}</div>
                            <div class="core-value">${core.toFixed(1)}%</div>
                        `;
                        coresContainer.appendChild(coreDiv);
                    });

                    // Memory Info
                    document.getElementById('memory_usage').textContent = data.memory.virtual.percent.toFixed(1) + '%';
                    updateProgressBar(document.getElementById('memory_progress'), data.memory.virtual.percent);
                    
                    document.getElementById('memory_total').textContent = data.memory.virtual.total_fmt;
                    document.getElementById('memory_used').textContent = data.memory.virtual.used_fmt;
                    document.getElementById('memory_available').textContent = data.memory.virtual.available_fmt;

                    // Temperature
                    if (data.temperature.temperature !== null) {
                        document.getElementById('temperature').textContent = data.temperature.temperature.toFixed(1) + '°C';
                        const tempPercent = Math.min(100, (data.temperature.temperature / 85) * 100);
                        updateProgressBar(document.getElementById('temp_progress'), tempPercent);
                        
                        const tempStatus = document.getElementById('temp_status');
                        tempStatus.textContent = data.temperature.status;
                        tempStatus.className = 'status-badge status-' + data.temperature.status_class;
                    } else {
                        document.getElementById('temperature').textContent = 'N/A';
                        document.getElementById('temp_status').textContent = 'Unknown';
                    }

                    // Network
                    document.getElementById('bytes_sent').textContent = data.network.bytes_sent_fmt;
                    document.getElementById('bytes_recv').textContent = data.network.bytes_recv_fmt;
                    document.getElementById('packets_sent').textContent = data.network.packets_sent.toLocaleString();
                    document.getElementById('packets_recv').textContent = data.network.packets_recv.toLocaleString();

                    // Network Interfaces
                    const interfacesContainer = document.getElementById('network_interfaces');
                    interfacesContainer.innerHTML = '';
                    data.network.interfaces.forEach(interface => {
                        const interfaceDiv = document.createElement('div');
                        interfaceDiv.className = 'network-interface';
                        interfaceDiv.innerHTML = `
                            <div class="interface-name">${interface.name}</div>
                            <div class="interface-ip">${interface.ip}</div>
                        `;
                        interfacesContainer.appendChild(interfaceDiv);
                    });

                    // Storage
                    const storageContainer = document.getElementById('storage_info');
                    storageContainer.innerHTML = '';
                    data.storage.forEach(storage => {
                        const storageDiv = document.createElement('div');
                        storageDiv.className = 'storage-item';
                        storageDiv.innerHTML = `
                            <div class="storage-header">
                                <div class="storage-path">
                                    <i class="fas fa-folder"></i> ${storage.mountpoint}
                                </div>
                                <div class="storage-type">${storage.fstype}</div>
                            </div>
                            <div class="metric">
                                <span class="metric-label">Usage:</span>
                                <span class="metric-value">${storage.percent.toFixed(1)}%</span>
                            </div>
                            <div class="progress-container">
                                <div class="progress-bar">
                                    <div class="progress-fill ${storage.percent > 80 ? 'danger' : storage.percent > 60 ? 'warning' : 'normal'}" 
                                         style="width: ${storage.percent}%"></div>
                                </div>
                            </div>
                            <div class="metric">
                                <span class="metric-label">Space:</span>
                                <span class="metric-value">${storage.used_fmt} / ${storage.total_fmt}</span>
                            </div>
                        `;
                        storageContainer.appendChild(storageDiv);
                    });

                    // Processes
                    const processTableBody = document.getElementById('process_tbody');
                    processTableBody.innerHTML = '';
                    data.processes.forEach(process => {
                        const row = document.createElement('tr');
                        row.innerHTML = `
                            <td>${process.pid || 'N/A'}</td>
                            <td style="max-width: 200px; overflow: hidden; text-overflow: ellipsis;">${process.name || 'N/A'}</td>
                            <td>${process.username || 'N/A'}</td>
                            <td>${process.status || 'unknown'}</td>
                            <td><span style="color: var(--accent-1); font-weight: bold;">${(process.cpu_percent || 0).toFixed(1)}%</span></td>
                            <td><span style="color: var(--accent-2); font-weight: bold;">${(process.memory_percent || 0).toFixed(1)}%</span></td>
                        `;
                        processTableBody.appendChild(row);
                    });

                    // Update timestamps
                    const now = new Date().toLocaleTimeString();
                    document.getElementById('last_update').textContent = data.timestamp;
                    document.getElementById('header_update').textContent = now;
                })
                .catch(error => {
                    console.error('Error fetching data:', error);
                    
                    const statusIndicator = document.querySelector('.status-indicator');
                    if (statusIndicator) {
                        statusIndicator.style.background = 'var(--danger)';
                    }
                });
        }

        // Update data immediately and then every 2 seconds
        updateData();
        setInterval(updateData, 2000);

        console.log('🍓 Raspberry Pi Ultra Monitor loaded successfully!');
    </script>
</body>
</html>
'''

if __name__ == '__main__':
    print("🍓 Raspberry Pi Ultra Monitor Starting...")
    print("=" * 50)
    print("📱 Local Access:     http://localhost:8080")
    print("🌐 Network Access:   http://YOUR_PI_IP:8080")
    print("🔄 Auto-refresh:     Every 2 seconds")
    print("❌ Stop server:      Ctrl+C")
    print("=" * 50)
    
    try:
        app.run(host='0.0.0.0', port=8080, debug=False)
    except KeyboardInterrupt:
        print("\n👋 Ultra Monitor stopped by user")
        monitor.monitoring = False