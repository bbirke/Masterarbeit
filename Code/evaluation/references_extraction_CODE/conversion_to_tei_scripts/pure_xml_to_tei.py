import sys
from lxml import etree
from lxml.etree import QName
import os.path
from generate_new_xml import add_to_xml, get_time
from retrieve_jats_metadata import check_ref_existence, create_standard_reference


# forse va annullato il fatto che solo la prima occorrenza viene considerata, altrimenti si perdono dati importanti sulla precision
# modifiche da fare:
# 1. tenere in considerazione la possibilità che un metadato sia taggato male: gestire gli errori
def create_citation(metadata_list, analyt_node, mono_node, imprint_node):
    title = year = volume = pages = url = source = fpage = lpage = issue = doi = publisher = 0

    for coupled_meta in metadata_list:
        if analyt_node is None:
            analyt_node = mono_node

        # option only for excite
        if coupled_meta[0] == 'author' or coupled_meta[0] == 'editor' and len(coupled_meta[1]) > 0:
            if coupled_meta[0] == 'author':
                node = analyt_node
            else:
                node = mono_node
            author_node = etree.SubElement(node, coupled_meta[0])
            persname_node = etree.SubElement(author_node, 'persName')
            for tup in coupled_meta[1]:
                if coupled_meta[0] != tup[0]:
                    if tup[0] == 'surname':
                        new_node = 'surname'
                    else:
                        new_node = 'given-name'
                    etree.SubElement(persname_node, new_node).text = tup[1]

                else:
                    persname_node.text = tup[1]

        elif coupled_meta[0] == 'title':  # and title == 0:
            level = None
            val = None
            if analyt_node != mono_node:
                level = ['level']
                val = ['a']
            analyt_node, title = create_standard_reference(analyt_node, 'title', level, val, coupled_meta[1], title)

        # DA SISTEMARE LA FPAGE PERCHè SI VEDE INTERNA AL TAG INVECE CHE IN FROM
        # elif coupled_meta[0] == 'fpage' and fpage == 0:
        elif coupled_meta[0] == 'fpage' and fpage == lpage:
            imprint_node, fpage = create_standard_reference(imprint_node, 'biblScope', ['unit', 'from'], ['page', coupled_meta[1]], None, fpage)

        # elif coupled_meta[0] == 'lpage' and fpage == 1 and lpage == 0:
        elif coupled_meta[0] == 'lpage':
            if fpage == (lpage+1):
                for node in imprint_node:
                    if node.attrib.get('unit') == 'page' and not node.attrib.get('to'):
                        if coupled_meta[1]:
                            node.attrib['to'] = coupled_meta[1]
                        else:  # fatto apposta per evitare che in caso di tag vuoto ci sia errore
                            node.attrib['to'] = ""
                        lpage += 1
            else:
                if coupled_meta[1]:
                    text = coupled_meta[1]
                else:
                    text = ""
                imprint_node, cur_var = create_standard_reference(imprint_node, 'biblScope', ['unit', 'to'], ['page', text], None, fpage)

        elif coupled_meta[0] == 'identifier':
            analyt_node, doi = create_standard_reference(analyt_node, 'idno', ['type'], ['DOI'], coupled_meta[1], doi)

        elif coupled_meta[0] == 'pages':  #  and pages == 0:
            imprint_node, pages = create_standard_reference(imprint_node, 'biblScope', ['unit'], ['page'], coupled_meta[1], pages)

        elif coupled_meta[0] == 'publisher':  # and publisher == 0:
            imprint_node, publisher = create_standard_reference(imprint_node, 'publisher', None, None, coupled_meta[1], publisher)

        elif coupled_meta[0] == 'source':  # and source == 0:
            mono_node, source = create_standard_reference(mono_node, 'title', None, None, coupled_meta[1], source)

        elif coupled_meta[0] == 'url':  # and url == 0:
            mono_node, url = create_standard_reference(imprint_node, 'ref', ['target'], [coupled_meta[1]], coupled_meta[1], url)

        elif coupled_meta[0] == 'volume':  # and volume == 0:
            imprint_node, volume = create_standard_reference(imprint_node, 'biblScope', ['unit'], ['volume'], coupled_meta[1], volume)

        elif coupled_meta[0] == 'issue':  # and issue == 0:
            imprint_node, issue = create_standard_reference(imprint_node, 'biblScope', ['unit'], ['issue'], coupled_meta[1], volume)

        elif coupled_meta[0] == 'year':  # and year == 0:
            imprint_node, year = create_standard_reference(imprint_node, 'date', ['when'], [get_time(coupled_meta[1])], coupled_meta[1], year)

        else:
            print(coupled_meta)


def add_listbibl(tree, cit_id, metadata_list, source, article_title):
    root = tree.getroot()

    # create listBibl with respective id
    listbibl_element = etree.SubElement(root[0][0], 'biblStruct')
    listbibl_element.attrib[QName("http://www.w3.org/XML/1998/namespace", "id")] = "b"+str(cit_id)
    # create sections analytic and/or monograph

    # sezione solo per excite
    analyt_node = None
    # if source and article_title:
    if source:  # è sufficiente che ci sia article title per creare la sezione analytic
        analyt_node = etree.SubElement(listbibl_element, 'analytic')
    # fino a qua

    mono_node = etree.SubElement(listbibl_element, 'monogr')
    imprint_node = etree.SubElement(mono_node, 'imprint')
    # call the function create_citations to fill the sections
    create_citation(metadata_list, analyt_node, mono_node, imprint_node)


def parse_generic_xml_output(input_xml, output_xml):
    # call the function check_ref_existence to verify the existence of the references section
    tree, ex_phr = check_ref_existence(input_xml, output_xml, False)
    if tree is None:
        sys.exit('No citation subtree found in {}'.format(input_xml)+': \n'+ex_phr)

    # iteration over single references
    cur_cit = 1
    outtree = etree.parse(output_xml)
    while cur_cit <= len(tree.xpath('//reference')):
        cur_pos = cur_cit-1
        all_meta_full = []
        sour = False
        art_title = False
        for c in tree.xpath('//reference')[cur_pos]:
            # all_meta_full.append([c.tag, c.text])
            if c.tag == 'source':
                sour = True
            if c.tag == 'title':
                art_title = True
            if c.tag != 'author' and c.tag != 'editor':
                all_meta_full.append([c.tag, c.text])
            else:
                l = []
                if len(c.getchildren()) > 0:
                    [l.append((child.tag, child.text)) for child in c]
                else:
                    l.append((c.tag, c.text))
                all_meta_full.append([c.tag, l])
        # print('ref ', cur_cit, all_meta_full)
        add_listbibl(outtree, cur_pos, all_meta_full, sour, art_title)
        cur_cit += 1
    add_to_xml(outtree, output_xml)


# Driver Code
if __name__ == "__main__":
    # change the input XML so to call create_tei_xml

    filename = 'AGR-BIO-SCI_1_excite.xml'
    only_name = os.path.splitext(filename)[0]
    # path to the folder of the output directory: use absolute path, e.g. /Users/alessiacioffi/Desktop/dhdk/tesi/conversion_to_TEI/scholarcy
    out_path = 'D:/Projects/Masterarbeit/evaluation/references_extraction_DATA/own_results/'
    # path to the folder of the output directory: use absolute path, es. /Users/alessiacioffi/Desktop/dhdk/tesi/gold_standard/XML_citations
    in_path = 'D:/Projects/Masterarbeit/evaluation/references_extraction_DATA/output_files/ExCite/'


    # launch the filling function with the path of the input xml and the one of the output xml
    parse_generic_xml_output(in_path+filename, out_path+only_name+"_tei.xml")
