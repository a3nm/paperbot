"""
Fetches papers.
"""

import os
import json
import random
import requests

def download(phenny, input, verbose=True):
    """
    Downloads a paper.
    """
    # only accept requests in a channel
    if not input.sender.startswith('#'):
        # unless the user is an admin, of course
        if not input.admin:
            phenny.say("i only take requests in the ##hplusroadmap channel.")
            return
        else:
            # just give a warning message to the admin.. not a big deal.
            phenny.say("okay i'll try, but please send me requests in ##hplusroadmap in the future.")

    # get the input
    line = input.group()

    # was this an explicit command?
    explicit = False
    if line.startswith(phenny.nick):
        explicit = True
        line = line[len(phenny.nick):]

        if line.startswith(",") or line.startswith(":"):
            line = line[1:]

    if line.startswith(" "):
        line = line.strip()

    # don't bother if there's nothing there
    if len(line) < 5 or (not "http://" in line and not "https://" in line) or not line.startswith("http"):
        return

    translation_url = "http://localhost:1969/web"

    headers = {
        "Content-Type": "application/json",
    }
    
    data = {
        "url": line,
        "sessionid": "what"
    }

    data = json.dumps(data)

    response = requests.post(translation_url, data=data, headers=headers)

    if response.status_code == 200:
        # see if there are any attachments
        content = json.loads(response.content)
        item = content[0]
        title = item["title"]
        
        if item.has_key("attachments"):
            pdf_url = None
            for attachment in item["attachments"]:
                if attachment.has_key("mimeType") and "application/pdf" in attachment["mimeType"]:
                    pdf_url = attachment["url"]
                    break

            if pdf_url:
                user_agent = "Mozilla/5.0 (X11; Linux i686 (x86_64)) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.57 Safari/536.11"

                headers = {
                    "User-Agent": user_agent,
                }

                response = None
                if pdf_url.startswith("https://"):
                    response = requests.get(pdf_url, headers=headers, verify=False)
                else:
                    response = requests.get(pdf_url, headers=headers)

                # detect failure
                if response.status_code == 401:
                    phenny.say("HTTP 401 unauthorized " + str(pdf_url))
                    return
                elif response.status_code != 200:
                    phenny.say("HTTP " + str(response.status_code) + " " + str(pdf_url))
                    return

                data = response.content

                path = os.path.join("/home/bryan/public_html/papers2/paperbot/", title + ".pdf")

                file_handler = open(path, "w")
                file_handler.write(data)
                file_handler.close()

                # grr..
                title = title.encode("ascii", "ignore")

                filename = requests.utils.quote(title)
                url = "http://diyhpl.us/~bryan/papers2/paperbot/" + filename + ".pdf"
                
                phenny.say(url)
                return
            elif verbose and explicit:
                phenny.say("error: didn't find any pdfs on " + line)
                phenny.say(download_url(line))
                return
        elif verbose and explicit:
            phenny.say("error: dunno how to find the pdf on " + line)
            phenny.say(download_url(line))
            return
    elif verbose and explicit:
        if response.status_code == 501:
            if verbose:
                phenny.say("no translator available, raw dump: " + download_url(line))
                return
        else:
            if verbose:
                phenny.say("error: HTTP " + str(response.status_code) + " " + download_url(line))
                return
    else:
        return
download.commands = ["fetch", "get", "download"]
download.priority = "high"
download.rule = r'(.*)'

def download_ieee(url):
    """
    Downloads an IEEE paper. The Zotero translator requires frames/windows to
    be available. Eventually translation-server will be fixed, but until then
    it might be nice to have an IEEE workaround.
    """
    # url = "http://ieeexplore.ieee.org:80/xpl/freeabs_all.jsp?reload=true&arnumber=901261"
    # url = "http://ieeexplore.ieee.org/iel5/27/19498/00901261.pdf?arnumber=901261"
    raise NotImplementedError

def download_url(url):
    response = requests.get(url, headers={"User-Agent": "origami-pdf"})
    content = response.content
    
    title = "%0.2x" % random.getrandbits(128)

    path = os.path.join("/home/bryan/public_html/papers2/paperbot/", title)

    file_handler = open(path, "w")
    file_handler.write(content)
    file_handler.close()

    url = "http://diyhpl.us/~bryan/papers2/paperbot/" + title

    return url
