function xslt_transform($xml, $xsl, $output)
{
	trap [Exception]
	{
	    Write-Host $_.Exception;
	}
	
	$xslt = New-Object System.Xml.Xsl.XslCompiledTransform;
	$xslt.Load($xsl);
	$xslt.Transform($xml, $output);
}

function upload($file) {
    trap [Exception]
    {
        Write-Host $_.Exception;
    }

    $wc = New-Object 'System.Net.WebClient';
    $wc.UploadFile("https://ci.appveyor.com/api/testresults/xunit/$($env:APPVEYOR_JOB_ID)", $file); 
}

function run {
    $stylesheet = "C:/projects/jpype/test/transform_xunit_to_appveyor.xsl";
    $output = "C:/projects/jpype/test/transformed.xml"
    
    python testsuite.py --xml; $success = $?;
    
    $input = (Resolve-Path *.xml);

    xslt_transform $input $stylesheet $output
    
    Get-Content -path 'transformed.xml';
    
    exit $success
}

run