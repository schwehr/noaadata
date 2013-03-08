<?xml version="1.0" encoding="ISO-8859-1"?>

<!-- Author: Kurt Schwehr -->
<!-- $Date: 2006-12-21 11:15:12 -0500 (Thu, 21 Dec 2006) $ -->

<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

  <xsl:template match="/">
    <html>
      <title>AIS Message Definition - Human Readable Form</title>
      <body>
	<h1>AIS Message Definitions</h1>
	<!-- Maybe this should be a table too? -->
	<ul>
	  <xsl:for-each select="ais-binary-message/message">
	    <li>
	      <a href="{concat('#',@name)}"><xsl:value-of select="@name"/></a>
	      (<xsl:value-of select="@dac"/>:<xsl:value-of select="@fid"/>:<xsl:value-of select="@efid"/>): 
	      <xsl:value-of select="description"/>
	    </li>
	  </xsl:for-each>
	</ul>



	<xsl:for-each select="ais-binary-message/message">
	  <a name="{concat('',@name)}">
	  <h2>AIS Message: <xsl:value-of select="@name"/>
	    (<xsl:value-of select="@dac"/>:<xsl:value-of select="@fid"/>:<xsl:value-of select="@efid"/>)
	  </h2>
	  </a>
	  <h3>Description:</h3><p><xsl:value-of select="description"/></p>
	  <xsl:for-each select="note">
	    <p><b>Note:</b>  <xsl:value-of select="."/></p>
	  </xsl:for-each>

	  <!-- FIX: make the see alsos be active links -->
	  <xsl:for-each select="see-also">
	    <p><b>See Also:</b>  <xsl:value-of select="."/></p>
	  </xsl:for-each>

	  <table border="1">
	    <tr bgcolor="#9acd32">
	      <th align="left">Name</th>
	      <th align="left">NumberOfBits</th>
	      <th align="left">ArrayLength</th>
	      <th align="left">Type</th>
	      <th align="left">Units</th>
	      <th align="left">Description</th>
	    </tr>
	    <xsl:for-each select="field">
	      <tr>
		<td><xsl:value-of select="@name"/></td>
		<td><xsl:value-of select="@numberofbits"/></td>
		<td><xsl:value-of select="@arraylength"/></td>
		<td><xsl:value-of select="@type"/></td>
		<td><xsl:value-of select="units"/></td>
		<td>
		  <xsl:value-of select="description"/>
		  <xsl:for-each select="lookuptable/entry">
		    <br/>
		    <b><xsl:value-of select="@key"/></b>: <xsl:value-of select="."/>
		  </xsl:for-each>

		</td>
	      </tr>
	    </xsl:for-each>
	  </table>
	</xsl:for-each>
      </body>
    </html>
  </xsl:template>

</xsl:stylesheet>
