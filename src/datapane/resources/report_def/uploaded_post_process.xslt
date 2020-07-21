<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0"
                xmlns:fn="urn:local:dp-report-functions"
                exclude-result-prefixes="fn" extension-element-prefixes="fn">
  <xsl:output omit-xml-declaration="no" indent="no" encoding="utf-8"
              method='xml' cdata-section-elements="Text"/>
  <xsl:strip-space elements="*"/>

  <!--  Match and copy across everything, i.e. id -->
  <xsl:template match="@* | node()">
    <xsl:copy>
      <xsl:apply-templates select="@* | node()"/>
    </xsl:copy>
  </xsl:template>

  <!--  Strip all comments-->
  <xsl:template match="comment()"/>

  <!--  Drop wrapped blocks -->
  <xsl:template match="/Report/Main//Wrapped">
    <xsl:apply-templates/>
  </xsl:template>

</xsl:stylesheet>
