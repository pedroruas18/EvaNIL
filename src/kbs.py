import csv
import obonet
import sys

sys.path.append("./")

class KnowledgeBase:
    """Class representing a knowledge base.
    
    Attributes
    ----------
        kb (str): the knowledge base to represent, including "hp", "medic", "ctd_anatomy", "ctd_chemicals", "chebi", "go_bp" 
    
    Methods
    -------
        __init__(self, kb)
        load_obo(self, kb)
        load_tsv(self, kb)
    """

    global name_to_id, synonym_to_id, child_to_parent, umls_to_hp
    name_to_id, synonym_to_id, child_to_parent, umls_to_hp = dict(), dict(), dict(), dict()

    def __init__(self, kb):
        self.kb = kb
    
    def load_obo(self, kb):
        """Loads KBs from .obo files (ChEBI, HPO, MEDIC, GO) into structured dicts.
        
        Args 
            kb (str): selected ontology to load, has value "medic", "chebi", "go_bp" or "hp"

        Returns
            name_to_id (dict):
            synonym_to_id (dict): 
            child_to_parent (dict):
            umls_to_hp (dict): has format {"UMLS id": "HPO id"}
        """
        print("---------------------\nLoading", kb, "...")
        corpus_dir = "./retrieved_data/kb_files/"
        filepaths = {"medic": "CTD_diseases", "chebi": "chebi_lite", "go_bp": "go-basic"}
        
        if kb in filepaths.keys():
            filepath = "./retrieved_data/kb_files/" + filepaths[kb] + ".obo"    
        else:
            filepath = "./retrieved_data/kb_files/" + kb + '.obo'
        
        graph = obonet.read_obo(filepath)
        
        for node in  graph.nodes(data=True):
            add_node = True
            
            if "name" in node[1].keys():
                node_id, node_name = node[0], node[1]["name"]

                if kb == "go_bp": #For go_bp, ensure that only Biological Process concepts are considered
                    
                    if node[1]['namespace'] == 'biological_process':
                        name_to_id[node_name] = node_id
                    else:
                        add_node = False
                
                else:

                    if kb == "medic":

                        if node_id[0:4] != "OMIM": #exclude OMIM concepts
                            node_id = node_id.strip("MESH:")
                            name_to_id[node_name] = node_id
                    
                    else:
                        name_to_id[node_name] = node_id

                if 'is_a' in node[1].keys() and add_node: # The root node of the ontology does not have is_a relationships

                    if len(node[1]['is_a']) == 1: # Only consider concepts with ONE direct ancestor
                        child_to_parent[node_id] = node[1]['is_a'][0]
                
                if "synonym" in node[1].keys() and add_node: # Check for synonyms for node (if they exist)
                        
                    for synonym in node[1]["synonym"]:
                        synonym_name = synonym.split("\"")[1]
                        synonym_to_id[synonym_name] = node_id

                if "xref" in node[1].keys() and add_node:

                    if kb == "hp": #map UMLS concepts to HPO concepts
                        umls_xrefs = list()

                        for xref in node[1]['xref']:
                            if xref[:4] == "UMLS":
                                umls_id = xref.strip("UMLS:")
                                umls_to_hp[umls_id] =  node_id 

        self.name_to_id = name_to_id
        self.synonym_to_id = synonym_to_id
        self.child_to_parent = child_to_parent
        self.umls_to_hp = umls_to_hp
        print("...", kb, "loaded!")

    def load_tsv(self, kb):
        """Loads KBs from .tsv files (CTD-Chemicals, CTD-Anatomy) into structured dicts"""

        print("---------------------\nLoading", kb, "...")
        kb_dict = {"ctd_chemicals": "CTD_chemicals", "ctd_anatomy": "CTD_anatomy"}
        filepath = "./retrieved_data/kb_files/" + kb_dict[kb] + ".tsv"
        
        with open(filepath) as kb_file:
            reader = csv.reader(kb_file, delimiter="\t")
            row_count = int()
        
            for row in reader:
                row_count += 1
                
                if row_count >= 30:
                    node_name = row[0] 
                    node_id = row[1][5:] # "MESH:" + 
                    node_parents = row[4].split('|')
                    synonyms = row[7].split('|')
                    name_to_id[node_name] = node_id
                    
                    if len(node_parents) == 1: ## Only consider concepts with ONE direct ancestor
                        child_to_parent[node_id] = node_parents[0]
                    
                    for synonym in synonyms:
                        synonym_to_id[synonym] = node_id
        
        self.name_to_id = name_to_id
        self.synonym_to_id = synonym_to_id
        self.child_to_parent = child_to_parent
        print("...", kb, "loaded!")
      


