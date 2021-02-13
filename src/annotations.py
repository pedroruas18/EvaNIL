import csv
import json
import os
import multiprocessing
import sys
import time
import xml.etree.ElementTree as ET
from kbs import KnowledgeBase
from functools import partial

sys.path.append("./")


def add_annotation_to_output_dict(file_id, annotation, output_dict):
    """Updates output_dict with given annotation"""

    if file_id in output_dict.keys(): 
        current_annotations = output_dict[file_id]
        current_annotations.append(annotation)
        output_dict[file_id] = current_annotations
                          
    else:
        output_dict[file_id] = [annotation]

    return output_dict

    
def parse_PBDMS_doc(kb_data, doc_dict):
    """Parse MeSH annotations in given document from PBDMS dataset.

    Args
        kb_data (KnowledgeBase): instance of the referred class representing a given knowledge base 
        doc_dict (dict): contains data from PBDMS split file in dict format
        
    Returns
        output_PBDMS (list): has format [(annotation_str, start_pos, end_pos,  mesh_id, direct_ancestor)]
    """

    doc_dict_up = json.loads(doc_dict)
    doc_id = doc_dict_up["_id"]
    
    if len(doc_dict_up['mentions']) > 0: #current doc will be present in the final dataset   
        output_PBDMS = [doc_id] 

        for mention in doc_dict_up['mentions']:
            mesh_id = mention['mesh_id'] 
                                                    
            if mesh_id in kb_data.child_to_parent.keys():
                direct_ancestor = "MESH:" + kb_data.child_to_parent[mesh_id].strip("MESH:")
                update_mesh_id =  "MESH:" + mesh_id
                annotation = (mention['mention'], mention['start_offset'], mention['end_offset'], 
                                                    update_mesh_id, direct_ancestor)
                output_PBDMS.append(annotation)
    
    if len(output_PBDMS)<=1 and len(output_PBDMS[0]) == 1:
        output_PBDMS = list()
    
    return output_PBDMS


def structure_PBDMS_annotations(documents, kb_data):
    """Parallel implementation of the function parse_PBDMS_doc

    Args
        documents (list): includes documents retrieved from PBDMS file (str) 
        kb_data (KnowledgeBase): instance of the referred class representing a given knowledge base 

    Returns
        doc_annotations (list): each element is a document including the respective valid annotations to output 
    """
    
    doc_annotations = list()
    partial_func = partial(parse_PBDMS_doc, kb_data)
        
    with multiprocessing.Pool(processes=10) as pool:
        doc_annotations = pool.map(partial_func, documents)
    
    return doc_annotations


def convert_PBDMS_into_dict(doc_annotations):
    """Convert annotations built from PBDMS dataset into final output dict.

    Args
        doc_annotations (list): has format [(annotation 1), (annotation 2), ...]

    Returns
        output_PBDMS (dict): has format {file_id: [(annotation_str, start_pos, end_pos,  mesh_id, direct_ancestor)]}
    """

    output_PBDMS = dict()

    for doc in doc_annotations:
        
        if len(doc) > 1:
            doc_annot = [annot for annot in doc if type(annot) != str]
            output_PBDMS[doc[0]] = doc_annot
    
    return output_PBDMS


def parse_NCBI_disease(kb_data):
    """Parse MeSH annotations in NCBI Disease corpus.
        
    Args
        kb_data (KnowledgeBase): instance of the referred class representing a given knowledge base 
        
    Returns
        output_NCBI_Disease (dict): has format {file_id: [(annotation_str, start_pos, end_pos,  mesh_id, direct_ancestor)]}
    """

    print("Parsing NCBI Disease corpus...")
    output_NCBI_disease = dict()
    corpus_dir = "./retrieved_data/corpora/NCBI_disease_corpus/"
    filenames = ["NCBItrainset_corpus.txt", "NCBIdevelopset_corpus.txt", "NCBItestset_corpus.txt"]

    for filename in filenames:
            
        with open(corpus_dir + filename, 'r', encoding="utf-8") as corpus_file:
            data = corpus_file.readlines()
            corpus_file.close()
                
            for line in data:
                line_data = line.split("\t")
                file_id = line_data[0]
                    
                if len(line_data) == 6:
                    mesh_id = line_data[5].strip("\n")
            
                    if mesh_id in kb_data.child_to_parent.keys():  
                        direct_ancestor =  kb_data.child_to_parent[mesh_id].strip("MESH:")
                        update_mesh_id = line_data[5].strip("MESH:").strip("\n")
                        annotation = (line_data[3], line_data[1], line_data[2], update_mesh_id, direct_ancestor)
                        output_NCBI_disease = add_annotation_to_output_dict(file_id, annotation, 
                                                                                            output_NCBI_disease)
       
    print("...Done!")
    return output_NCBI_disease

    
def parse_BC5CDR(kb_data):
    """Parse MeSH annotations in BC5CDR corpus.
        
    Args
        kb_data (KnowledgeBase): instance of the referred class representing a given knowledge base  
        
    Returns
        output_BC5CDR (dict): has format {file_id: [(annotation_str, start_pos, end_pos,  mesh_id, direct_ancestor)]}
    """

    print("Parsing BC5CDR corpus...")
    output_BC5CDR = dict()

    if kb_data.kb == "medic":
        entity_type = "Disease"
        
    elif kb_data.kb == "ctd_chemicals":
        entity_type = "Chemical"

    corpus_dir = "./retrieved_data/corpora/BioCreative-V-CDR-Corpus/CDR_Data/CDR.Corpus.v010516/"  
    filenames = ["CDR_TrainingSet.PubTator.txt", "CDR_DevelopmentSet.PubTator.txt", "CDR_TestSet.PubTator.txt"]

    for filename in filenames:
        with open(corpus_dir + filename, 'r', encoding="utf-8") as corpus_file:
            data = corpus_file.readlines()
            corpus_file.close()

            for line in data:
                line_data = line.split("\t")
                file_id = line_data[0]
                    
                if len(line_data) == 6 and line_data[4] == entity_type:
                    mesh_id = "MESH:" + line_data[5].strip("\n")  
                        
                    if mesh_id in kb_data.child_to_parent.keys():
                        direct_ancestor = "https://id.nlm.nih.gov/mesh/" \
                                                + kb_data.child_to_parent[mesh_id].strip("MESH:")
                        update_mesh_id = "https://id.nlm.nih.gov/mesh/" + line_data[5].strip("MESH:").strip("\n")
                        annotation = (line_data[3], line_data[1], line_data[2], update_mesh_id, direct_ancestor)
                        output_BC5CDR = add_annotation_to_output_dict(file_id, annotation, output_BC5CDR)

    print("...Done!")
    return output_BC5CDR

   
def parse_CRAFT(kb_data):
    """Parse annotations ChEBI or GO annotations in CRAFT corpus. 

    Args
        kb_data (KnowledgeBase): instance of the referred class representing a given knowledge base 
        
    Returns
        output_CRAFT (dict): has format {file_id: [(annotation_str, start_pos, end_pos, kb_id, direct_ancestor)]}
    """

    print("Parsing CRAFT corpus...")
    corpus_dir = str()
        
    if kb_data.kb == "chebi":
        corpus_dir = "./retrieved_data/corpora/CRAFT-4.0.1/concept-annotation/CHEBI/CHEBI/knowtator/"
        
    elif kb_data.kb == "go_bp":
        corpus_dir = "./retrieved_data/corpora/CRAFT-4.0.1/concept-annotation/GO_BP/GO_BP/knowtator/"

    output_CRAFT = dict()
        
    for document in os.listdir(corpus_dir): 
        root = ET.parse(corpus_dir + document)
        file_id = document.strip('.txt.knowtator.xml')
        annotations = dict()

        for annotation in root.iter("annotation"):
            annotation_id = annotation.find('mention').attrib['id']
            annotation_text = annotation.find('spannedText').text
            start_pos, end_pos = annotation.find('span').attrib['start'], annotation.find('span').attrib['end']
            annotations[annotation_id] = [annotation_text, start_pos, end_pos] 
                
        for classMention in root.iter("classMention"):
            classMention_id = classMention.attrib['id']
            annotation_values = annotations[classMention_id]
            kb_id = classMention.find('mentionClass').attrib['id']
                    
            if kb_id in kb_data.child_to_parent.keys(): # Consider only KB concepts with ONE direct ancestor
                direct_ancestor = kb_data.child_to_parent[kb_id]
                annotation = (annotation_values[0], annotation_values[1], 
                                annotation_values[2], kb_id, direct_ancestor) 
                output_CRAFT = add_annotation_to_output_dict(file_id, annotation, output_CRAFT)
                    
    print("...Done!")
    return output_CRAFT

   
def parse_MedMentions(kb_data):
    """Parse UMLS annotations from MedMentions corpus and convert them to HPO annotations.
        
    Args
        kb_data (KnowledgeBase): instance of the referred class representing a given knowledge base 

    Returns
        output_MedMentions (dict): has format {file_id: [(annotation_str, start_pos, end_pos, hp_id, direct_ancestor)]}
    """
    
    print("Parsing MedMentions corpus...")
    output_MedMentions = dict()
    filepath = "./retrieved_data/corpora/MedMentions/corpus_pubtator.txt"
    
    with open(filepath, 'r', buffering=1, encoding="utf-8") as corpus_file:

            for line in corpus_file:
                if "|t|" not in line and "|a|" not in line and line != "\n":
                    doc_id = line.split("\t")[0]
                    annotation_str = line.split("\t")[3]
                    umls_id =line.split("\t")[5].strip("\n")
                    start_pos, end_pos = line.split("\t")[1], line.split("\t")[2]
                        
                    if umls_id in kb_data.umls_to_hp.keys(): # UMLS concept has an equivalent HPO concept
                        hp_id = kb_data.umls_to_hp[umls_id]

                        if hp_id in kb_data.child_to_parent.keys(): # Consider only HPO concepts with ONE direct ancestor
                            direct_ancestor = kb_data.child_to_parent[hp_id].strip("\n")
                            annotation = (annotation_str, start_pos, end_pos, hp_id, direct_ancestor)
                            output_MedMentions = add_annotation_to_output_dict(doc_id, annotation, output_MedMentions)
    
    corpus_file.close()

    print("...Done!")
    return output_MedMentions

    
def parse_PGR(kb_data):
    """Parse HPO annotaitons in PGR corpus.

    Args
        kb_data (KnowledgeBase): instance of the referred class representing a given knowledge base  

    Returns
        output_PGR (dict): has format {file_id: [(annotation_str, start_pos, end_pos, hp_id, direct_ancestor)]}
    """

    print("Parsing  corpus...")
    output_PGR = dict()
    filepaths = ["./retrieved_data/corpora/PGR/train.tsv", "./retrieved_data/corpora/PGR/test.tsv"]

    for filepath in filepaths:
            
        with open(filepath, encoding="utf-8") as corpus_file:
            reader = csv.reader(corpus_file, delimiter="\t")
            row_count = int()

            for row in reader:
                row_count += 1
                    
                if row_count > 1: # Skip the header
                    doc_id = row[0]
                    annotation_str = row[3]
                    hp_id = row[5].replace("_", ":")
                    start_pos, end_pos = row[8], row[9]

                    if hp_id in kb_data.child_to_parent.keys(): # Only consider concept ids with ONE direct ancestor
                        direct_ancestor = kb_data.child_to_parent[hp_id]
                        annotation = (annotation_str, start_pos, end_pos, hp_id, direct_ancestor)
                        output_PGR = add_annotation_to_output_dict(doc_id, annotation, output_PGR)
    
    print("...Done!")         
    return output_PGR


def parse_annotations(kb, split):
    """Wrapper function to build the output dict specified by arg 'kb' (str)"""

    obo_list = ["hp", "chebi", "medic", "go_bp"] 
    tsv_list = ["ctd_chemicals", "ctd_anatomy"]
    kb_data = KnowledgeBase(kb)
    out_dict = dict()

    if kb in obo_list:
        kb_data.load_obo(kb_data.kb)        

        if kb == "hp":
            output_MedMentions= parse_MedMentions(kb_data)
            output_PGR = parse_PGR(kb_data)
            out_dict = {**output_PGR, **output_MedMentions} # Merge two dicts
            
        elif kb == "medic":
            documents = list()
            print("Parsing PBDMS ( split", str(split), ")...")
            begin_time_split = time.time()
            
            with open("./retrieved_data/corpora/pubmed_ds/split_" + split + ".txt", 'r', buffering=1, encoding="utf-8") as input_split:
                documents = [doc for doc in input_split]
                input_split.close()
            
            doc_annotations = structure_PBDMS_annotations(documents, kb_data)
            
            output_PBDMS = convert_PBDMS_into_dict(doc_annotations)
            

            if split == "1": #Split 1 contains documents from PBDMS, NCBI disease, and BC5CDR corpora
                output_NCBI_disease = parse_NCBI_disease(kb_data)
                output_BC5CDR = parse_BC5CDR(kb_data)
                out_dict = {**output_PBDMS, **output_NCBI_disease, **output_BC5CDR}
                   
            else:
                out_dict = output_PBDMS 
            
            total_time = time.time() - begin_time_split
            print("...Done!\nRuntime for split", str(split), ":", str(round(total_time, 3)), "s")

        elif kb == "chebi":
            out_dict = parse_CRAFT(kb_data)
            
        elif kb == "go_bp":
            out_dict = parse_CRAFT(kb_data)

    elif kb in tsv_list:    
        kb_data.load_tsv(kb_data.kb)
        documents = list()
        print("Parsing PBDMS ( split", str(split), ")...")
        begin_time_split = time.time()

        with open("./retrieved_data/corpora/pubmed_ds/split_" + split + ".txt", 'r', buffering=1, encoding="utf-8") as input_split:
            documents = [doc for doc in input_split]
            input_split.close()
        
        doc_annotations = structure_PBDMS_annotations(documents, kb_data)
        output_PBDMS = convert_PBDMS_into_dict(doc_annotations)

        if kb == "ctd_chemicals" and split == "1":  
            output_BC5CDR = parse_BC5CDR(kb_data)
            out_dict = {**output_PBDMS, **output_BC5CDR}
                       
        else:
            out_dict = output_PBDMS
        
        total_time = time.time() - begin_time_split
        print("...Done!\nRuntime for split", str(split), ":", str(round(total_time, 3)), "s")
        
    return out_dict













  