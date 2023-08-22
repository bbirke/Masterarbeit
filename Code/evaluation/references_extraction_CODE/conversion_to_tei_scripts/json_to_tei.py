import json as JS
from lxml.etree import QName
from lxml import etree
import os.path
from generate_new_xml import generate_xml, get_time, add_to_xml
from retrieve_jats_metadata import create_standard_reference
import sys


# da sistemare una volta capito come muoversi (al momento interpretata venue come title)
# al momento del confronto, solo nel caso di science parse, si farà un doppio check per vedere se il titolo del...
# monografico coincide con quello dell'analitico e gli autori sono gli stessi. Nel caso si accerta l'uguaglianza.
def create_citation(metadata_list, analyt_node, mono_node, imprint_node):
    title = venue = year = 0

    for coupled_meta in metadata_list:
        if analyt_node is None:
            analyt_node = mono_node

        if coupled_meta[0][0] == 'author':  # and len(coupled_meta) > 0:
            for tup in coupled_meta:
                author_element = etree.SubElement(analyt_node, 'author')
                persname_element = etree.SubElement(author_element, 'persName')
                persname_element.text = tup[1]

        elif coupled_meta[0] == 'title':  # and title == 0:
            if analyt_node == mono_node:
                analyt_node, title = create_standard_reference(analyt_node, 'title', None, None, coupled_meta[1], title)
            else:
                analyt_node, title = create_standard_reference(analyt_node, 'title', ['level'], ['a'], coupled_meta[1], title)

        elif coupled_meta[0] == 'venue':  # and venue == 0:
            mono_node, source = create_standard_reference(mono_node, 'title', None, None, coupled_meta[1], venue)

        elif coupled_meta[0] == 'year':  # and year == 0:
            imprint_node, year = create_standard_reference(imprint_node, 'date', ['when'], [get_time(str(coupled_meta[1]))], str(coupled_meta[1]), year)

        else:
            print(coupled_meta)


def add_listbibl(tree, cit_id, metadata_list, venue, article_title):
    root = tree.getroot()

    # create listBibl with respective id
    listbibl_element = etree.SubElement(root[0][0], 'biblStruct')
    listbibl_element.attrib[QName("http://www.w3.org/XML/1998/namespace", "id")] = "b"+str(cit_id)
    # create sections analytic and/or monograph
    analyt_node = None
    if venue:
        analyt_node = etree.SubElement(listbibl_element, 'analytic')
    mono_node = etree.SubElement(listbibl_element, 'monogr')
    imprint_node = etree.SubElement(mono_node, 'imprint')
    # call the function create_citations to fill the sections
    create_citation(metadata_list, analyt_node, mono_node, imprint_node)


def json_parser(infile, outfile):
    # check the existence of the xml
    try:
        generate_xml(outfile)
        field_list = ['title', 'author', 'venue', 'year']
        with open(infile, "r") as json_file:

            data = JS.load(json_file)
            try:
                meta = data['metadata']['references']
                print("reference list: ", meta)
            except KeyError:
                sys.exit('Ops, no references section found!')

            outtree = etree.parse(outfile)
            for ref in meta:
                all_meta = []
                title = False
                venue = False
                for field in field_list:
                    try:
                        if ref[field] is not None:
                            if not isinstance(ref[field], list):
                                if field == 'title':
                                    title = True
                                elif field == 'venue':
                                    venue = True
                                all_meta.append((field, ref[field]))
                            else:
                                l = []
                                if len(ref[field]):
                                    for value in ref[field]:
                                        l.append((field, value))
                                    all_meta.append(l)
                    except KeyError:  # this activates in case no metadata with such key exists
                        pass
                print(all_meta)
                add_listbibl(outtree, meta.index(ref), all_meta, venue, title)
        add_to_xml(outtree, outfile)

    except FileNotFoundError:
        sys.exit('No file found: {}'.format(infile)+'check if the filepath and the file name are correct')


# Driver Code
# use absolute path, es. '/Users/alessiacioffi/Desktop/dhdk/tesi/gold_standard/XML_citations/AGR-BIO-SCI_1.xml'
if __name__ == "__main__":
    # change the input XML so to call create_tei_xml
    # filename = os.path.splitext('paper_test.cermxml')[0]
    filename = 'z_notes_test1_sp.json'
    only_name = os.path.splitext(filename)[0]
    # path to the folder of the output directory: use absolute path, e.g. /Users/alessiacioffi/Desktop/dhdk/tesi/conversion_to_TEI/scholarcy
    out_path = '/Users/alessiacioffi/Desktop/dhdk/tesi/software_eval/goldStand_parsed/parsed_output_files/ScienceParse/'
    # path to the folder of the output directory: use absolute path, es. /Users/alessiacioffi/Desktop/dhdk/tesi/gold_standard/XML_citations
    in_path = '/Users/alessiacioffi/Desktop/dhdk/tesi/software_eval/output_files/ScienceParse/'
    # launch the filling function with the path of the input xml and the one of the output xml
    json_parser(in_path+filename, out_path+only_name+"_tei.xml")
