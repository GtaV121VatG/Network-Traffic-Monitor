import psutil
import time
from datetime import datetime
from collections import defaultdict
import socket
import platform
import os

class NetworkMonitor:
    def __init__(self):
        self.connection_history = []
        self.ip_attempts = defaultdict(list)
        self.port_scans = defaultdict(set)
        self.alerts = []
        
        self.known_safe_ips = {
            '127.0.0.1', '::1', 
            '8.8.8.8', '8.8.4.4',
            '1.1.1.1', '1.0.0.1',
        }
        
        self.suspicious_ports = {23, 445, 3389, 5900, 21, 135, 137, 139, 1433, 3306}
        
        self.logs_dir = 'logs'
        if not os.path.exists(self.logs_dir):
            os.makedirs(self.logs_dir)
    
    def get_device_type(self):
        system = platform.system()
        release = platform.release()
        machine = platform.machine()
        processor = platform.processor()
        
        if system == 'Windows':
            try:
                version = platform.version()
                if '11' in release or '11' in version:
                    return 'Windows 11 PC'
                elif '10' in release:
                    return 'Windows 10 PC'
                else:
                    return f'Windows {release} PC'
            except:
                return 'Windows PC'
                
        elif system == 'Darwin':
            if 'arm' in machine.lower() or 'apple' in processor.lower():
                return 'Mac (Apple Silicon M1/M2/M3)'
            else:
                return 'Mac (Intel)'
                
        elif system == 'Linux':
            try:
                with open('/proc/device-tree/model', 'r') as f:
                    model = f.read()
                    if 'raspberry' in model.lower():
                        return 'Raspberry Pi'
            except:
                pass
            return 'Linux PC'
            
        elif system == 'iOS':
            return 'iPhone/iPad'
            
        elif system == 'Android':
            return 'Android Device'
            
        else:
            return f'{system} Device'
    
    def get_network_info(self):
        network_info = []
        
        try:
            interfaces = psutil.net_if_addrs()
            stats = psutil.net_if_stats()
            
            for interface_name, addresses in interfaces.items():
                if interface_name in stats:
                    stat = stats[interface_name]
                    
                    ipv4_addr = None
                    for addr in addresses:
                        if addr.family == socket.AF_INET:
                            ipv4_addr = addr.address
                            break
                    
                    if stat.isup and ipv4_addr and ipv4_addr != '127.0.0.1':
                        connection_type = 'Unknown'
                        if 'wi-fi' in interface_name.lower() or 'wireless' in interface_name.lower() or 'wlan' in interface_name.lower():
                            connection_type = 'Wi-Fi'
                        elif 'ethernet' in interface_name.lower() or 'eth' in interface_name.lower():
                            connection_type = 'Ethernet'
                        elif 'vpn' in interface_name.lower() or 'tap' in interface_name.lower() or 'tun' in interface_name.lower():
                            connection_type = 'VPN'
                        
                        network_info.append({
                            'name': interface_name,
                            'type': connection_type,
                            'ip': ipv4_addr,
                            'speed': f'{stat.speed} Mbps' if stat.speed > 0 else 'Unknown',
                            'status': 'Connected' if stat.isup else 'Disconnected'
                        })
        except Exception:
            pass
        
        return network_info
    
    def log_alert(self, alert):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        device_type = self.get_device_type()
        
        log_file = os.path.join(self.logs_dir, 'alerts.log')
        
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(f"[{timestamp}] [{alert['severity'].upper()}] {alert['type']}\n")
            f.write(f"Description: {alert['description']}\n")
            f.write(f"IP: {alert.get('ip', 'N/A')}\n")
            f.write(f"Device Type: {device_type}\n")
            f.write(f"{'-'*80}\n")
    
    def log_connections(self, connections):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        log_file = os.path.join(self.logs_dir, 'connections.log')
        
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(f"\n[{timestamp}] Connection Snapshot\n")
            f.write(f"Total Active Connections: {len(connections)}\n")
            f.write(f"{'-'*80}\n")
            
            for conn in connections:
                f.write(f"Process: {conn['process']}\n")
                f.write(f"Local: {conn['local_addr']} -> Remote: {conn['remote_addr']}\n")
                f.write(f"Status: {conn['status']}\n")
                f.write(f"\n")
            
            f.write(f"{'='*80}\n")
        
    def get_active_connections(self):
        connections = []
        
        try:
            for conn in psutil.net_connections(kind='inet'):
                if conn.status == 'ESTABLISHED' or conn.status == 'LISTEN':
                    connection_data = {
                        'local_addr': f"{conn.laddr.ip}:{conn.laddr.port}" if conn.laddr else "N/A",
                        'remote_addr': f"{conn.raddr.ip}:{conn.raddr.port}" if conn.raddr else "N/A",
                        'status': conn.status,
                        'pid': conn.pid,
                        'timestamp': datetime.now().isoformat()
                    }
                    
                    try:
                        if conn.pid:
                            process = psutil.Process(conn.pid)
                            connection_data['process'] = process.name()
                        else:
                            connection_data['process'] = 'Unknown'
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        connection_data['process'] = 'Unknown'
                    
                    connections.append(connection_data)
                    
                    if conn.raddr:
                        self._track_connection(conn.raddr.ip, conn.raddr.port)
                        
        except (psutil.AccessDenied, PermissionError):
            pass
        except Exception:
            pass
        
        if connections:
            self.log_connections(connections)
            
        return connections
    
    def _track_connection(self, ip, port):
        current_time = time.time()
        self.ip_attempts[ip].append(current_time)
        self.ip_attempts[ip] = [t for t in self.ip_attempts[ip] if current_time - t < 60]
        self.port_scans[ip].add(port)
    
    def detect_threats(self):
        threats = []
        current_time = time.time()
        
        for ip, attempts in self.ip_attempts.items():
            recent_attempts = [t for t in attempts if current_time - t < 10]
            
            if len(recent_attempts) > 10:
                threat = {
                    'severity': 'critical',
                    'type': 'Repeated Connection Attempts',
                    'description': f"IP {ip} made {len(recent_attempts)} connection attempts in 10 seconds",
                    'ip': ip,
                    'timestamp': datetime.now().isoformat()
                }
                threats.append(threat)
                self.log_alert(threat)
        
        for ip, ports in self.port_scans.items():
            if len(ports) > 5:
                threat = {
                    'severity': 'critical',
                    'type': 'Port Scan Detected',
                    'description': f"IP {ip} connected to {len(ports)} different ports",
                    'ip': ip,
                    'ports': list(ports),
                    'timestamp': datetime.now().isoformat()
                }
                threats.append(threat)
                self.log_alert(threat)
        
        for conn in psutil.net_connections(kind='inet'):
            if conn.raddr and conn.raddr.port in self.suspicious_ports:
                threat = {
                    'severity': 'warning',
                    'type': 'Suspicious Port Activity',
                    'description': f"Connection to suspicious port {conn.raddr.port} from {conn.raddr.ip}",
                    'ip': conn.raddr.ip,
                    'port': conn.raddr.port,
                    'timestamp': datetime.now().isoformat()
                }
                threats.append(threat)
                self.log_alert(threat)
        
        for ip in self.ip_attempts.keys():
            if ip not in self.known_safe_ips and not ip.startswith('192.168.'):
                if len(self.ip_attempts[ip]) > 3:
                    threat = {
                        'severity': 'info',
                        'type': 'Unknown IP Detected',
                        'description': f"Multiple connections from unknown IP: {ip}",
                        'ip': ip,
                        'timestamp': datetime.now().isoformat()
                    }
                    threats.append(threat)
                    self.log_alert(threat)
        
        return threats
    
    def get_network_stats(self):
        try:
            net_io = psutil.net_io_counters()
            return {
                'bytes_sent': net_io.bytes_sent,
                'bytes_recv': net_io.bytes_recv,
                'packets_sent': net_io.packets_sent,
                'packets_recv': net_io.packets_recv,
                'errors_in': net_io.errin,
                'errors_out': net_io.errout,
                'drops_in': net_io.dropin,
                'drops_out': net_io.dropout
            }
        except Exception:
            return {}
    
    def get_summary(self):
        connections = self.get_active_connections()
        threats = self.detect_threats()
        stats = self.get_network_stats()
        network_info = self.get_network_info()
        device_type = self.get_device_type()
        
        return {
            'active_connections': len(connections),
            'connections': connections[:20],
            'total_alerts': len(threats),
            'alerts': threats[:20],
            'suspicious_ips': len([ip for ip in self.ip_attempts.keys() if len(self.ip_attempts[ip]) > 3]),
            'network_stats': stats,
            'network_info': network_info,
            'device_type': device_type,
            'timestamp': datetime.now().isoformat()
        }