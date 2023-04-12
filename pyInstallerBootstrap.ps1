if ((Get-Command python -ErrorAction SilentlyContinue) -and (Get-Command python).CommandType -eq "Application") {
    Remove-Item $env:USERPROFILE\AppData\Local\Microsoft\WindowsApps\python*.exe
}

$global:ProgressPreference = 'SilentlyContinue'
$pythonCommand = Get-Command python -ErrorAction SilentlyContinue
if (-not $pythonCommand) {
    Write-Host "Python is not installed. Installing Python..."
    $url = "https://www.python.org/ftp/python/3.10.6/python-3.10.6-amd64.exe"
    $localPath = "C:\vagrant\python-3.10.6-amd64.exe"

    if (-not (Test-Path -Path $localPath)) {
        Invoke-WebRequest -Uri $url -UseBasicParsing -OutFile $localPath
    } else {
        Write-Host "Not redownloading. File already exists at $localPath"
    }

    & $localPath /quiet InstallAllUsers=1 PrependPath=1
    $newPythonPath = "$env:ProgramFiles\Python310"
    $newPythonScriptsPath = "$env:ProgramFiles\Python310\Scripts"

    $env:Path += ";$newPythonPath;$newPythonScriptsPath"
    # Wait for 10 seconds before checking for Python installation
    Start-Sleep -Seconds 10
} elseif ($pythonCommand.CommandType -eq "Application") {
    Write-Host "Python is already installed."
}



# Wait for Python installation to complete
$pythonExePath = "$env:ProgramFiles\Python310\python.exe"
$timeout = 300
$elapsed = 0
while (-not (Test-Path $pythonExePath) -and $elapsed -lt $timeout) {
    Start-Sleep -Seconds 1
    $elapsed += 1
}

if ($elapsed -eq $timeout) {
    Write-Host "Python installation timed out after $timeout seconds."
    exit 1
}

# Wait for pip to become available
$pipTimeout = 60
$pipElapsed = 0
while (-not (& $pythonExePath -m pip --version 2> $null) -and $pipElapsed -lt $pipTimeout) {
    Start-Sleep -Seconds 1
    $pipElapsed += 1
}

if ($pipElapsed -eq $pipTimeout) {
    Write-Host "Pip not available after $pipTimeout seconds."
    exit 1
}

if (-not (& $pythonExePath -m pip list | Select-String -Pattern "^pyinstaller\s")) {
    Write-Host "PyInstaller is not installed. Installing PyInstaller..."
    # Install pyinstaller using the full path of the Python executable
    & $pythonExePath -m pip install pyinstaller
} else {
    Write-Host "PyInstaller is already installed."
}
