import sys
from lxml import etree
from lxml.etree import QName
import os.path
from generate_new_xml import add_to_xml, get_time
from retrieve_jats_metadata import check_ref_existence, create_standard_reference


def create_citation(metadata_list, analyt_node, mono_node, imprint_node):
    title = source = year = volume = fpage = lpage = 0

    for coupled_meta in metadata_list:
        if analyt_node is None:
            analyt_node = mono_node

        if coupled_meta[0] == 'string-name' and len(coupled_meta[1]) > 0:
            author_element = etree.SubElement(analyt_node, 'author')
            persname_element = etree.SubElement(author_element, 'persName')

            for tup in coupled_meta[1]:
                if tup[0] == 'surname':
                    new_node = 'surname'
                else:
                    new_node = 'forename'
                etree.SubElement(persname_element, new_node).text = tup[1]

        elif coupled_meta[0] == 'article-title':  # and title == 0:
            if analyt_node == mono_node:
                analyt_node, title = create_standard_reference(analyt_node, 'title', None, None, coupled_meta[1], title)
            else:
                analyt_node, title = create_standard_reference(analyt_node, 'title', ['level'], ['a'], coupled_meta[1], title)

        elif coupled_meta[0] == 'source':  # and source == 0:
            mono_node, source = create_standard_reference(mono_node, 'title', None, None, coupled_meta[1], source)

        elif coupled_meta[0] == 'year':  # and year == 0:
            imprint_node, year = create_standard_reference(imprint_node, 'date', ['when'], [get_time(coupled_meta[1])], coupled_meta[1], year)

        elif coupled_meta[0] == 'volume':  # and volume == 0:
            imprint_node, volume = create_standard_reference(imprint_node, 'biblScope', ['unit'], ['volume'], coupled_meta[1], volume)

        elif coupled_meta[0] == 'issue':  # and issue == 0:
            imprint_node, issue = create_standard_reference(imprint_node, 'biblScope', ['unit'], ['issue'], coupled_meta[1], volume)

        elif coupled_meta[0] == 'fpage':  # and fpage == 0:
            imprint_node, fpage = create_standard_reference(imprint_node, 'biblScope', ['unit', 'from'], ['page', coupled_meta[1]], None, fpage)

        # if lpage is found, check if last <biblscope unit="page" from="xxx"> in imprint node has attribute to=""
        # if there is no imprint node, or there is no such node in imprint or if the last imprint node has a to="":
        # create a <biblscope unit="page" to="xxx"> element
        # vice versa add an attribute to to the already existing page element
        elif coupled_meta[0] == 'lpage':
            if coupled_meta[1]:
                text = coupled_meta[1]
            else:
                text = ""
            try:
                pages = [a for a in imprint_node.getchildren() if a.attrib.get('unit') == 'page']
            except ValueError:
                pages = []
            if not len(pages) or (len(pages) and pages[-1].attrib.get('to')):
                imprint_node, cur_var = create_standard_reference(imprint_node, 'biblScope', ['unit', 'to'], ['page', text], None, fpage)
            else:
                pages[-1].attrib['to'] = text
            lpage += 1

        else:
            print(coupled_meta)

        '''if fpage == (lpage+1):
                for node in imprint_node:
                    if node.attrib.get('unit') == 'page' and not node.attrib.get('to'):
                        node.attrib['to'] = coupled_meta[1]
                        lpage += 1
            # cerco il nodo più vicino all'elemento lpage corrente che non contenga un to="": 
            # seleziono tra i figli di imprint con tag 'page' quello in posizione fpage-1
            elif fpage > (lpage+1):
                pages = [a for a in imprint_node.getchildren() if a.tag == 'page']
                if not pages[fpage-1].attrib.get('to'):
                    pages[fpage-1].attrib['to'] = coupled_meta[1]
                lpage += 1  
            # con questo else non si perdono gli lpage lasciati a sè
            else:
                if coupled_meta[1]:
                    text = coupled_meta[1]
                else:
                    text = ""
                imprint_node, cur_var = create_standard_reference(imprint_node, 'biblScope', ['unit', 'to'], ['page', text], None, fpage)'''



def add_listbibl(tree, cit_id, metadata_list, source, article_title):
    root = tree.getroot()

    # create listBibl with respective id
    listbibl_element = etree.SubElement(root[0][0], 'biblStruct')
    listbibl_element.attrib[QName("http://www.w3.org/XML/1998/namespace", "id")] = "b"+str(cit_id)
    # create sections analytic and/or monograph
    analyt_node = None
    if source:  # section anal. is always created when source tag exists
        analyt_node = etree.SubElement(listbibl_element, 'analytic')
    mono_node = etree.SubElement(listbibl_element, 'monogr')
    imprint_node = etree.SubElement(mono_node, 'imprint')
    # call the function create_citations to fill the sections
    create_citation(metadata_list, analyt_node, mono_node, imprint_node)


def parse_cermine_output(input_xml, output_xml):
    # call the function check_ref_existence to verify the existence of the references section
    tree, ex_phr = check_ref_existence(input_xml, output_xml, True)
    if tree is None:
        sys.exit('No citation subtree found in {}'.format(input_xml)+': \n'+ex_phr)

    # iteration over single references
    cur_cit = 1
    outtree = etree.parse(output_xml)
    while cur_cit <= len(tree.xpath('//ref')):
        cur_pos = cur_cit-1
        # all_meta is the list of all the elements under the current 'ref' element
        all_meta_full = []
        sour = False
        art_title = False
        for meta in tree.xpath('//ref')[cur_pos]:
            for c in meta:
                if c.tag == 'source':
                    sour = True
                if c.tag == 'article-title':
                    art_title = True
                if c.tag != 'string-name':
                    all_meta_full.append([c.tag, c.text])
                else:
                    l = []
                    [l.append((child.tag, child.text)) for child in c]
                    all_meta_full.append([c.tag, l])
        # print('ref ', cur_cit, ' ', all_meta_full)
        add_listbibl(outtree, cur_pos, all_meta_full, sour, art_title)
        cur_cit += 1
    add_to_xml(outtree, output_xml)


    ''' # all_meta = [[(c.tag, c.text) for c in meta] for meta in tree.xpath('//ref')[cur_pos]]
    all_meta = [[c.tag for c in meta] for meta in tree.xpath('//ref')[cur_pos]]'''


# Driver Code
# use absolute path, es. '/Users/alessiacioffi/Desktop/dhdk/tesi/gold_standard/XML_citations/AGR-BIO-SCI_1.xml'
if __name__ == "__main__":
    # change the input XML so to call create_tei_xml
    filename = 'VET_54.cermxml'
    only_name = os.path.splitext(filename)[0]
    # path to intput directory: absolute path, e.g. /Users/alessiacioffi/Desktop/dhdk/tesi/gold_standard/XML_citations
    in_path = '/Users/alessiacioffi/Desktop/dhdk/tesi/software_eval/output_files/Cermine/'
    # path to output directory: absolute path, e.g. /Users/alessiacioffi/Desktop/dhdk/tesi/conversion_to_TEI/scholarcy
    out_path = '/Users/alessiacioffi/Desktop/dhdk/tesi/software_eval/goldStand_parsed/parsed_output_files/Cermine/'
    # launch the filling function with the path of the input xml and the one of the output xml
    parse_cermine_output(in_path+filename, out_path+only_name+"_tei.xml")
