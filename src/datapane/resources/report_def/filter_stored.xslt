<?xml version="1.0" encoding="utf-8" ?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0" xmlns:fn="urn:local:dp-report-functions" exclude-result-prefixes="fn">
  <xsl:output omit-xml-declaration="no" indent="yes" encoding="utf-8" method='xml' cdata-section-elements="Text"/>
  <xsl:strip-space elements="*"/>
  <xsl:param name="blocksquery"/>

  <!--  Match and copy across everything, i.e. id -->
  <xsl:template match="@* | node()">
    <xsl:copy>
      <xsl:apply-templates select="@* | node()"/>
    </xsl:copy>
  </xsl:template>

  <!--  Strip all comments-->
  <xsl:template match="comment()"/>

  <!-- Apply XPath filter and collect in a single Blocks element -->
  <xsl:template match="/Report/Main">
    <Main>
      <Blocks>
        <xsl:copy-of select="$blocksquery"/>
      </Blocks>
    </Main>
  </xsl:template>

</xsl:stylesheet>
