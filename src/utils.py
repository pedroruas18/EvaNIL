import json
import os
import sys

sys.path.append("./")


def retrieve_annotations(partition, test):
    """Retrieves annotations from chosen partition of EvaNIL dataset into dict.
    
    Args
        partition (str): has value "medic", "ctd_anatomy", "ctd_chemicals", "chebi", "go_bp" or "hp"
        test (bool): "True" to retrieve only annotation from test set, "False" otherwise
    
    Returns
        annotations (dict): has format {file_id: [(annotation_str, start_pos, end_pos, hp_id, direct_ancestor)]}
    """
    
    annotation_files = list()
    has_pbmds_files = ["medic", "ctd_anatomy", "ctd_chemicals"]
    corpus_dir = "./dataset/" + partition + "/"
    annotations = dict()

    if partition in has_pbmds_files:
        
        for split in range(1, 30): 
            corpus_dir_temp = corpus_dir + "split_" + str(split) + "/"
            
            if test:
                test_filepath = corpus_dir_temp + "test.json"
                annotation_files.append(test_filepath)
            
            else:
                annotation_files_temp = [corpus_dir_temp + filepath for filepath in os.listdir(corpus_dir_temp)]
                annotation_files.extend(annotation_files_temp)

    elif partition not in has_pbmds_files:

        if test:
            annotation_files = [corpus_dir + "test.json"]
        
        else:
            annotation_files_temp = os.listdir(corpus_dir)
            annotation_files = [corpus_dir + filepath for filepath in annotation_files_temp]

    for annot_file in annotation_files:
        
        with open(annot_file, 'r') as in_file:
            data = json.load(in_file)
            annotations.update(data)
        
    return annotations