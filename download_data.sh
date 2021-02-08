mkdir retrieved_data retrieved_data/kb_files retrieved_data/corpora

# KB files
cd retrieved_data/kb_files

wget ctdbase.org/reports/CTD_diseases.obo.gz # MEDIC
gzip -d CTD_diseases.obo.gz 

wget ctdbase.org/reports/CTD_diseases.tsv.gz # CTD-Chemicals
gzip -d CTD_diseases.tsv.gz 

wget ctdbase.org/reports/CTD_anatomy.tsv.gz # CTD-Anatomy
gzip -d CTD_anatomy.tsv.gz

wget ftp://ftp.ebi.ac.uk/pub/databases/chebi/ontology/chebi_lite.obo.gz # ChEBI
gzip -d chebi_lite.obo.gz

wget http://purl.obolibrary.org/obo/go/go-basic.obo # GO_BP
go-basic.obo 

wget https://raw.githubusercontent.com/obophenotype/human-phenotype-ontology/master/hp.obo # HPO

#-----------------------------------------------------------------------------------------------
# Corpora

cd ../corpora

# CRAFT
wget https://github.com/UCDenver-ccp/CRAFT/archive/v4.0.1.zip 
unzip CRAFT-v4.0.1.zip

# NCBI Disease corpus
mkdir NCBI_disease_corpus
cd NCBI_disease_corpus
wget https://www.ncbi.nlm.nih.gov/CBBresearch/Dogan/DISEASE/NCBIdevelopset_corpus.zip
unzip NCBIdevelopset_corpus.zip
wget https://www.ncbi.nlm.nih.gov/CBBresearch/Dogan/DISEASE/NCBItestset_corpus.zip
unzip NCBItestset_corpus.zip
wget https://www.ncbi.nlm.nih.gov/CBBresearch/Dogan/DISEASE/NCBItrainset_corpus.zip
unzip NCBItrainset_corpus.zip
cd ..

#MedMentions
mkdir MedMentions 
cd MedMentions
wget https://github.com/chanzuckerberg/MedMentions/blob/master/full/data/corpus_pubtator.txt.gz 
gzip -d corpus_pubtator.txt.gz 
cd ..

# PGR
mkdir PGR 
cd PGR
wget https://github.com/lasigeBioTM/PGR/blob/master/corpora/10_12_2018_corpus/test.tsv
wget https://github.com/lasigeBioTM/PGR/blob/master/corpora/10_12_2018_corpus/train.tsv
cd ..

#BC5CDR
wget https://codeload.github.com/JHnlp/BioCreative-V-CDR-Corpus/zip/master 
unzip master

#PubMed DS
echo "Donwload PubMed DS manually through the following link: https://drive.google.com/file/d/16mEFpCHhFGuQ7zYRAp2PP3XbAFq9MwoM/view"
