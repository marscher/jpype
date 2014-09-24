# Sample script to install Python and pip under Windows
# Authors: Olivier Grisel, Jonathan Helmus and Kyle Kastner
# License: CC0 1.0 Universal: http://creativecommons.org/publicdomain/zero/1.0/

$MINICONDA_URL = "http://repo.continuum.io/miniconda/"
$BASE_URL = "https://www.python.org/ftp/python/"
$GET_PIP_URL = "https://bootstrap.pypa.io/get-pip.py"
$GET_PIP_PATH = "C:\get-pip.py"


function RunCommand ($command, $command_args) {
    Write-Host $command $command_args
    Start-Process -FilePath $command -ArgumentList $command_args -Wait -Passthru
}

function InstallPip ($python_home) {
    $pip_path = $python_home + "\Scripts\pip.exe"
    $python_path = $python_home + "\python.exe"
    if (-not(Test-Path $pip_path)) {
        Write-Host "Installing pip..."
        $webclient = New-Object System.Net.WebClient
        $webclient.DownloadFile($GET_PIP_URL, $GET_PIP_PATH)
        Write-Host "Executing:" $python_path $GET_PIP_PATH
        Start-Process -FilePath "$python_path" -ArgumentList "$GET_PIP_PATH" -Wait -Passthru
    } else {
        Write-Host "pip already installed."
    }
}


function DownloadMiniconda ($python_version, $platform_suffix) {
    $webclient = New-Object System.Net.WebClient
    if ($python_version -eq "3.4") {
        $filename = "Miniconda3-3.6.0-Windows-" + $platform_suffix + ".exe"
    } else {
        $filename = "Miniconda-3.6.0-Windows-" + $platform_suffix + ".exe"
    }
    $url = $MINICONDA_URL + $filename

    $basedir = $pwd.Path + "\"
    $filepath = $basedir + $filename
    if (Test-Path $filename) {
        Write-Host "Reusing" $filepath
        return $filepath
    }

    # Download and retry up to 3 times in case of network transient errors.
    Write-Host "Downloading" $filename "from" $url
    $retry_attempts = 2
    for($i=0; $i -lt $retry_attempts; $i++){
        try {
            $webclient.DownloadFile($url, $filepath)
            break
        }
        Catch [Exception]{
            Start-Sleep 1
        }
   }
   if (Test-Path $filepath) {
       Write-Host "File saved at" $filepath
   } else {
       # Retry once to get the error message if any at the last try
       $webclient.DownloadFile($url, $filepath)
   }
   return $filepath
}


function InstallMiniconda ($python_version, $architecture, $python_home) {
    Write-Host "Installing Python" $python_version "for" $architecture "bit architecture to" $python_home
    if (Test-Path $python_home) {
        Write-Host $python_home "already exists, skipping."
        return $false
    }
    if ($architecture -eq "32") {
        $platform_suffix = "x86"
    } else {
        $platform_suffix = "x86_64"
    }
    $filepath = DownloadMiniconda $python_version $platform_suffix
    Write-Host "Installing" $filepath "to" $python_home
    $install_log = $python_home + ".log"
    $args = "/S /D=$python_home"
    Write-Host $filepath $args
    Start-Process -FilePath $filepath -ArgumentList $args -Wait -Passthru
    if (Test-Path $python_home) {
        Write-Host "Python $python_version ($architecture) installation complete"
    } else {
        Write-Host "Failed to install Python in $python_home"
        Get-Content -Path $install_log
        Exit 1
    }
}


function InstallMinicondaPip ($python_home) {
    $pip_path = $python_home + "\Scripts\pip.exe"
    $conda_path = $python_home + "\Scripts\conda.exe"
    if (-not(Test-Path $pip_path)) {
        Write-Host "Installing pip..."
        $args = "install --yes pip"
        Write-Host $conda_path $args
        Start-Process -FilePath "$conda_path" -ArgumentList $args -Wait -Passthru
    } else {
        Write-Host "pip already installed."
    }
}

function DownloadAnt() {
    $url = "http://www.us.apache.org/dist/ant/binaries/apache-ant-1.9.4-bin.zip"
    $webclient = New-Object System.Net.WebClient
    $filepath = "C:\ant.zip"
	
	if (Test-Path $filepath) {
        Write-Host "Reusing" $filepath
        return $filepath
    }
	
	# Download and retry up to 3 times in case of network transient errors.
    Write-Host "Downloading" $filename "from" $url
    $retry_attempts = 2
    for($i=0; $i -lt $retry_attempts; $i++){
        try {
            $webclient.DownloadFile($url, $filepath)
            break
        }
        Catch [Exception]{
            Start-Sleep 1
        }
   }
   if (Test-Path $filepath) {
       Write-Host "File saved at" $filepath
   } else {
       # Retry once to get the error message if any at the last try
       $webclient.DownloadFile($url, $filepath)
   }
   return $filepath
}

function InstallAnt() {
    trap [Exception]
    {
        Write-Host $_.Exception
        throw "install ant failed"
    }

    if (Test-Path $env:ANT_HOME) {
        Write-Host "ant already exists"
        return $false
    }

    $filepath = DownloadAnt
    # extract to C: (will result in something like C:\apache-ant-1.9.4
    pushd C:\
    7z x $filepath > $null
    popd
}

function InstallAntChocolatey() {
    trap [Exception]
    {
        Write-Host $_.Exception
        throw "install ant failed"
    }
    
    choco install ant
}

function main () {
    InstallAnt
    InstallMiniconda $env:PYTHON_VERSION $env:PYTHON_ARCH $env:PYTHON
    InstallMinicondaPip $env:PYTHON
}

main
