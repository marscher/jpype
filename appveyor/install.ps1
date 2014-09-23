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


InstallNumpy() {
    trap [Exception]
    {
        Write-Host $_.Exception
        throw "install numpy failed"
    }

    # TODO: figure out: we do not need to define a python home since the installed pip defines install location already?

    # download numpy
    $url="http://www.mirrorservice.org/sites/ftp.sourceforge.net/pub/sourceforge/n/nu/numpy/NumPy/1.9.0/numpy-1.9.0-win32-superpack-python2.7.exe"
    $webclient = New-Object System.Net.WebClient
    $filepath = "C:\numpy.exe"
    $webclient.DownloadFile($url, $filepath)
    # convert installer to wheel
    RunCommand "pip" "install wheel"
    RunCommand "python" "-m wheel convert $filepath"
    # install wheel
    RunCommand "pip" "install *.whl"
}


function main () {
    #InstallAnt
    InstallPip $env:PYTHON
    InstallNumpy
    
    RunCommand "python" "-c \"import numpy\""
}

main
