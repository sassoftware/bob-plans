#!/usr/bin/python

import os
import sys, optparse, urllib, xml.dom.minidom
import time

# return a nodelist of image nodes from a response to the product images call
def getImageNodes(responsexml):
    images = responsexml.getElementsByTagName("images")[0]
    imagenodelist = images.getElementsByTagName("image")
    return imagenodelist

# return a dictionary of image nodes with trailingversions matching the label, keyed off image id
def getImageDictByLabel(nodelist, label):
    retval = {}
    for node in nodelist:
        troveversion = node.getElementsByTagName("troveVersion")[0].childNodes[0].data
        imageid = node.getElementsByTagName("imageId")[0].childNodes[0].data
        status = node.getElementsByTagName("imageStatus")[0].getElementsByTagName("code")[0].childNodes[0].data
        if troveversion.lower().find(label.lower()) > -1 and status == "300":
            retval[int(imageid)] = node
    return retval

# returns the nth image in reverse sorted order of imageId
def getNthImage(nodedict, idx):
    keys = nodedict.keys()
    keys.sort()
    keys.reverse()
    imageid = keys[idx]
    return nodedict[imageid]

# return the url of the iso from the image node
def getIsoFileUrl(node):
    files = node.getElementsByTagName("file")
    isofile = files[0]
    isourl = isofile.getElementsByTagName("url")[0].childNodes[0].data
    return isourl

# get the sha1 sum of the downloaded iso 
def getFileSha1(filepath):
    import subprocess
    p = subprocess.Popen (('sha1sum', filepath), shell=False, stdout=subprocess.PIPE)
    x = p.communicate()[0]
    return x.split()[0]
    

def main():

    p = optparse.OptionParser()
    p.add_option('--label', '-l', type="string", dest="label")
    p.add_option('--rbusername', '-u', type="string", dest="rbusername")
    p.add_option('--rbpassword', '-p', type="string", dest="rbpassword")
    p.add_option('--rbserver', '-s', type="string", dest="rbserver")
    p.add_option('--rbproject', '-P', type="string", dest="rbproject")
    p.add_option('--index', '-i', type="int", dest="index", default=0)
    p.add_option('--outputfile', '-o', type="string", dest="outputfile")
    options, arguments = p.parse_args()

    if options.label is None \
        or options.outputfile is None \
        or options.rbusername is None \
        or options.rbpassword is None \
        or options.rbserver is None \
        or options.rbproject is None:
        sys.exit("You are missing required arguments, run with -h for help")

    base = 'https://%s:%s@%s/' % (options.rbusername, options.rbpassword,
            options.rbserver)
    conn = urllib.urlopen(base + "api/products/%s/images"
            % options.rbproject)
    response = conn.read()

    doc = xml.dom.minidom.parseString(response)
    list = getImageNodes(doc)
    matchingdict = getImageDictByLabel(list, options.label)
    image = getNthImage(matchingdict, options.index)
    url = getIsoFileUrl(image).replace('https://', 'http://')
    for x in range(5):
        sys.stdout.write("Retrieving ISO from %s.\n" % (url))
        urllib.urlretrieve(url, options.outputfile)
        if os.stat(options.outputfile).st_size == 0:
            # No idea why this happens...
            print >> sys.stderr, "File is empty!"
            time.sleep(15)
        else:
            break
    else:
        sys.exit("Failed to download image file")
    sys.stdout.write("ISO file %s has SHA1 %s.\n" % ( options.outputfile, getFileSha1(options.outputfile) ) )

    # Delete after it's downloaded
    imageId = str(image.getElementsByTagName('imageId')[0].childNodes[0].data)
    imageUrl = base + 'api/v1/images/' + imageId
    urllib.urlopen("%s%s?_method=DELETE" %
            (base, str(imageUrl.split('/', 3)[3])))

if __name__ == '__main__':
    main()
