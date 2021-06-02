import markdown
from markdown import extensions
from lxml import etree
import re


def get_html(mdfile):   

    with open(mdfile, 'r', encoding='utf-8') as f:
        text = f.readlines()
    md = markdown.Markdown(extensions=['meta'], output_format='html5')
    html = md.convert(''.join(text))
    meta = md.Meta

    for line in text:
        result = re.search('^\s{0,3}#{1}\s(.*)', line)
        if result:
            meta['title'] = result.group(1).strip()
            break

    if 'tags' in meta.keys():
        meta['tags'] = [x.strip() for x in meta['tags'][0].split(',')]
    else:
        raise Exception('Error: no tags metadata in {}'.format(mdfile))
    if 'title' not in meta.keys():
        raise Exception('Error: no title in {}'.format(mdfile))

    return html, meta


def get_display_html(mdfile):

    html, meta = get_html(mdfile)
    pos = html.find('</h1>')
    if pos > 0 and len(meta['tags']) > 0:
        pos += 5
        tags_line = ''
        for tag in meta['tags']:
            tags_line = tags_line  + ' ' + '<a class="tag" href="/tag/{0}">#{0}</a>'.format(tag)

        display_html = html[:pos] + '<div class="tags">' + tags_line + "</div>" + html[pos:] + '<br/><br/><br/><br/>'
    else:
        display_html = html
    
    return display_html, meta 


def get_text(mdfile):

    html, meta = get_html(mdfile)
    html = '<html>{}</html>'.format(html)
    tree = etree.fromstring(html, parser=etree.HTMLParser(recover=True))
    text = etree.tostring(tree, method='text', encoding='utf-8').decode('utf-8').strip()

    return text, meta
