import requests
from scrapy.selector import Selector
from flask import Flask, Response

app = Flask(__name__)

TEMPLATE = """
<html>
    <head>
        <title>Soundboard</title>
        <meta name="viewport" content="user-scalable=no">
        <script type="text/javascript">
            var audios = {};
            var current = undefined;
            function play(txt) {
                if (current) {
                    current.pause();
                    current.currentTime = 0;
                }
                if (audios[txt] === undefined) {
                    audios[txt] = new Audio(txt);
                }
                current = audios[txt];
                audios[txt].play();
            }
        </script>
        <style>
            body {
                font-size: 2em;
            }
        </style>
    </head>
    <body>
        <table>
%s
        </table>
    </body>
</html>
"""


def select(txt):
    xpath = "//div[@class='instant']/div[2]/@onmousedown"
    onmousedown = Selector(text=txt).xpath(xpath).extract()
    mp3s = [i[6:-2] for i in onmousedown]
    xpath = "//div[@class='instant']/a[1]/text()"
    titles = Selector(text=txt).xpath(xpath).extract()
    return titles, mp3s


def lead(i):
    return ' ' * i


def render(titles, mp3s):
    content = ""
    for title, mp3 in zip(titles, mp3s):
        url = "https://myinstants.com" + mp3
        js = "play('%s')" % url
        a = '<a onmousedown="%s">%s</a>' % (js, title)
        c = '%s<tr><td>%s</td></tr>\n' % (lead(12), a)
        content += c
    return TEMPLATE % content


@app.route("/<name>")
def soundboard(name):
    txt = requests.get("http://myinstants.com/profile/%s" % name).text
    return Response(render(*select(txt)), mimetype="text/html")

if __name__ == "__main__":
    app.run(host='0.0.0.0', port='8000')
