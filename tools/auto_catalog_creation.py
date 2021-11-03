# -*- coding: utf-8 -*-
import os
import yaml
from copy import deepcopy
from lxml import etree
from lxml.etree import Element

def main():
    root = read_xml("all_questions.xml")
    life_cycle_content = read_yaml("cat_member.yaml")
    cat_list = []
    cat_list_tmp = []
    for cat_vars in life_cycle_content["catalogs"]:
        cat_list.append(make_root(cat_vars))

    # for now this is the global namespace
    xmlns = "{http://purl.org/dc/elements/1.1/}"
    xml_nsmap = root.nsmap

    for question in root.iterchildren("question"):
        # finding the questionset of the question
        qset_uri = question.find("questionset").get(xmlns + "uri")
        qset_xpath = ".questionset[@dc:uri='" + qset_uri + "']"
        qset = root.find(qset_xpath, xml_nsmap)

        # finding the section of the questionset
        sec_uri = qset.find("section").get(xmlns + "uri")
        sec_xpath = ".section[@dc:uri='" + sec_uri + "']"
        sec = root.find(sec_xpath, xml_nsmap)

        for n, cat_info in enumerate(life_cycle_content["catalogs"]):
            # use path as key for check of membership to catalog
            if life_cycle_content[question.find("path").text][cat_info[0]]:
                # check if qset and sec are already in catalog
                if cat_list[n].find(qset_xpath, xml_nsmap) == None:
                    if cat_list[n].find(sec_xpath, xml_nsmap) == None:
                        tmp_sec = change_path(sec, cat_info[0])
                        cat_list[n].append(deepcopy(tmp_sec))
                    tmp_qset = change_path(qset, cat_info[0])
                    cat_list[n].append(deepcopy(tmp_qset))
                tmp_question = change_path(question, cat_info[0])
                # sort the questions below their respective questionsets
                cat_qset = cat_list[n].find(qset_xpath, xml_nsmap)
                index = cat_list[n].index(cat_qset)
                cat_list[n].insert(index+1, deepcopy(tmp_question))
            else:
                continue

    write_catalogs(cat_list, life_cycle_content["catalogs"])
    change_uri(life_cycle_content["catalogs"])

def write_catalogs(cat_list, name_list):
    # takes a list of root elements and file names and writes them to the specified
    # relative directory
    for n, cat in enumerate(cat_list):
        tree = etree.ElementTree(cat)
        tree.write("../rdmorganiser/questions/" + name_list[n][0] + ".xml",
                    xml_declaration=True, encoding="UTF-8")

def change_path(element, name):
    # takes an etree.Element and catalog key and changes the path variable of
    # the element
    element = deepcopy(element)
    path = element.find("path")
    remove_index = path.text.find("/")
    path.text = path.text.lstrip(path.text[0:remove_index])
    path.text = name + path.text
    return element

def change_uri(name_list):
    # this is rather a workaround than a solution, but prefixes on Attributes make things
    # unnecessary hard to access and change
    default_uri = "https://rdmorganiser.github.io/terms/questions/ua_ruhr"
    for name in name_list:
        cat = open("../rdmorganiser/questions/" + name[0] + ".xml", "r", encoding="UTF-8")
        lines = cat.readlines()
        cat.close()
        cat = open("../rdmorganiser/questions/" + name[0] + ".xml", "w", encoding="UTF-8")
        for line in lines:
            if default_uri in line:
                line = line.replace("ua_ruhr", name[0])
            cat.write(line)
        cat.close()

def make_root(cat_vars):
    # takes a list of catalog variables [key, name] and generates a root element
    # with a predefined name space among other informations
    XHTML_NAMESPACE = "http://purl.org/dc/elements/1.1/"
    XHTML = "{%s}" % XHTML_NAMESPACE
    NSMAP = {"dc":XHTML_NAMESPACE} # the default namespace with prefix
    root = etree.Element("rdmo", nsmap=NSMAP) # lxml only!
    root.append(etree.fromstring("""
        <catalog xmlns:dc="http://purl.org/dc/elements/1.1/" dc:uri="https://rdmorganiser.github.io/terms/questions/ua-ruhr">
		<uri_prefix>https://rdmorganiser.github.io/terms</uri_prefix>
		<key></key>
		<dc:comment/>
		<order>0</order>
		<title lang="en"></title>
		<title lang="de"></title>
	    </catalog>
        """))
    root[0][1].text = cat_vars[0]
    root[0][4].text = cat_vars[1]
    root[0][5].text = cat_vars[2]
    return root

def read_yaml(file_name):
    # reads in a yaml file and returns the content of it
    data_file = open(os.path.abspath(file_name), "r")
    content = yaml.safe_load(data_file)
    return content

def read_xml(file_name):
    # reads in a xml file and returns it as etree.Element
    tree = etree.parse(os.path.abspath(file_name))
    root = tree.getroot()
    return root

if __name__ == "__main__":
    main()
