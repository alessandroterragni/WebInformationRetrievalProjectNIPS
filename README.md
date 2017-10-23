# Web Information Retrieval Project NIPS

Alessandro Terragni | Robin Esposito | Luis Galdo Seara | Juan González | Xin Ma | Nazly Santos Buitrago  

TU\e Eindhoven, Web Information Retrieval And Data Mining, Prof: Mykola Pechenizkiy

## Project idea
The goal of this project is to develop an Information Retrieval (IR) system that supports basic functionalities, including keyword search (based on Boolean and Vector Space retrieval), query by example search (finding docs similar to a chosen doc), parametric search (specify where to search for keywords and docs in which language).

### Data
The data used for this project are the papers presented in NIPS conferences from 1987 until 2016. Data was extracted from Kaggle.
Moreover, other data from the authors such as H-index from Microsoft Academic and Google Scholar was crawled. In addition, information regarding the institution the authors belong to was crawled from Google Scholar.


## Achieved functionality
The team has managed to make a functionable web page (http://www.cimics.nl). Two search engines based on different languages and search algorithms have been implemented. The first one uses Java (Lucene) and the second one a Python library (Whoosh).
The final user can make queries based on papers, either metadata (year, author, topic) or content from the text, or based on authors (name, institution, topic). The content of the papers has been indexed using TF-IDF.
Topics have been extracted from the papers using two different algorithms (LDA and NMF). 
Information regarding the authors (h-index, institutions) has been extracted from Google Scholar and Microsoft Academic. The authors are ranked by PageRank (using the citations and collaborations between authors inside NIPS papers) and by H-index (from Microsoft Academic and Google Scholar).
Several clusters have been created using the aggregated information. In particular, there are four different types of authors clusters based on: collaborations between authors, text of their papers, topics of their papers, institutions and the topics of the papers that were written by authors belonging to those institutions.
In addition, the website contains a page where a comparison between the two algorithms of topic extraction is performed.
Some graphs related to topics, topics evolution and different topics of each author throughout the years are also included.

## FILES TO ADD TO THE REPOSITORY

Some files were too big to upload on github. 
You must download it from this link: https://drive.google.com/open?id=0B2M2nfKXpDMHZTM1NHZ2OFZpbTg

Put these files in data/original
- papers.csv        
- papers.json    

Put these files in data/generated/database    
- database.sqlite
 
Put these files in the website folder:
- database.sqlite
- index



