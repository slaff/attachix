<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    <xsl:template match="/" xmlns:d="DAV:">
        <html>
            <head>
                <link rel="stylesheet" type="text/css" href="/~static/css/folder.css"/>
                <!--
                   XLST can accept external JavaScripts and render them.
                   The code below demostrates how.
                -->
                <script type="text/javascript" src="/~static/js/redir.js">
                    <xsl:comment></xsl:comment>
                </script>
            </head>
            <body>
                <table border="1">
                    <tr class="header">
                        <th align="left">Name(<a class="asc"><xsl:attribute name="href">?_sort={DAV:}displayname,asc</xsl:attribute>asc</a> | <a class="asc"><xsl:attribute name="href">?_sort={DAV:}displayname,desc</xsl:attribute>desc</a>)</th>
                        <th align="left">Size(<a class="asc"><xsl:attribute name="href">?_sort={DAV:}getcontentlength,asc</xsl:attribute>asc</a> | <a class="asc"><xsl:attribute name="href">?_sort={DAV:}getcontentlength,desc</xsl:attribute>desc</a>)</th>
                        <th align="left">Lastmodified(<a class="asc"><xsl:attribute name="href">?_sort={DAV:}getlastmodified,asc</xsl:attribute>asc</a> | <a class="asc"><xsl:attribute name="href">?_sort={DAV:}getlastmodified,desc</xsl:attribute>desc</a>)</th>
                    </tr>
                    <xsl:for-each select="d:multistatus/d:response">
                        <xsl:sort select="d:propstat/d:prop/d:resourcetype"/>
                        <tr>
                            <td>
                                <!-- Case based on the mime type -->
                                <a>
                                    <xsl:attribute name='href'>
                                        <xsl:value-of select="d:href"/>
                                    </xsl:attribute>
                                    <xsl:attribute name='type'>
                                        <xsl:choose>
                                            <xsl:when test="d:propstat/d:prop/d:resourcetype/d:collection">folder</xsl:when>
                                            <xsl:otherwise>file</xsl:otherwise>
                                        </xsl:choose>
                                    </xsl:attribute>
                                    <xsl:if test="d:propstat/d:prop/d:displayname">
                                        <xsl:value-of select="d:propstat/d:prop/d:displayname"/>
                                    </xsl:if>
                                    <xsl:if test="not(d:propstat/d:prop/d:displayname)">
                                        <xsl:value-of select="d:href"/>
                                    </xsl:if>
                                </a>

                            </td>
                            <td>
                                <xsl:value-of select="d:propstat/d:prop/d:getcontentlength"/>
                            </td>
                            <td>
                                <xsl:value-of select="d:propstat/d:prop/d:getlastmodified"/>
                            </td>
                        </tr>
                    </xsl:for-each>
                    <tr>
                        <td align="right" colspan="3">
                              <form enctype="multipart/form-data" method="post">
                                <input type="file" multiple="true" name="file[]"/>
                                <input type="submit" value=" Upload "/>
                              </form>
                        </td>
                    </tr>
                    <tr>
                        <td align="right" colspan="2">Size:
                            <xsl:value-of select="sum(d:multistatus/d:response/d:propstat/d:prop/d:getcontentlength)"/> bytes
                        </td>
                        <td align="right">Total:
                            <xsl:value-of select="count(d:multistatus/d:response)"/>
                        </td>
                        
                    </tr>
                </table>
            </body>
        </html>
    </xsl:template>
</xsl:stylesheet>
