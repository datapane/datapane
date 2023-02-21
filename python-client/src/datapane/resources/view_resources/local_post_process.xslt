<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0"
                xmlns:fn="urn:local:dp-report-functions"
                exclude-result-prefixes="fn" extension-element-prefixes="fn">
  <xsl:output omit-xml-declaration="no" indent="no" encoding="utf-8"
              method='xml' cdata-section-elements="Text HTML Code Formula Embed Description"/>
  <xsl:strip-space elements="*"/>

  <!--  Match and copy across everything, i.e. id -->
  <xsl:template match="@* | node()">
    <xsl:copy>
      <xsl:apply-templates select="@* | node()"/>
    </xsl:copy>
  </xsl:template>

  <!--  Strip all comments-->
  <xsl:template match="comment()"/>

  <!-- Drop blocks if embedded -->
  <!-- Disabled for now as local report rendering handles Blocks -->
  <!--
  <xsl:template match="/View//Blocks">
    <xsl:choose>
      <xsl:when test="$embedded">
        <xsl:apply-templates/>
      </xsl:when>

      <xsl:otherwise>
        <xsl:copy>
          <xsl:apply-templates select="@* | node()"/>
        </xsl:copy>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>
  -->

  <!-- find/replace nested Views -> Group -->
  <!--
  <xsl:template match="/View//View">
    <Group valign="center" columns="1">
      <xsl:apply-templates/>
    </Group>
  </xsl:template>
  -->


</xsl:stylesheet>
