#!/usr/bin/python3
# USC_XML_Reference_data_extractor.py
"""

Copyright © 2013 ontolawgy LLC. MIT licensed.

See LICENSE for more details, but here are the license terms in a nutshell: Do
what you want with this, including build a commercial product, just make sure
to mention that you got some of your ideas from here. If you break something,
kill people, etc., any legal consequences are yours, and yours alone.

OK, so what is this tool for?

This small program extracts granular legal cross-references from U.S. Code XML
data.  It is up to you to slice and dice the result as you see fit. I set up
the output this way for a specific project. It is very bare bones, but provides
a framework for doing fancier stuff.

"""

import os, re, sys
from sys import argv
from lxml import etree

def iterate_sections(sections, refdict):

    """Iterate over all sections and add references to a dict as a list of
    dicts, embedding relevant metadata. Yes, it is messy and redundant, but it
    protects against potential data loss when extracting individual records.
    As of 2013-11-11, it does not capture supra-section taxonomies such as
    chapter, subchapter, etc., but this function is pretty straightforward to
    add and may be added in the near future.

    Note that you may need to monitor the input file size. This has only been
    tested on slivers of the U.S. Code at the Chapter level in Titles that are
    organized in a Title/Chapter/Subchapter taxonomy."""

    for i in range(len(sections)): #Iterate over all sections
        if 'identifier' in sections[i].attrib: #Check to see if it's a real section
            id = sections[i].attrib['identifier']
            reflist = [] # initialize list for references
            section_citation_count = 0 # Track citation order per section
            for s in sections[i].iterfind('.//ref'): #Look for references
                section_citation_count += 1
                #iterate over ancestors, grab the closest one, and track that as the citing provision
                ancestors = []
                content_type = None
                for a in s.iterancestors():
                    if 'identifier' in a.attrib:
                        ancestors.append(a.attrib['identifier'])
                    else:
                        content_type = a.tag


                reflist.append([{'sec': id}, {'sec_sortkey': i}, {'citing_provision': {content_type: ancestors[0]}}, {'cited_provision':s.attrib}, {'section_citation_number': section_citation_count}])
                """Add references to list of dicts to be added to each section record in the main dict; some data duplicated to ensure data integrity in case record gets separated from its parent dict k:v pair in later post-processing when using this as a script or as part of a larger program"""
            # add references to the section record
            refdict[id]=dict({'sec':id}, **{'refs': reflist})

""" for debugging
for k in refdict:
    print (k, " has ", len(refdict[k]['refs']), "references")
"""

def output_metadata(of_name):
    """Output metadata to a text file as newline-separated lists of dicts
    for each reference record."""

    of = open(of_name, 'w')
    for v in refdict:
        dv = refdict[v]
        for i in dv['refs']:
            out = str(i)
            of.write(out+'\n')
    of.close()


if __name__ == "__main__":
    """Usage: USC_XML_Reference_data_extractor.py FILENAME - output goes to FILENAME_references.txt"""
    doc = etree.parse(argv[1]) # simple parse probably not feasible for very large files
    of_name = argv[1]+'_references.txt'
    sections = doc.xpath('//section')
    reflist = []
    refdict = {}
    iterate_sections(sections, refdict)
    output_metadata(of_name)

