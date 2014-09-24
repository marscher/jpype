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
    $importable=python -c "import _jpype; print _jpype.isStarted()"
    if( -not $importable) {
       throw "Jpype module is not importable - fail"
    }
     
    nosetests test/jpypetest --all-modules --with-xunit 2>stderr.out
    $success = $?
    Write-Host "result code of nosetests:" $success
    if(-not(Test-Path $input)) {
        throw "fatal error during testsuite execution"
    }
    xslt_transform $input $stylesheet $output

    upload $output
    Push-AppveyorArtifact $input
    Push-AppveyorArtifact $output
    Push-AppveyorArtifact 'stderr.out'
    
    # return exit code of testsuite
    if ( -not $success) {
        throw "testsuite not successful"
    }
}

run