# LINA Features Guide

## 🎯 Overview
LINA (Linux Intelligence Network Assistant) is an AI-powered cybersecurity assistant with **82+ tools** and multiple features.

---

## 🛠️ Available Tools (82 Total)

### Network Scanning & Discovery
- **nmap** - Network scanning, port scanning, OS detection
- **masscan** - Fast Internet-scale port scanner
- **rustscan** - Modern, fast port scanner
- **netcat** - Network utility for TCP/UDP connections
- **arp-scan** - ARP scanning tool

### Web Security & Scanning
- **gobuster** - Directory/file brute-forcing
- **feroxbuster** - Fast recursive content discovery
- **dirb** - Web content scanner
- **dirbuster** - Multi-threaded directory brute-forcing
- **ffuf** - Fast web fuzzer
- **nikto** - Web server vulnerability scanner
- **wpscan** - WordPress security scanner
- **sqlmap** - Automatic SQL injection tool
- **curl** - HTTP request tool
- **wget** - File download utility

### Password & Authentication
- **hydra** - Network logon cracker
- **john** - Password cracker
- **hashcat** - Advanced password recovery

### Exploitation & Payloads
- **msfvenom** - Metasploit payload generator
- **searchsploit** - Exploit-DB search tool
- **metasploit** - Penetration testing framework

### DNS & Domain Tools
- **dig** - DNS interrogation tool
- **nslookup** - DNS lookup utility
- **whois** - Domain registration lookup
- **sublist3r** - Subdomain enumeration

### Forensics & Analysis
- **volatility** - Memory analysis framework
- **autopsy** - Digital forensics platform
- **wireshark** - Network protocol analyzer
- **tcpdump** - Packet analyzer
- **binwalk** - Firmware analysis tool

### And 60+ more tools! See full list in the Tools page.

---

## 🚀 How to Use Tools

### Method 1: Natural Language (Recommended)
Just ask LINA what you want to do:
- "scan localhost with nmap"
- "brute force directories on example.com"
- "check if sqlmap is installed"
- "explain how nmap works"
- "find subdomains of example.com"

### Method 2: Direct Tool Requests
- "use nmap to scan 192.168.1.1"
- "run gobuster on https://target.com"
- "execute sqlmap against target.com"

### Method 3: View All Tools
Click the **"Tools"** button in the chat header to see all 82 tools with:
- Tool descriptions
- Installation status
- Categories
- Risk levels

---

## 🎨 Features

### 1. **Auto-Execute Commands**
When LINA generates a command, it automatically executes it and shows results in the terminal (right side).

### 2. **Split-Screen Interface**
- **Left**: Chat interface for interacting with LINA
- **Right**: Terminal output showing command execution results

### 3. **Risk Assessment**
Every command is automatically assessed for safety:
- Risk levels: SAFE, LOW, MEDIUM, HIGH, RISKY, CRITICAL, BLOCKED
- Database pattern matching
- AI-powered risk analysis

### 4. **Tool Intelligence**
LINA uses a "Librarian & Scholar" system:
- **Librarian**: Selects the right tool for your task
- **Scholar**: Composes the perfect command syntax

### 5. **Session Management**
- Each role (Student/Forensic Expert/Penetration Tester) has its own session
- Command history tracking
- Tool usage analytics

### 6. **Analytics Dashboard**
View your session statistics:
- Commands executed
- Tools used
- Session duration
- Learning insights

---

## 💡 Example Commands

### Network Scanning
- "scan ports on localhost"
- "find all hosts on my network"
- "check if port 80 is open on example.com"

### Web Security
- "scan example.com for vulnerabilities"
- "find directories on https://target.com"
- "test for SQL injection on target.com"

### System Operations
- "list all running processes"
- "check disk space"
- "show network connections"

### Learning & Explanations
- "explain how nmap works"
- "what is SQL injection?"
- "how do I use gobuster?"

### Multi-Step Plans
- "create a plan to test website security"
- "plan a network reconnaissance workflow"

---

## 📊 Roles

### Student
- More explanations and guidance
- Educational focus
- Safe defaults

### Forensic Expert
- Digital forensics tools
- Memory analysis
- Evidence collection

### Penetration Tester
- Full offensive security toolkit
- Advanced exploitation
- All tools available

---

## 🔍 Quick Tips

1. **Ask naturally** - Just describe what you want to do
2. **Be specific** - Include targets, IPs, or domains
3. **Use "explain"** - Learn how tools work
4. **Check tools** - Click "Tools" button to browse all available tools
5. **View analytics** - Track your usage and progress

---

## ⚠️ Important Notes

- **Tool Installation**: Many tools need to be installed on your system
- **macOS**: Use `brew install <tool-name>` to install tools
- **Linux**: Use `apt install <tool-name>` or `yum install <tool-name>`
- **Commands execute automatically** - Be careful with destructive commands!

---

## 🎓 Getting Started

1. Select your role
2. Ask LINA to do something (e.g., "scan localhost")
3. Watch as it generates and executes commands
4. View results in the terminal
5. Explore the Tools page to see all available tools

Happy hacking! 🚀

