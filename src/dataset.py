import json
import os
import random
import sys
import time
from annotations import parse_annotations

sys.path.append("./")


def split_partition(annotations):
    """Randomly split annotations into train (80%), dev (10%), and test (10%) sets"""

    train_annotations = dict()
    dev_annotations = dict()
    test_annotations = dict()            
    doc_names = list(annotations.keys()) 
    random.seed(100) #To ensure the shuffle always return the same result (allows reproducibility)
    random.shuffle(doc_names)
        
    split_1 = int(0.8 * len(doc_names))
    split_2 = int(0.9 * len(doc_names))

    train_doc_names = doc_names[:split_1]
    dev_doc_names = doc_names[split_1:split_2]
    test_doc_names = doc_names[split_2:]
    
    for doc in train_doc_names:
        train_annotations[doc] = annotations[doc]
        
    for doc in dev_doc_names:
        dev_annotations[doc] = annotations[doc]
        
    for doc in test_doc_names:
        test_annotations[doc] = annotations[doc]

    return train_annotations, dev_annotations, test_annotations


def build_partition(annotations, partition, split):
    """Output given partition in .json files.

    Args:
        annotations (dict): has format {file_id: [(annotation_str, start_pos, end_pos, hp_id, direct_ancestor)]}
        partition (str): has value medic, ctd_anatomy, ctd_chemicals, chebi, go_bp or hp
        split(str): specifies the split of PBDMS dataset that was processed, has value "" for partitions without PBDMS docs
    
    Returns:
        train.json, dev.json, and test.json files in the respective partition directory
    """
    
    if split != "":
        partition_dir = "./dataset/" + partition + "/split_" + split + "/"
    
    else:
        partition_dir = "./dataset/" + partition+ "/"    

    if not os.path.exists(partition_dir):
        os.makedirs(partition_dir)
    
    train_annotations, dev_annotations, test_annotations = split_partition(annotations)
    subset_list = ["train", "dev", "test"]
    
    for subset in subset_list:
        
        if subset == "train":
            out_dict = json.dumps(train_annotations, indent=4, ensure_ascii=False)
        elif subset == "dev":
            out_dict = json.dumps(dev_annotations, indent=4, ensure_ascii=False)
        elif subset == "test":
            out_dict = json.dumps(test_annotations, indent=4, ensure_ascii=False)

        if not os.path.exists(partition_dir):
            os.makedirs(partition_dir)

        with open(partition_dir + subset + ".json", "w", encoding="utf-8") as out_file:
            out_file.write(out_dict)
            out_file.close()
    
    total_docs =  len(train_annotations.keys()) + len(dev_annotations.keys()) + len(test_annotations.keys())

    print("-----------OUTPUT-----------\nPARTITION: ", partition, "\tSPLIT: ", str(split), \
        "\nTOTAL DOCS: ", total_docs, "\nTRAIN: ", len(train_annotations.keys()), \
        "| DEV: ", len(dev_annotations.keys()), "| TEST: ", len(test_annotations.keys()))


if __name__ == "__main__":
    start_time = time.time()
    partition = sys.argv[1] # medic, ctd_anatomy, ctd_chemicals, chebi, go_bp, hp
    has_pbmds_files = ["medic", "ctd_anatomy", "ctd_chemicals"]

    if partition not in has_pbmds_files:   
        annotations = parse_annotations(partition, '')
        build_partition(annotations, partition, '')
    
    else: #PBDMS dataset is too large, so it is processed sequentially in splits        
        i = 1

        while i <=29: #There are 29 splits in PBDMS dataset
            annotations = parse_annotations(partition, str(i))
            build_partition(annotations, partition, str(i))
            i += 1
    
    total_time = time.time() - start_time #total_min= round((end_time-start_time)/60, 2)
    print("---------------\nTotal Runtime:", str(round(total_time, 3)), "s")


