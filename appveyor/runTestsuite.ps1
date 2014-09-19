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
    
    nosetests test/jpypetest --all-modules --with-xunit
    $success = $?;
    
    $input = "C:/projects/jpype/nosetests.xml";

    xslt_transform $input $stylesheet $output

    upload $output
    
    # return exit code of testsuite
    exit $success
}

run