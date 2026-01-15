import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import './App.css';

const API_URL = 'http://localhost:5000/api';

function App() {
    const [isConnected, setIsConnected] = useState(false);
    const [deviceType, setDeviceType] = useState('Unknown');
    const [stats, setStats] = useState({
        active_connections: 0,
        total_alerts: 0,
        suspicious_ips: 0,
        network_stats: {}
    });
    const [connections, setConnections] = useState([]);
    const [alerts, setAlerts] = useState([]);
    const [history, setHistory] = useState([]);
    const [networkInfo, setNetworkInfo] = useState([]);
    const [error, setError] = useState(null);
    const [showHelp, setShowHelp] = useState(false);

    useEffect(() => {
        const checkConnection = async () => {
            try {
                await axios.get(`${API_URL}/status`);
                setIsConnected(true);
                setError(null);
            } catch (err) {
                setIsConnected(false);
                setError('Cannot connect to monitoring server. Make sure Python backend is running on port 5000.');
            }
        };

        checkConnection();
        const interval = setInterval(checkConnection, 5000);
        return () => clearInterval(interval);
    }, []);

    useEffect(() => {
        if (!isConnected) return;

        const fetchData = async () => {
            try {
                const [statsRes, connectionsRes, alertsRes, historyRes] = await Promise.all([
                    axios.get(`${API_URL}/stats`),
                    axios.get(`${API_URL}/connections`),
                    axios.get(`${API_URL}/alerts`),
                    axios.get(`${API_URL}/history`)
                ]);

                setStats(statsRes.data);
                setConnections(connectionsRes.data.connections || []);
                setAlerts(alertsRes.data.alerts || []);
                setHistory(historyRes.data || []);
                setNetworkInfo(statsRes.data.network_info || []);
                setDeviceType(statsRes.data.device_type || 'Unknown');
            } catch (err) {
                console.error('Error fetching data:', err);
            }
        };

        fetchData();
        const interval = setInterval(fetchData, 2000);
        return () => clearInterval(interval);
    }, [isConnected]);

    const formatBytes = (bytes) => {
        if (!bytes) return '0 B';
        const k = 1024;
        const sizes = ['B', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
    };

    return (
        <div className="App">
            <div className="container">
                <header className="header">
                    <div className="header-left">
                        <div className="title-with-help">
                            <h1>Network Traffic Monitor</h1>
                            <button className="help-button" onClick={() => setShowHelp(true)}>
                                ?
                            </button>
                        </div>
                        <p>Real-time monitoring and threat detection system</p>
                    </div>
                    <div className="header-right">
                        <div className="device-info">Device: {deviceType}</div>
                        <div className="status-badge">
                            {isConnected ? 'System Online' : 'System Offline'}
                        </div>
                    </div>
                </header>

                {showHelp && (
                    <div className="help-modal-overlay" onClick={() => setShowHelp(false)}>
                        <div className="help-modal" onClick={(e) => e.stopPropagation()}>
                            <h2>How This Works</h2>

                            <div className="help-section">
                                <h3>What is this?</h3>
                                <p>This is a network monitoring tool that keeps track of what your computer is connecting to on the internet. Think of it like a security camera for your internet connection.</p>
                            </div>

                            <div className="help-section">
                                <h3>Network Interfaces</h3>
                                <p>Shows how your device connects to the internet. You might see Wi-Fi (wireless) or Ethernet (cable). Each one has an IP address, which is like your computer's phone number on the internet.</p>
                            </div>

                            <div className="help-section">
                                <h3>System Statistics</h3>
                                <p>Quick numbers that tell you what's happening right now. Active Connections shows how many programs are talking to the internet. Security Alerts tells you if anything suspicious was detected.</p>
                            </div>

                            <div className="help-section">
                                <h3>Traffic Analysis</h3>
                                <p>The graph shows your internet activity over time. The blue line tracks connections, and the red line shows security warnings. If you see spikes, something is using your internet more than usual.</p>
                            </div>

                            <div className="help-section">
                                <h3>Active Connections</h3>
                                <p>Lists every program on your computer that's currently using the internet. You'll see things like your web browser, system updates, and other apps. Each one shows where it's connecting to.</p>
                            </div>

                            <div className="help-section">
                                <h3>Security Alerts</h3>
                                <p>Warnings about unusual activity. Critical alerts (red) are serious and need attention. Warning alerts (orange) are suspicious but not urgent. Info alerts (blue) are just notifications.</p>
                            </div>

                            <div className="help-section">
                                <h3>Logs</h3>
                                <p>Everything gets saved to files in the backend folder. You can review what happened later if you need to check something. Logs are stored in: network-monitor\backend\logs</p>
                            </div>

                            <button className="back-button" onClick={() => setShowHelp(false)}>
                                Back to Monitor
                            </button>
                        </div>
                    </div>
                )}

                {error && (
                    <div className="error-banner">
                        <strong>Connection Error</strong>
                        {error}
                    </div>
                )}

                {isConnected && (
                    <>
                        {networkInfo.length > 0 && (
                            <div className="section">
                                <div className="section-header">
                                    <h2 className="section-title">Network Interfaces</h2>
                                    <span className="section-count">{networkInfo.length} Active</span>
                                </div>
                                <div className="network-interfaces">
                                    {networkInfo.map((net, idx) => (
                                        <div key={idx} className="interface-card">
                                            <div className="interface-header">
                                                <div className="interface-type">{net.type}</div>
                                                <div className="interface-status">{net.status}</div>
                                            </div>
                                            <div className="interface-name">{net.name}</div>
                                            <div className="interface-detail">
                                                <span className="detail-label">IP Address</span>
                                                <span className="detail-value">{net.ip}</span>
                                            </div>
                                            <div className="interface-detail">
                                                <span className="detail-label">Speed</span>
                                                <span className="detail-value">{net.speed}</span>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        )}

                        <div className="main-grid">
                            <div className="left-column">
                                <div className="section">
                                    <div className="section-header">
                                        <h2 className="section-title">System Statistics</h2>
                                    </div>
                                    <div className="stats-grid">
                                        <div className="stat-box">
                                            <div className="stat-value">{stats.active_connections}</div>
                                            <div className="stat-label">Active Connections</div>
                                        </div>
                                        <div className="stat-box">
                                            <div className="stat-value">{stats.total_alerts}</div>
                                            <div className="stat-label">Security Alerts</div>
                                        </div>
                                        <div className="stat-box">
                                            <div className="stat-value">{stats.suspicious_ips}</div>
                                            <div className="stat-label">Suspicious IPs</div>
                                        </div>
                                        <div className="stat-box">
                                            <div className="stat-value">{formatBytes(stats.network_stats?.bytes_recv)}</div>
                                            <div className="stat-label">Data Received</div>
                                        </div>
                                    </div>
                                </div>

                                <div className="section">
                                    <div className="section-header">
                                        <h2 className="section-title">Traffic Analysis</h2>
                                    </div>
                                    <div className="chart-container">
                                        <ResponsiveContainer width="100%" height={280}>
                                            <LineChart data={history}>
                                                <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" />
                                                <XAxis
                                                    dataKey="timestamp"
                                                    tickFormatter={(time) => new Date(time).toLocaleTimeString()}
                                                    stroke="#666"
                                                    style={{ fontSize: '12px' }}
                                                />
                                                <YAxis stroke="#666" style={{ fontSize: '12px' }} />
                                                <Tooltip
                                                    labelFormatter={(time) => new Date(time).toLocaleTimeString()}
                                                    contentStyle={{ borderRadius: '4px', border: '1px solid #ddd' }}
                                                />
                                                <Legend />
                                                <Line
                                                    type="monotone"
                                                    dataKey="active_connections"
                                                    stroke="#2c3e50"
                                                    strokeWidth={2}
                                                    name="Connections"
                                                    dot={false}
                                                />
                                                <Line
                                                    type="monotone"
                                                    dataKey="total_alerts"
                                                    stroke="#c0392b"
                                                    strokeWidth={2}
                                                    name="Alerts"
                                                    dot={false}
                                                />
                                            </LineChart>
                                        </ResponsiveContainer>
                                    </div>
                                </div>

                                <div className="section">
                                    <div className="section-header">
                                        <h2 className="section-title">Active Connections</h2>
                                        <span className="section-count">{connections.length}</span>
                                    </div>
                                    <div className="connection-list">
                                        {connections.length === 0 ? (
                                            <div className="empty-state">
                                                <div className="empty-state-text">No active connections detected</div>
                                            </div>
                                        ) : (
                                            connections.map((conn, idx) => (
                                                <div key={idx} className="connection-item">
                                                    <div className="connection-row">
                                                        <span className="process-name">{conn.process || 'Unknown Process'}</span>
                                                        <span className="connection-status">{conn.status}</span>
                                                    </div>
                                                    <div className="connection-address">{conn.local_addr} → {conn.remote_addr}</div>
                                                    <div className="connection-time">{new Date(conn.timestamp).toLocaleTimeString()}</div>
                                                </div>
                                            ))
                                        )}
                                    </div>
                                </div>
                            </div>

                            <div className="right-column">
                                <div className="section">
                                    <div className="section-header">
                                        <h2 className="section-title">Security Alerts</h2>
                                        <span className="section-count">{alerts.length}</span>
                                    </div>
                                    <div className="alert-list">
                                        {alerts.length === 0 ? (
                                            <div className="empty-state">
                                                <div className="empty-state-text">No security threats detected</div>
                                            </div>
                                        ) : (
                                            alerts.map((alert, idx) => (
                                                <div key={idx} className={`alert-item ${alert.severity}`}>
                                                    <div className="alert-row">
                                                        <span className="alert-type">{alert.type}</span>
                                                        <span className={`severity-badge ${alert.severity}`}>{alert.severity}</span>
                                                    </div>
                                                    <div className="alert-description">{alert.description}</div>
                                                    <div className="alert-time">{new Date(alert.timestamp).toLocaleTimeString()}</div>
                                                </div>
                                            ))
                                        )}
                                    </div>
                                </div>
                            </div>
                        </div>
                    </>
                )}
            </div>
        </div>
    );
}

export default App;