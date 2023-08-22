import json as JS
from lxml.etree import QName
from lxml import etree
import os.path
from generate_new_xml import generate_xml, get_time, add_to_xml
from retrieve_jats_metadata import create_standard_reference
import sys
from glob import glob


# da sistemare una volta capito come muoversi (al momento interpretata venue come title)
# al momento del confronto, solo nel caso di science parse, si farà un doppio check per vedere se il titolo del...
# monografico coincide con quello dell'analitico e gli autori sono gli stessi. Nel caso si accerta l'uguaglianza.
def create_citation(metadata_list, analyt_node, mono_node, imprint_node, series_node):
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
            pers_dict = coupled_meta[1]
            for k, v in pers_dict.items():
                if k == 'surname':
                    new_node = 'surname'
                else:
                    new_node = 'forename'
                if v:
                    name_part = etree.SubElement(persname_node, new_node)
                    name_part.text = v
                    if k == "first_name" or k == "middle_name":
                        name_type = "first" if k == "first_name" else "middle"
                        name_part.set('type', name_type)

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
            imprint_node, fpage = create_standard_reference(imprint_node, 'biblScope', ['unit', 'from'],
                                                            ['page', coupled_meta[1]], None, fpage)

        # elif coupled_meta[0] == 'lpage' and fpage == 1 and lpage == 0:
        elif coupled_meta[0] == 'lpage':
            if fpage == (lpage + 1):
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
                imprint_node, cur_var = create_standard_reference(imprint_node, 'biblScope', ['unit', 'to'],
                                                                  ['page', text], None, fpage)

        elif coupled_meta[0] == 'identifier':
            analyt_node, doi = create_standard_reference(analyt_node, 'idno', ['type'], ['DOI'], coupled_meta[1], doi)

        elif coupled_meta[0] == 'pages':  # and pages == 0:
            imprint_node, pages = create_standard_reference(imprint_node, 'biblScope', ['unit'], ['page'],
                                                            coupled_meta[1], pages)

        elif coupled_meta[0] == 'publisher':  # and publisher == 0:
            imprint_node, publisher = create_standard_reference(imprint_node, 'publisher', None, None, coupled_meta[1],
                                                                publisher)

        elif coupled_meta[0] == 'source':  # and source == 0:
            mono_node, source = create_standard_reference(mono_node, 'title', None, None, coupled_meta[1], source)

        elif coupled_meta[0] == 'url':  # and url == 0:
            mono_node, url = create_standard_reference(imprint_node, 'ref', ['target'], [coupled_meta[1]],
                                                       coupled_meta[1], url)

        elif coupled_meta[0] == 'volume':  # and volume == 0:
            imprint_node, volume = create_standard_reference(imprint_node, 'biblScope', ['unit'], ['volume'],
                                                             coupled_meta[1], volume)

        elif coupled_meta[0] == 'issue':  # and issue == 0:
            imprint_node, issue = create_standard_reference(imprint_node, 'biblScope', ['unit'], ['issue'],
                                                            coupled_meta[1], volume)

        elif coupled_meta[0] == 'year':  # and year == 0:
            imprint_node, year = create_standard_reference(imprint_node, 'date', ['when'], [get_time(coupled_meta[1])],
                                                           coupled_meta[1], year)

        else:
            print(coupled_meta)


def add_listbibl(tree, cit_id, metadata_list, analytic_var, series_var):
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
    create_citation(metadata_list, analyt_node, mono_node, imprint_node, series_node)


def anystyle_parser(infile, outfile):
    try:
        generate_xml(outfile)
        pub_list = ['article-journal', 'chapter', 'paper-conference']  # cases in which analytitc node is created

        # load the file and check if there are references in list
        with open(infile, encoding="utf8") as json_file:
            data = JS.load(json_file)
            data = data["segmented_references"]["references"]
            if len(data):
                pass
                # print("references: ", data)
            else:
                sys.exit('Ops, no bibliographic section found!')

            # check and list the metadata present in the input json file
            outtree = etree.parse(outfile)
            for ref in data:
                all_meta = []
                analytic_var, series_var = False, False
                for group in ref["reference"]:
                    entity_group = group["entity_group"]

                    #keys = ref.keys()
                    # check if the reference type allows to create the analytitc section or not
                    if entity_group == 'source':
                        analytic_var = True
                    if entity_group == 'title':
                        series_var = True
                    # separate the metadata so that in the creation phase they are ready to be analysed
                    # elif entity_group != 'type':
                    #     if entity_group == 'volume':
                    #         series_var = True

                        # the fields, if not present should not be identified, else counted as an empty data
                    word = group["word"]["raw"]
                    if group["word"]["segmented"]:
                        word = group["word"]["segmented"]

                    all_meta.append((entity_group, word))

                    # print(all_meta)
                add_listbibl(outtree, data.index(ref), all_meta, analytic_var, series_var)
            add_to_xml(outtree, outfile)

    except FileNotFoundError:
        sys.exit('No file found: {}'.format(infile)+'. Check if the filepath and the file name are correct.')


# Driver Code
# use absolute path, es. '/Users/alessiacioffi/Desktop/dhdk/tesi/gold_standard/XML_citations/AGR-BIO-SCI_1.xml'
if __name__ == "__main__":
    # change the input XML so to call create_tei_xml
    # filename = os.path.splitext('paper_test.cermxml')[0]
    fnames = glob('D:/Projects/Masterarbeit/evaluation/references_extraction_DATA/output_files/bibex/*.json')
    for fname in fnames:
        filename = os.path.basename(fname)
        filename = "NEU_42.json"
        only_name = os.path.splitext(filename)[0]
        # path to the folder of the output directory: use absolute path, e.g. /Users/alessiacioffi/Desktop/dhdk/tesi/conversion_to_TEI/scholarcy
        out_path = 'D:/Projects/Masterarbeit/evaluation/references_extraction_DATA/goldStand_parsed/parsed_output_files/bibex/'
        # path to the folder of the output directory: use absolute path, es. /Users/alessiacioffi/Desktop/dhdk/tesi/gold_standard/XML_citations
        in_path = 'D:/Projects/Masterarbeit/evaluation/references_extraction_DATA/output_files/bibex/'
        # launch the filling function with the path of the input xml and the one of the output xml
        anystyle_parser(in_path+filename, out_path+only_name+"_tei.xml")
