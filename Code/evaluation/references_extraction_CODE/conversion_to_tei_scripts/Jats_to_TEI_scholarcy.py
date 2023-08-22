import sys
from lxml import etree
from lxml.etree import QName
import os.path
from generate_new_xml import add_to_xml, get_time
from retrieve_jats_metadata import check_ref_existence, create_standard_reference


def create_citation(metadata_list, analyt_node, mono_node, imprint_node, series_node, pub_type):
    title = source = series = year = volume = issue = page_range = publisher = pubplace = uri = doi = 0

    for coupled_meta in metadata_list:
        if analyt_node is None:  # if there is no analytic section write in monograph
            analyt_node = mono_node

        if coupled_meta[0] == 'person-group':  # and len(coupled_meta[1]) > 0:
            for author in coupled_meta[1]:
                if author[0] == 'author':
                    tag_name = 'author'
                    cur_node = analyt_node
                else:
                    tag_name = 'editor'
                    cur_node = mono_node
                author_element = etree.SubElement(cur_node, tag_name)
                persname_element = etree.SubElement(author_element, 'persName')
                persname_element.text = author[1]

        elif coupled_meta[0] == 'article-title' or coupled_meta[0] == 'chapter-title' and title == 0:
            if analyt_node != mono_node:
                lev = 'a'
            else:
                lev = 'm'
            analyt_node, title = create_standard_reference(analyt_node, 'title', ['level'], [lev], coupled_meta[1], title)

        elif coupled_meta[0] == 'source':  # and source == 0:
            if pub_type == 'article-journal':
                lev = 'j'
            else:
                lev = 'm'
            mono_node, source = create_standard_reference(mono_node, 'title', ['level'], [lev], coupled_meta[1], source)

        elif coupled_meta[0] == 'series':  # and series == 0:
            if series_node is None:
                imprint_node, volume = create_standard_reference(imprint_node, 'biblScope', ['unit'], ['volume'],
                                                                 coupled_meta[1], volume)
            else:
                series_node, volume = create_standard_reference(series_node, 'biblScope', ['unit'], ['volume'],
                                                                coupled_meta[1], volume)

        elif coupled_meta[0] == 'year':  # and year == 0:
            imprint_node, year = create_standard_reference(imprint_node, 'date', ['when'], [get_time(coupled_meta[1])], coupled_meta[1], year)

        elif coupled_meta[0] == 'volume':  # and volume == 0:
            imprint_node, volume = create_standard_reference(imprint_node, 'biblScope', ['unit'], ['volume'], coupled_meta[1], volume)

        elif coupled_meta[0] == 'issue':  # and issue == 0:
            imprint_node, issue = create_standard_reference(imprint_node, 'biblScope', ['unit'], ['issue'], coupled_meta[1], issue)

        elif coupled_meta[0] == 'publisher-name':  # and publisher == 0:
            imprint_node, publisher = create_standard_reference(imprint_node, 'publisher', None, None, coupled_meta[1], publisher)

        elif coupled_meta[0] == 'publisher-loc':  # and pubplace == 0:
            imprint_node, pubplace = create_standard_reference(imprint_node, 'pubPlace', None, None, coupled_meta[1], pubplace)

        elif coupled_meta[0] == 'page-range':  # and page_range == 0:
            imprint_node, page_range = create_standard_reference(imprint_node, 'biblScope', ['unit'], ['page'], coupled_meta[1], page_range)

        elif coupled_meta[0] == 'pub-id':
            analyt_node, doi = create_standard_reference(analyt_node, 'idno', ['type'], ['DOI'], coupled_meta[1], doi)

        elif coupled_meta[0] == 'uri':
            mono_node, uri = create_standard_reference(mono_node, 'ref', ['target'], [coupled_meta[1]], coupled_meta[1], uri)

        else:
            print(coupled_meta)


def add_listbibl(tree, cit_id, metadata_list, analytic_var, series_var, pub_type):
    root = tree.getroot()

    # create listBibl with respective id
    listbibl_element = etree.SubElement(root[0][0], 'biblStruct')
    listbibl_element.attrib[QName("http://www.w3.org/XML/1998/namespace", "id")] = "b"+str(cit_id)
    # create sections analytic and/or monograph
    analyt_node, series_node = None, None
    if analytic_var:
        analyt_node = etree.SubElement(listbibl_element, 'analytic')
    mono_node = etree.SubElement(listbibl_element, 'monogr')
    imprint_node = etree.SubElement(mono_node, 'imprint')
    if series_var:
        series_node = etree.SubElement(listbibl_element, 'series')
    # call the function create_citations to fill the sections
    create_citation(metadata_list, analyt_node, mono_node, imprint_node, series_node, pub_type)


def parse_scholarcy_output(input_xml, output_xml):
    # call the function check_ref_existence to verify the existence of the references section
    tree, ex_phr = check_ref_existence(input_xml, output_xml, True)
    if tree is None:
        sys.exit('No citation subtree found in {}'.format(input_xml)+': \n'+ex_phr)

    # iteration over single references
    cur_cit = 1
    outtree = etree.parse(output_xml)
    # listBibl_node = etree.SubElement(tree.getroot()[0], 'listBibl')
    while cur_cit <= len(tree.xpath('//ref')):
        cur_pos = cur_cit-1
        all_meta_full = []
        analytic_var, series_var = False, False
        pub_type = ''
        pub_list = ['article-journal', 'chapter', 'paper-conference']
        for c in tree.xpath('//ref')[cur_pos]:
            if c.tag == 'element-citation' and c.attrib.get('publication-type') in pub_list:
                analytic_var = True
                pub_type = c.attrib.get('publication-type')
            for child in c:
                if child.tag == 'series':
                    series_var = True
                if child.tag != 'person-group':
                    all_meta_full.append([child.tag, child.text])
                else:
                    l = []
                    [l.append((child.attrib.get('person-group-type'), subchild.text)) for subchild in child]
                    all_meta_full.append([child.tag, l])
        # print('ref ', cur_cit, analytic_var, ' ', all_meta_full)
        add_listbibl(outtree, cur_pos, all_meta_full, analytic_var, series_var, pub_type)
        cur_cit += 1
    add_to_xml(outtree, output_xml)


# Driver Code
if __name__ == "__main__":
    # change the input XML so to call create_tei_xml
    # filename = os.path.splitext('AGR-BIO-SCI_1.pdf_(Jats2).xml')[0]
    filename = 'z_notes_test2.pdf.xml'
    only_name = os.path.splitext(filename)[0]
    # path to output directory folder: use absolute path, e.g. /Users/alessiacioffi/Desktop/dhdk/conversion_to_TEI
    out_path = '/Users/alessiacioffi/Desktop/dhdk/tesi/software_eval/goldStand_parsed/parsed_output_files/scholarcy/'
    # path to output directory folder: use absolute path, es. /Users/alessiacioffi/Desktop/dhdk/tesi/
    in_path = '/Users/alessiacioffi/Desktop/dhdk/tesi/software_eval/output_files/Scholarcy/'
    # launch the filling function with the path of the input xml and the one of the output xml
    parse_scholarcy_output(in_path+filename, out_path+only_name+"_tei.xml")
