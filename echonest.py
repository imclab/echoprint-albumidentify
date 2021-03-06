#!/usr/bin/python

import os
import sys
import urllib2
import urlparse
import urllib
import json
import subprocess

import conf

def get_fingerprint_code(file):
    codegen = os.path.abspath("echoprint-codegen")
    proclist = [codegen, os.path.abspath(file), "0", "30"]
    try:
        p = subprocess.Popen(proclist, stdout=subprocess.PIPE)
        code = p.communicate()[0]
        code = json.loads(code)
        if len(code) and "code" in code[0]:
            codestr = code[0]["code"]
            return fp_lookup(codestr)

    except OSError:
        print >>sys.stderr, "put echoprint-codegen in %s" % os.path.dirname(os.path.abspath(sys.argv[0]))
        sys.exit(1)

def fingerprint(file):
    code = get_fingerprint_code(file)
    songs = code["response"]["songs"]
    if len(songs):
        if "tracks" in songs[0]:
            ep = [t for t in songs[0]["tracks"] if t["catalog"] == "echoprint"]
            if len(ep):
                return ep[0]["foreign_id"]
    return None

def _do_en_query(method, postdata=None, **kwargs):
    args = {}
    for k,v in kwargs.items():
        args[k] = v.encode("utf8")
    args["api_key"] = conf.echonest_key
    args["format"]="json"

    url=urlparse.urlunparse(('http',
        conf.echonest_host,
        '/api/v4/%s' % method,
        '',
        urllib.urlencode(args),
    ''))
    #print >> sys.stderr, "opening url",url
    req = urllib2.Request(url)
    f = urllib2.urlopen(req)
    return json.loads(f.read())

def artist_profile(artistid):
	return _do_en_query("artist/profile", bucket="id:musicbrainz", id=artistid)

def fp_lookup(code):
	return _do_en_query("song/identify", bucket="id:echoprint", code=code, version="4.12")

def track_profile(id):
	return _do_en_query("track/profile", id=id)

def pp(data):
	print json.dumps(data, indent=4)

def main():
	#pp(artist_profile("ARH6W4X1187B99274F"))
	pp(fingerprint(sys.argv[1]))

if __name__ =="__main__":
	if len(sys.argv) < 2:
		print "usage: %s [mbid|] <args>" % sys.argv[0]
		sys.exit()
	else:
		main()
