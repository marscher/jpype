<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
<!-- The "root" or "main" template -->
<xsl:key name="class" match="/testsuite/testcase/@classname" use="." />
<xsl:output method="xml" encoding="UTF-8" indent="yes" />

<xsl:template match="testsuite">

<assembly name="python">
<xsl:attribute name="total">
  <xsl:value-of select="@tests"></xsl:value-of>
</xsl:attribute> 

<xsl:attribute name="passed">
  <xsl:value-of select="@tests - @errors - @failures - @skip"></xsl:value-of>
</xsl:attribute> 

<xsl:attribute name="failed">
  <xsl:value-of select="@errors"></xsl:value-of>
</xsl:attribute> 

<xsl:attribute name="skipped">
  <xsl:value-of select="@skip"></xsl:value-of>
</xsl:attribute>

<!-- class names, only unique -->
<xsl:for-each select="/testsuite/testcase/@classname[generate-id()
                                       = generate-id(key('class',.)[1])]">
  <class>
    <xsl:variable name="className" select="." />
    <xsl:attribute name="name">
        <xsl:value-of select="."/>
    </xsl:attribute>
    
    <!-- select only those testcases, which match the current classname -->
    <xsl:for-each select="/testsuite/testcase[@classname=$className]">
    <!-- 
    The test node contains information about a single test execution.

Attribute   Introduced  Value
name    1.0     The display name of the test
type    1.0     The full type name of the class
method  1.0     The name of the method
result  1.0     One of "Pass", "Fail", or "Skip"
time    1.0     The time, in fractional seconds, spent running the test (not present for "Skip" results)


Child   Introduced  Value
<failure>   1.0     [0..1] Present if the test result is "Fail"
<reason>    1.0     [0..1] Present if the test result is "Skip"
<traits>    1.0     [0..1] Present if the test has any trait metadata
<output>    1.1     [0..1] Contains any text written to Console.Out or Console.Error (in CDATA until 1.2)  -->
	    <test>
	        <xsl:attribute name="name">
	            <xsl:value-of select="@name"></xsl:value-of>
	        </xsl:attribute>
	        
	        <xsl:attribute name="time">
                <xsl:value-of select="@time"></xsl:value-of>
            </xsl:attribute>
	        
	        <xsl:variable name="result">
	           <xsl:choose>
                    <xsl:when test="error">Fail</xsl:when>
                    <xsl:when test="skipped">Skip</xsl:when>
                    <xsl:otherwise>Pass</xsl:otherwise>
               </xsl:choose>
	        </xsl:variable>
	        <xsl:attribute name="result">
		       <xsl:value-of select="$result"></xsl:value-of>
	        </xsl:attribute>
	        
	        <xsl:choose>
                    <xsl:when test="error">
	                    <failure>
	                        <xsl:attribute name="exception-type">
	                            <xsl:value-of select="error/@type"></xsl:value-of>
	                        </xsl:attribute>
	                        <message>
	                           <xsl:value-of select="error"></xsl:value-of>
	                        </message>
	                    </failure>
                    </xsl:when>
                    <xsl:when test="skipped">
	                    <reason>
	                        <xsl:value-of select="skipped/@message"></xsl:value-of>
	                    </reason>
                    </xsl:when>
               </xsl:choose>
               
               <xsl:choose>
               <xsl:when test="system-out">
                    <output><xsl:value-of select="system-out/."/></output>
               </xsl:when>
               </xsl:choose>
	    </test>
    </xsl:for-each>
 </class>
</xsl:for-each>

</assembly>

</xsl:template>
</xsl:stylesheet>
