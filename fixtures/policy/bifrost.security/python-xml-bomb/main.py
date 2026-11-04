import sys
from xml.etree.ElementTree import fromstring as etree_fromstring
from xml.sax import parseString as sax_parse_string
from xml.dom.minidom import parseString as minidom_parse_string


class Handler:
    pass


def parse_all():
    remote_xml = sys.argv[1]
    etree_fromstring(remote_xml)
    sax_parse_string(remote_xml, Handler())
    minidom_parse_string(remote_xml)
    etree_fromstring("<root/>")
