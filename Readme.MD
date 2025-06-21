# 🍓 Raspberry Pi Ultra Monitor

<div align="center">

![Raspberry Pi Ultra Monitor](https://img.shields.io/badge/Raspberry%20Pi-Ultra%20Monitor-ff006e?style=for-the-badge&logo=raspberry-pi&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.7+-00f5ff?style=for-the-badge&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-2.0+-8338ec?style=for-the-badge&logo=flask&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-06ffa5?style=for-the-badge)

**A stunning, real-time web-based system monitoring dashboard for Raspberry Pi**

*Transform your Pi monitoring experience with this ultra-modern, responsive interface*

[🚀 Quick Start](#-quick-start) • [✨ Features](#-features) • [📸 Screenshots](#-screenshots) • [🛠️ Installation](#️-installation) • [📱 Usage](#-usage) • [🤝 Contributing](#-contributing)

</div>

---

## 🌟 Overview

Raspberry Pi Ultra Monitor is a beautiful, real-time web-based dashboard that provides comprehensive system monitoring for your Raspberry Pi. Built with Flask and featuring a stunning cyberpunk-inspired UI with glassmorphism effects, it offers professional-grade monitoring in an incredibly user-friendly package.

Perfect for headless Raspberry Pi setups, this monitor can be accessed from any device on your network through a modern web browser.

## ✨ Features

### 🎨 **Ultra-Modern UI**
- **Glassmorphism design** with backdrop blur effects
- **Cyberpunk color palette** with neon accents
- **Smooth animations** and hover effects
- **Responsive layout** - works on desktop, tablet, and mobile
- **Dark theme** optimized for extended viewing

### 📊 **Comprehensive Monitoring**
- **🔥 CPU Monitoring**
  - Real-time usage percentage
  - Per-core utilization display
  - CPU frequency information
  - Temperature monitoring with status indicators

- **💾 Memory Management**
  - RAM usage with detailed breakdown
  - Swap memory information
  - Available vs. used memory visualization
  - Memory pressure indicators

- **💽 Storage Analytics**
  - Disk usage for all mounted partitions
  - Filesystem type identification
  - Free space calculations
  - Visual usage bars with color coding

- **🌐 Network Activity**
  - Bytes sent/received statistics
  - Packet transfer counts
  - Network interface details with IP addresses
  - Real-time network throughput

- **⚡ Process Management**
  - Top 15 processes by CPU usage
  - Memory consumption per process
  - Process status monitoring
  - User identification for each process

- **🏠 System Information**
  - Raspberry Pi model detection
  - Operating system details
  - System uptime tracking
  - Boot time information

### 🚀 **Performance Features**
- **Real-time updates** every 2 seconds
- **Zero-latency interface** with smooth transitions
- **Lightweight backend** optimized for Pi hardware
- **Auto-refresh capabilities** with manual refresh option (Ctrl+R)
- **Error resilience** with graceful degradation

## 📸 Screenshots

### Dashboard Overview
*A sleek, comprehensive view of all system metrics*

### Mobile Responsive
*Full functionality on phones and tablets*

### Real-time Updates
*Live monitoring with smooth animations*

## 🛠️ Installation

### Prerequisites
- Raspberry Pi (any model with network connectivity)
- Python 3.7 or higher
- Internet connection for initial setup

### Quick Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/raspberry-pi-ultra-monitor.git
cd raspberry-pi-ultra-monitor

# Install dependencies
pip install flask psutil

# Make executable
chmod +x clean_monitor.py

# Run the monitor
python3 clean_monitor.py
```

### Alternative Installation

```bash
# Install dependencies manually
pip install -r requirements.txt

# Or install individually
pip install flask>=2.0.0 psutil>=5.8.0
```

## 📱 Usage

### Starting the Monitor

```bash
python3 clean_monitor.py
```

You'll see output like:
```
🍓 Raspberry Pi Ultra Monitor Starting...
==================================================
📱 Local Access:     http://localhost:8080
🌐 Network Access:   http://YOUR_PI_IP:8080
🔄 Auto-refresh:     Every 2 seconds
❌ Stop server:      Ctrl+C
==================================================
```

### Accessing the Dashboard

**Local Access:**
```
http://localhost:8080
```

**Network Access:**
```
http://YOUR_PI_IP:8080
```

**Find your Pi's IP address:**
```bash
hostname -I
```

### Keyboard Shortcuts
- **Ctrl+R** - Manual refresh
- **Ctrl+C** - Stop the server (in terminal)

## ⚙️ Configuration

### Running as a System Service

Create a systemd service for automatic startup:

```bash
# Create service file
sudo nano /etc/systemd/system/rpi-monitor.service
```

Add the following content:
```ini
[Unit]
Description=Raspberry Pi Ultra Monitor
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/raspberry-pi-ultra-monitor
ExecStart=/usr/bin/python3 /home/pi/raspberry-pi-ultra-monitor/clean_monitor.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Enable and start the service:
```bash
sudo systemctl daemon-reload
sudo systemctl enable rpi-monitor.service
sudo systemctl start rpi-monitor.service

# Check status
sudo systemctl status rpi-monitor.service
```

### Customizing Port

To change the default port (8080), modify the last line in `clean_monitor.py`:

```python
app.run(host='0.0.0.0', port=YOUR_PORT, debug=False)
```

### Security Considerations

For production use, consider:
- Adding authentication
- Using HTTPS with SSL certificates
- Implementing rate limiting
- Running behind a reverse proxy

## 🏗️ Architecture

### Backend (Python/Flask)
- **Flask web framework** for HTTP server
- **psutil library** for system metrics
- **Threading** for background monitoring
- **JSON API** for real-time data exchange

### Frontend (HTML/CSS/JavaScript)
- **Vanilla JavaScript** for real-time updates
- **CSS Grid/Flexbox** for responsive layout
- **CSS Custom Properties** for theming
- **Font Awesome icons** for visual elements

### Data Flow
```
System Metrics → psutil → Python Processing → Flask API → JSON → JavaScript → DOM Updates → UI
```

## 🔧 Development

### Project Structure
```
raspberry-pi-ultra-monitor/
├── clean_monitor.py          # Main application file
├── requirements.txt          # Python dependencies
├── README.md                # This file
├── LICENSE                  # MIT License
└── screenshots/             # UI screenshots
    ├── dashboard.png
    ├── mobile.png
    └── realtime.png
```

### Adding New Metrics

1. **Backend**: Add metric collection in `RPiMonitor` class
2. **API**: Update the data dictionary in `update_data()`
3. **Frontend**: Add UI elements and JavaScript update logic

Example:
```python
def get_new_metric(self):
    """Get new system metric"""
    return {"value": "some_data"}

# Add to update_data():
self.data['new_metric'] = self.get_new_metric()
```

### Contributing to Development

```bash
# Fork the repository
git clone https://github.com/yourusername/raspberry-pi-ultra-monitor.git

# Create feature branch
git checkout -b feature/new-metric

# Make changes and commit
git commit -m "Add new metric monitoring"

# Push and create pull request
git push origin feature/new-metric
```

## 🚨 Troubleshooting

### Common Issues

**Port Already in Use:**
```bash
# Find process using port 8080
sudo lsof -i :8080

# Kill the process
sudo kill -9 PID
```

**Permission Denied for Temperature:**
```bash
# Add user to required groups
sudo usermod -a -G gpio,i2c pi
```

**Module Not Found:**
```bash
# Ensure virtual environment is activated
source venv/bin/activate

# Reinstall dependencies
pip install --upgrade -r requirements.txt
```

**Can't Access from Network:**
```bash
# Check firewall settings
sudo ufw status

# Allow port (if using UFW)
sudo ufw allow 8080
```

### Performance Optimization

For better performance on older Pi models:
- Increase update interval in JavaScript (change `2000` to `5000` for 5-second updates)
- Reduce the number of processes shown
- Disable animations in CSS

## 📊 System Requirements

### Minimum Requirements
- **Raspberry Pi Zero W** or higher
- **512 MB RAM** (1 GB recommended)
- **Python 3.7+**
- **Network connectivity**

### Recommended Setup
- **Raspberry Pi 3B+** or higher
- **1 GB RAM** or more
- **Fast SD Card** (Class 10 or better)
- **Stable network connection**

### Tested Platforms
- ✅ Raspberry Pi 4B (4GB/8GB)
- ✅ Raspberry Pi 3B+
- ✅ Raspberry Pi 3B
- ✅ Raspberry Pi Zero 2W
- ⚠️ Raspberry Pi Zero W (limited performance)

## 🤝 Contributing

We welcome contributions! Here's how you can help:

### Types of Contributions
- 🐛 **Bug reports** and fixes
- ✨ **New features** and enhancements
- 📚 **Documentation** improvements
- 🎨 **UI/UX** enhancements
- 🧪 **Testing** on different Pi models

### Contributing Guidelines

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

### Code Style
- Follow **PEP 8** for Python code
- Use **meaningful variable names**
- Add **comments** for complex logic
- Write **docstrings** for functions
- Keep **functions focused** and small

### Reporting Issues
Please include:
- Raspberry Pi model and OS version
- Python version
- Error messages and logs
- Steps to reproduce the issue

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

```
MIT License

Copyright (c) 2024 Raspberry Pi Ultra Monitor

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
```

## 🙏 Acknowledgments

- **Raspberry Pi Foundation** for creating amazing hardware
- **Flask** community for the excellent web framework
- **psutil** developers for comprehensive system monitoring
- **Font Awesome** for beautiful icons
- **Open source community** for inspiration and support

## 📞 Support

### Getting Help
- 📖 **Documentation**: Check this README and inline comments
- 🐛 **Issues**: [GitHub Issues](https://github.com/yourusername/raspberry-pi-ultra-monitor/issues)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/yourusername/raspberry-pi-ultra-monitor/discussions)

### Commercial Support
For commercial deployments or custom features, please contact:
- 📧 Email: your.email@example.com
- 💼 LinkedIn: [Your Profile](https://linkedin.com/in/yourprofile)

---

<div align="center">

**Made with ❤️ for the Raspberry Pi community**

⭐ **Star this repo** if you find it useful!

[Report Bug](https://github.com/yourusername/raspberry-pi-ultra-monitor/issues) • [Request Feature](https://github.com/yourusername/raspberry-pi-ultra-monitor/issues) • [Contribute](https://github.com/yourusername/raspberry-pi-ultra-monitor/blob/main/CONTRIBUTING.md)

</div>