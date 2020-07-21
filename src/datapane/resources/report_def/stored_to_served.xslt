<?xml version="1.0" encoding="utf-8" ?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0" xmlns:fn="urn:local:dp-report-functions" exclude-result-prefixes="fn">
  <xsl:output omit-xml-declaration="no" indent="yes" encoding="utf-8" method='xml' cdata-section-elements="Text"/>
  <xsl:strip-space elements="*"/>

  <!--  Match and copy across everything, i.e. id -->
  <xsl:template match="@* | node()">
    <xsl:copy>
      <xsl:apply-templates select="@* | node()"/>
    </xsl:copy>
  </xsl:template>

  <!--  Strip all comments-->
  <xsl:template match="comment()"/>

  <!--  Modify cas-referencing blocks, adding signed src and export urls -->
  <xsl:template match="/Report/Main//*[@src][starts-with(@src, 'cas://')]">
    <xsl:copy>
      <!-- copy all attributed, overridding src -->
      <xsl:copy-of select="@*"/>
      <xsl:attribute name="src"><xsl:value-of select="fn:add_signed_url(string(@src))"/></xsl:attribute>

      <xsl:if test="@preview">
        <xsl:attribute name="preview"><xsl:value-of select="fn:add_signed_url(string(@preview))"/></xsl:attribute>
      </xsl:if>

      <xsl:attribute name="export_url"><xsl:value-of select="fn:add_export_url(string(@src))"/></xsl:attribute>
      <!-- recurse into subnodes -->
      <xsl:apply-templates/>
    </xsl:copy>
  </xsl:template>

  <!--  Drop Nested blocks
    TODO - change to remove main and just have top-level blocks ?
    No, removes ability to add other blocks that are differentiated from <Blocks>
  -->
  <xsl:template match="/Report/Main//Blocks">
    <xsl:apply-templates/>
  </xsl:template>

</xsl:stylesheet>
