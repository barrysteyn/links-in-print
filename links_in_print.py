from pelican import signals
import re
import html5lib

RAW_FOOTNOTE_CONTAINERS = ["code"]

def getText(node, recursive = False):
    """Get all the text associated with this node.
       With recursive == True, all text from child nodes is retrieved."""
    L = ['']
    for n in node.childNodes:
        if n.nodeType in (node.TEXT_NODE, node.CDATA_SECTION_NODE):
            L.append(n.data)
        else:
            if not recursive:
                return None
        L.append(getText(n) )
    return ''.join(L)

def parse_for_links(article_generator):
    prefix = 'L'

    for article in article_generator.articles:
        links = []
        parser = html5lib.HTMLParser(tree=html5lib.getTreeBuilder("dom"))
        dom = parser.parse(article._content)

        for link in dom.getElementsByTagName("a"):
           href = link.getAttribute('href')

           if len(href) == 0 or href[0] == '#':
               continue  # do not print internal links

           links.append(href)
           sup = dom.createElement("sup")
           sup.setAttribute("class", "print")
           sup.appendChild(dom.createTextNode(prefix + str(len(links))))

           if link.nextSibling:
               link.parentNode.insertBefore(sup, link.nextSibling)
           else:
               link.parentNode.appendChild(sup)


        if links == []:
            continue

        # Links Title
        links_title = dom.createElement("h2")
        links_title.setAttribute("class", "print")
        links_title.appendChild(dom.createTextNode("Links"))
        dom.getElementsByTagName("body")[0].appendChild(links_title)

        # Actual Links
        links_div = dom.createElement("div")
        links_div.setAttribute("class", "print")
        link_list = dom.createElement("ol")
        link_list.setAttribute("class", "print-links")
        for link in links:
            li = dom.createElement("li")
            li.appendChild(dom.createTextNode(link))
            link_list.appendChild(li)

        links_div.appendChild(link_list)
        dom.getElementsByTagName("body")[0].appendChild(links_div)

        # Produce the output
        s = html5lib.serializer.htmlserializer.HTMLSerializer(omit_optional_tags=False, quote_attr_values=True)
        output_generator = s.serialize(html5lib.treewalkers.getTreeWalker("dom")(dom.getElementsByTagName("body")[0]))
        article._content = "".join(list(output_generator)).replace("<body>", "").replace("</body>", "")

def register():
    signals.article_generator_finalized.connect(parse_for_links)

