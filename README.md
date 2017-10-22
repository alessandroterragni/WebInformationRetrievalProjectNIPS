# Web Information Retrieval Project NIPS

Alessandro Terragni | Robin Esposito | Luis Galdo Seara | Juan González | Xin Ma | Nazly Santos Buitrago  

TU\e Eindhoven, Web Information Retrieval And Data Mining, Prof: Mykola Pechenizkiy

## Project idea
The goal of this project is to develop an Information Retrieval (IR) system that supports basic functionality, including keyword search (based on Boolean and Vector Space retrieval), query by example search (finding docs similar to a chosen doc), parametric search (specify where to search for keywords and docs in which language).	

### Data
The data used for this project are the papers presented in NIPS conferences from 1987 until 2016. Data was extracted from Kaggle: https://www.kaggle.com/benhamner/nips%E2%80%90papers .
Also, other data from the authors such as H-index from Microsoft Academic and Google Scholar was crawled. Also, information regarding the institution to where the authors belong to was crawled from Google Scholar.

## Achieved functionality
The team has managed to make a functionable web page (http://www.cimics.nl) where a search engine is implemented. Two search engines based on different languages and search algorithms have been implemented. The first one uses Java (Lucene) and the second one a Python library (Whoosh).
The final user can make queries based on papers, either metadata (author, topic) or content from the text, or based on authors (name, institution, topic). The content of the papers has been indexed using TF.IDF [include links].
Topics have been extracted from the papers using two different algorithms (LDA and NMF). 
Information regarding the authors (h-index, institutions) has been extracted from Google Scholar [include link] and Microsoft Academic [include link].
The authors can be ranked based on the PageRank (using the citations between authors inside NIPS papers) or in H-index (either from Microsoft Academic or Google Scholar).
Several clusters have been created using the known info. There are four different types of clusters based on::
Collaborations between authors
Authors and the content of their papers
Authors and the topic of their papers
Institutions and the topics of the papers that were written by authors belonging to those institutions.
Also, the web page contains a page where a comparison between the two algorithms of topic extraction is performed.
Some graphs related to topics, topics evolution and different topics of each author throughout the years are included in the web page.

## FILES TO ADD TO THE REPOSITORY

Some files were too big to upload on github. 
You must download it from this link: https://drive.google.com/open?id=0B2M2nfKXpDMHZTM1NHZ2OFZpbTg

Put these files in data/original
- papers.csv        
- papers.json    

Put these files in data/generated/database    
- database.sqlite
 



