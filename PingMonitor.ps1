# Функция для чтения ini файла (парсер очень простой)
function Parse-IniFile {
    param([string]$Path)

    if (-Not (Test-Path $Path)) {
        throw "INI file not found: $Path"
    }

    $ini = @{}
    $section = ""

    foreach ($line in Get-Content $Path) {
        $line = $line.Trim()
        if ($line -match '^\s*;') { continue } # пропускаем комментарии
        if ($line -match '^\[(.+)\]$') {
            $section = $matches[1]
            if (-not $ini.ContainsKey($section)) {
                $ini[$section] = @{}
            }
        } elseif ($line -match '^(.*?)=(.*)$') {
            $key = $matches[1].Trim()
            $value = $matches[2].Trim()
            if ($section) {
                $ini[$section][$key] = $value
            } else {
                $ini[$key] = $value
            }
        }
    }

    return $ini
}

try {
    # Устанавливаем корректную кодировку для вывода в консоль
    [Console]::OutputEncoding = [Text.UTF8Encoding]::new()

    $scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
    $iniPath = Join-Path $scriptDir "server.ini"

    $iniData = Parse-IniFile -Path $iniPath

    $server = $iniData["Server"]["ip"]

    if (-not $server) {
        Write-Host "Server IP not set in ini"
        exit
    }

    # Читаем интервал из ini, если не указан — ставим 10 сек по умолчанию
    $interval = $iniData["Server"]["interval"]
    if (-not $interval) {
        $interval = 10
    } else {
        if (-not [int]::TryParse($interval, [ref]$null)) {
            Write-Host "Warning: interval в server.ini не число. Используем 10."
            $interval = 10
        } else {
            $interval = [int]$interval
        }
    }

    # Читаем enableLog, по умолчанию true
    $enableLog = $iniData["Server"]["enableLog"]
    if (-not $enableLog) {
        $enableLog = $true
    } else {
        $enableLog = $enableLog.ToLower() -eq "true"
    }

    # Читаем showPacketLoss, по умолчанию true
    $showPacketLoss = $iniData["Server"]["showPacketLoss"]
    if (-not $showPacketLoss) {
        $showPacketLoss = $true
    } else {
        $showPacketLoss = $showPacketLoss.ToLower() -eq "true"
    }

    # Читаем showSuccess, по умолчанию true
    $showSuccess = $iniData["Server"]["showSuccess"]
    if (-not $showSuccess) {
        $showSuccess = $true
    } else {
        $showSuccess = $showSuccess.ToLower() -eq "true"
    }

    # Читаем showUptime, по умолчанию true
    $showUptime = $iniData["Server"]["showUptime"]
    if (-not $showUptime) {
        $showUptime = $true
    } else {
        $showUptime = $showUptime.ToLower() -eq "true"
    }

    # Читаем showStatus, по умолчанию true
    $showStatus = $iniData["Server"]["showStatus"]
    if (-not $showStatus) {
        $showStatus = $true
    } else {
        $showStatus = $showStatus.ToLower() -eq "true"
    }

    # Создаём имя для лога с датой и временем, если логирование включено
    if ($enableLog) {
        $timestampForFile = Get-Date -Format "yyyy-MM-dd_HH-mm-ss"
        $logPath = Join-Path $scriptDir "arma3_ping_log_$timestampForFile.txt"

        "Arma 3 Ping Monitor Log to $server" | Out-File -FilePath $logPath -Encoding UTF8
        "Timestamp`t`t`tResult" | Out-File -FilePath $logPath -Encoding UTF8 -Append
        "----------------------------------------" | Out-File -FilePath $logPath -Encoding UTF8 -Append
    }

    Write-Host ""
    Write-Host "Press 'P' to Pause/Resume, 'Q' to Quit." -ForegroundColor Yellow
    Write-Host ""

    $paused = $false

    # Новые счётчики
    $totalPings = 0
    $successPings = 0
    $failPings = 0
    $sumResponseTime = 0

    # Время запуска скрипта
    $startTime = Get-Date

    while ($true) {

        # Проверяем, была ли нажата клавиша
        if ([Console]::KeyAvailable) {
            $key = [Console]::ReadKey($true).Key
            switch ($key) {
                'P' {
                    $paused = -not $paused
                    if ($paused) {
                        Write-Host "[PAUSED] Press 'P' to Resume or 'Q' to Quit." -ForegroundColor DarkYellow
                    } else {
                        Write-Host "[RESUMED]" -ForegroundColor Green
                    }
                }
                'Q' {
                    Write-Host "Quitting..." -ForegroundColor Red
                    exit
                }
            }
        }
    
        if (-not $paused) {
            $totalPings++
            $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
            
            $pingReply = Test-Connection -ComputerName $server -Count 1 -ErrorAction SilentlyContinue

            # Время работы с начала запуска (TimeSpan)
            $uptime = (Get-Date) - $startTime
            # Форматируем время: часы:минуты:секунды
            $uptimeFormatted = "{0:00}h:{1:00}m:{2:00}s" -f $uptime.Hours, $uptime.Minutes, $uptime.Seconds

            if ($pingReply) {
                $successPings++
                $sumResponseTime += $pingReply.ResponseTime
                $avgResponseTime = [math]::Round($sumResponseTime / $successPings, 2)
                $lossPercent = 0
                $status = "Online"

                $message = "Ping to $server - Avg = ${avgResponseTime}ms"
                if ($showPacketLoss) {
                    $message += "; Packet Loss = ${lossPercent}%"
                }
                if ($showSuccess) {
                    $message += "; Success = $successPings/$totalPings"
                }
                if ($showUptime) {
                    $message += "; Uptime = $uptimeFormatted"
                }
                if ($showStatus) {
                    $message += "; Status = $status"
                }

                Write-Host $timestamp -NoNewline -ForegroundColor Cyan
                Write-Host "`t$message" -ForegroundColor Green
            } else {
                $failPings++
                $lossPercent = [math]::Round(($failPings / $totalPings) * 100, 2)
                $status = "Offline"

                $message = "Ping to $server failed or blocked"
                if ($showPacketLoss) {
                    $message += "; Packet Loss = ${lossPercent}%"
                }
                if ($showSuccess) {
                    $message += "; Fail = $failPings/$totalPings"
                }
                if ($showUptime) {
                    $message += "; Uptime = $uptimeFormatted"
                }
                if ($showStatus) {
                    $message += "; Status = $status"
                }

                Write-Host $timestamp -NoNewline -ForegroundColor Cyan
                Write-Host "`t$message" -ForegroundColor Red
            }
    
            if ($enableLog) {
                "$timestamp`t$message" | Out-File -FilePath $logPath -Encoding UTF8 -Append
            }
        }
    
        Start-Sleep -Seconds $interval
    }

} catch {
    Write-Host "Error: $_"
}
