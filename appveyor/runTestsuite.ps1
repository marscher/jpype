function xslt_transform($xml, $xsl, $output)
{
	trap [Exception]
	{
	    Write-Host $_.Exception
	}
	
	$xslt = New-Object System.Xml.Xsl.XslCompiledTransform
	$xslt.Load($xsl)
	$xslt.Transform($xml, $output)
}

function upload($file) {
    trap [Exception]
    {
        Write-Host $_.Exception
    }

    $wc = New-Object 'System.Net.WebClient'
    $wc.UploadFile("https://ci.appveyor.com/api/testresults/xunit/$($env:APPVEYOR_JOB_ID)", $file)
}

function run {
    cd $env:APPVEYOR_BUILD_FOLDER
    $stylesheet =  "test/transform_xunit_to_appveyor.xsl"
    $input = "nosetests.xml"
    $output = "test/transformed.xml"
    $stdout = "output.txt"
    python -c "import _jpype"
    if(-not $?) {
       throw "Jpype module is not importable - fail"
    }
     
    nosetests test/jpypetest --all-modules --with-xunit --verbose 1>$stdout 2>&1
    $success = $?
    Push-AppveyorArtifact $stdout
    
    if(-not(Test-Path $input)) {
        throw "fatal error during testsuite execution. Nose didnt succeed in writing output"
    }
    xslt_transform $input $stylesheet $output

    upload $output
    Push-AppveyorArtifact $input
    Push-AppveyorArtifact $output
    
    # return exit code of testsuite
    if ( -not $success) {
        throw "testsuite not successful"
    }
}

run