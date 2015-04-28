from pelican import signals
import html5lib

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

           if href in links:
               index = links.index(href) + 1
           else:
               links.append(href)
               index = len(links)

           sup = dom.createElement("sup")
           sup.setAttribute("class", "print")
           sup.appendChild(dom.createTextNode(prefix + str(index)))

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

