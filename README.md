# 📌 Features
- Ping of the specified server at a specified interval.
- Detailed information about latency, packet loss, and availability.
- Saving logs to a file for later analysis.
- User-friendly dark interface with scrollable log window.
- Support for custom settings.

The simple version
## 🚀 Installation
1. Download the files:PingMonitor.ps1 server.ini RunPingMonitor.bat place the in a folder that is convenient for you, open the server.ini file and edit the ip= and port= fields.
2.Run the RunPingMonitor.bat file, a command prompt will open and you will receive information about your connection.

Server.ini
    [Server]
    
    ; The IP address of the ping server
    ip=8.8.8.8
    
    ; Server port (not used in this script if needed for other purposes)
    port=0000
    
    ; The interval between pings in seconds (for example, 2 seconds)
    interval=2
    
    ; Enable logging of results in a file
    ; true - logging is enabled
    ; false - logging is disabled
    enableLog=true
    
    ; Whether to show the percentage of packet loss in the output
    ; true - to show packet loss
    ; false - not to show packet loss
    showPacketLoss=true
    
    ; Whether to show the number of successful pings in the output
    ; true - show the successful ping counter
    ; false - do not show
    showSuccess=true
    
    ; Whether to show the running time of the script from the moment of launch
    ; true - show opening hours
    ; false - do not show
    showUptime=true
    
    ; Whether to show the current server status (Online/Offline)
    ; true - show the status
    ; false - do not show
    showStatus=true






