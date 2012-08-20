<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    <xsl:template match="/" xmlns:d="DAV:" xmlns:s="system:">
        <html>
            <head>
                <!-- <base href="http://attachix.de/" /> -->
                <link rel="stylesheet" type="text/css" href="/~static/css/folder.css"/>
                <link rel="stylesheet" type="text/css" href="/.custom/css/folder.css"/>
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
                                <xsl:if test="d:propstat/d:prop/d:getcontenttype">
                                    <xsl:choose>
                                        <xsl:when test="d:propstat/d:prop/s:image-thumbnail-small">
                                            <img width="200">
                                                <xsl:attribute name='src'><xsl:value-of select="d:propstat/d:prop/s:image-thumbnail-small"/></xsl:attribute>
                                            </img>
                                        </xsl:when>
                                        <xsl:when test="contains(d:propstat/d:prop/d:getcontenttype,'video/')">
                                            <a ><!-- On Click Embed the Flash Player -->
                                                <xsl:attribute name='href'>javascript:</xsl:attribute>
                                                <xsl:attribute name='onclick'>window.open('/~static/html/player.html?/.views/<xsl:value-of select="d:href"/>/flash.flv:/.views/<xsl:value-of select="d:href"/>/image.png'); return false</xsl:attribute>
                                                <img class="playable">
                                                    <xsl:attribute name='src'>/.views/<xsl:value-of select="d:href"/>/image.png</xsl:attribute>
                                                </img>
                                            </a>
                                        </xsl:when>
                                        <xsl:when test="contains(d:propstat/d:prop/d:getcontenttype,'audio/')">
                                            <a ><!-- On Click Embed the Flash Player -->
                                                <xsl:attribute name='href'>javascript:</xsl:attribute>
                                                <xsl:attribute name='onclick'>window.open('/~static/html/aplayer.html?/.views/<xsl:value-of select="d:href"/>/song.mp3:/.views/<xsl:value-of select="d:href"/>/image.png'); return false</xsl:attribute>
                                                <img src="/~static/img/audio.png" width="50" />
                                            </a>
                                        </xsl:when>
                                    </xsl:choose>
                                </xsl:if>

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
