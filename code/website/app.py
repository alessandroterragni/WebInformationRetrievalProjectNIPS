from flask import Flask, render_template, url_for, request

application = Flask(__name__, static_url_path='')


# DB setup
import sqlite3
database = "../database/database.sqlite"
conn = sqlite3.connect(database)

# Plot setup
import pandas as pd
import numpy as np
import seaborn as sns
import random
import datetime


def searchPapers_whoosh(year=None, author=None, topic=None, userQuery=None):
        
    # Open the existing index
    import whoosh.index as index
    import nltk
    nltk.download('wordnet')
    from nltk.stem.wordnet import WordNetLemmatizer
    lemma = WordNetLemmatizer()
    userQuery = " ".join(lemma.lemmatize(word,'n') for word in userQuery.split())
    userQuery = " ".join(lemma.lemmatize(word,'v') for word in userQuery.split())
    index_dir = "../index"

    ix = index.open_dir(index_dir)
    
    if topic == 'All the topics':
        topic = None
    if year == 'All the years':
        year = None
    # Parse with filter on fields    
    from whoosh import query
    from whoosh import qparser
    from whoosh.qparser import QueryParser
    from whoosh.qparser import MultifieldParser

    with ix.searcher() as s:
        if(not userQuery):
            qp = QueryParser("id", schema=ix.schema)
            user_q = qp.parse("*")
            
        else:
            # 0 = importance to documents with one of the terms
            # 1 = importance to documents with all of the terms
            og = qparser.OrGroup.factory(0.8)

            # search both in title and text
            mparser = MultifieldParser(["title", "paper_text"], schema=ix.schema, group=og)
            user_q = mparser.parse(userQuery)        

        # Filter results for fields
        allow_q = query.NullQuery        
        
        if (year):
            allow_q = allow_q & query.Term("year", year)
        
        if (author):
            formattedAuthors = author.lower().split()
            for fa in formattedAuthors:
                fa = "*" + fa + "*"
                allow_q = allow_q & query.Wildcard("authors", fa)

        if (topic):
        	topicParser = qparser.QueryParser("topic", ix.schema)
        	allow_q = allow_q & topicParser.parse('"' + topic + '"')

        if (not year and not author and not topic):
            results = s.search(user_q, limit=50)
        else:
            results = s.search(user_q, filter=allow_q, limit=50)
        
        papers = []
        for result in results:
            papers.extend([int(result['id'])])
        return papers



def searchAuthors_whoosh(name=None, institution=None, topic=None):
    
    l = []
    likeName = '%' + name.upper() + '%' if (name) else None 
    likeInstitution = '%' + institution.upper() + '%' if (institution) else None
    if topic == 'All the topics':
        topic = None
    topic = topic if (topic) else None
    
    with conn:
        cur = conn.cursor()
        cur.execute("SELECT a.id " + 
                    "FROM authors a JOIN paper_authors pa ON a.id=pa.author_id JOIN paper_topic pt ON pt.paper_id=pa.paper_id " + 
                    "JOIN topics t ON t.id=pt.topic_id LEFT JOIN author_institution ai ON ai.author_id=a.id LEFT JOIN institutions i ON i.id=ai.institution_id " + 
                    "JOIN author_ranking ar on ar.author_id=a.id " +
                    "WHERE a.name LIKE IFNULL(?,'%') AND IFNULL(i.name,'') LIKE IFNULL(?,'%') AND t.name = IFNULL(?,t.name) " +
                    "GROUP BY a.id, ar.pagerank_citations ORDER BY ar.pagerank_collaborations DESC", (likeName, likeInstitution, topic))
        
        rows = cur.fetchall()
        
        for row in rows:
            l.extend(row)
            
    return(l)
	

def searchAuthors_lucene(name=None, institution=None,topic=None,mix=None):
    import requests
    import json
    result = []
    s = requests.Session()
    if topic == 'All the topics':
        topic = None
    else:
        with conn:
	        cur = conn.cursor()
	        cur.execute("SELECT id FROM topics WHERE name = ?", (topic,))
	        rows = cur.fetchall()
	        for row in rows:
	    	    topic = row[0]
    url = 'http://18.220.42.182:8080/nips-RESTService/api/getauthor/para?'
    if name:
        url += ('name='+name+'&')
    if institution:
        url += ('inst='+institution+'&')
    if topic:
        url += ('topic='+str(topic)+'&')
    if mix:
        url += ('mix='+mix+'&')
    with open('somefile.txt', 'wt') as f:
        f.write(url)
    r = s.get(url[:-1])
    jsonData = json.loads(r.text)
    for author in jsonData:
        result.append(author['id'])
    return result


def searchPapers_lucene(fromY=None, toY =None, author=None, topic=None, userQuery=None,qm=None):
    import requests
    import json
    result = []
    s = requests.Session()
    if topic == 'All the topics':
        topic = None
    else:
        with conn:
	        cur = conn.cursor()
	        cur.execute("SELECT id FROM topics WHERE name = ?", (topic,))
	        rows = cur.fetchall()
	        for row in rows:
	    	    topic = row[0]
    url = 'http://18.220.42.182:8080/nips-RESTService/api/getpaper/para?'
    if fromY:
        url += ('bYear='+fromY+'&')
    if toY:
        url += ('eYear='+toY+'&')
    if author:
        url += ('author='+author+'&')
    if topic:
        url += ('topic='+str(topic)+'&')
    url += ('searchType='+qm+'&')

    if (qm == "boolean"):
        for sss in userQuery.split(' '):
            url += (sss.split('=')[0]+'='+sss.split('=')[1]+'&')
    else:
        if userQuery:
            url += ('sentence'+'='+userQuery+'&')
    r = s.get(url[:-1])
    
    with open('somefile.txt', 'wt') as f:
        f.write(r.text)
        f.write(url)
    
    jsonData = json.loads(r.text)
    for author in jsonData:
        result.append(author['id'])
    return result

def plot_topic_author(df,a_id):
    import matplotlib
    import matplotlib.pyplot as plt
    df_1 = df.loc[df['author_id'] == a_id]
    df_2 = df_1.groupby(['year'])['paper_id'].agg(['count']).reset_index()
    df_3 = pd.merge(df_1, df_2, on=['year'],left_index=False, right_index=False)
    #sns.set_style("whitegrid")
    plt.figure(figsize=(14,6))
    sns_plot = sns.barplot(x="year", y="count", hue="topic", data=df_3)
    sns_plot.legend(ncol=1, loc="upper left", frameon=True)
    sns.despine(left=True, bottom=True)
    
    plt.savefig('static/plot_topic_author.png')

def to_integer(dt_time):
    return 10000*dt_time.year + 100*dt_time.month + dt_time.day

@application.route("/")
def index():
	urls = {'get-papers': url_for('resultPapers'), 'get-authors': url_for('resultAuthors')}
	years = []
	topics = []

	with conn:
	    cur = conn.cursor()
	    cur.execute("SELECT year FROM papers GROUP BY year")
	    rows = cur.fetchall()
	    for row in rows:
	    	years.extend([int(row[0])])

	    cur = conn.cursor()
	    cur.execute("SELECT name FROM topics")
	    rows = cur.fetchall()
	    for row in rows:
	    	topics.extend([row[0]])

	return render_template('index.html', urls = urls, years = years, topics = topics)


@application.route('/result-papers', methods = ['POST', 'GET'])
def resultPapers():
    if request.method == 'POST':
        year = request.form['year']
        author = request.form['author']
        topic = request.form['topic']
        query = request.form['query']
        method = request.form['method']
        fromY = request.form['from']
        toY = request.form['to']
        mix = request.form['mixMethod']
        qm = request.form['QMethod']
        paperIds = []
        papers = []
        topicid = 0

        if (method=="lucene"):
            if (topic == "All the topics"):
                topic = None
            else:
               with conn:
                    cur = conn.cursor()
                    cur.execute("select id from topics where name=?",(topic,))
                    row = cur.fetchone()
                    topicid = row[0]

        if (method == "whoosh"):
            paperIds = searchPapers_whoosh(year=year, author=author, topic=topic, userQuery=query)
        elif (method == "lucene"):
            try:
                paperIds = searchPapers_lucene(fromY=fromY, toY=toY, author=author, topic=topicid, userQuery=query, qm=qm)
            except:
                paperIds = []

        with conn:
            cur = conn.cursor()
            cur.execute("select id, query_times from search_record WHERE query_string = ? and search_type='paper'",(query,))
            row = cur.fetchone()
            
            if row:
                cur.execute("update search_record set query_times = ?, latest_search = ? where id = ?",(row[1]+1,to_integer(datetime.datetime.now()),row[0],))
            else:
                cur.execute("insert into search_record (id,query_string,query_times,latest_search,search_type) values (NULL, ?,1,?,'paper') ",(query,to_integer(datetime.datetime.now()),))

            for id in paperIds:
                cur.execute("SELECT id, year, title FROM papers WHERE id = ?", (id,))
                row = cur.fetchone()
                cur.execute("SELECT topics.id, topics.name FROM paper_topic, topics WHERE paper_topic.paper_id = ? and paper_topic.topic_id = topics.id", (id,))
                row2 = cur.fetchone()
                paper = {'id': int(row[0]), 'year': int(row[1]), 'title': row[2],'topicid':row2[0],'topicname':row2[1]}

                cur.execute("SELECT authors.id, authors.name FROM paper_authors, authors WHERE paper_authors.paper_id = ? and paper_authors.author_id = authors.id", (id,))
                row3 = cur.fetchall()
                authors = []
                for row in row3:
                    cur.execute("SELECT institutions.id, institutions.name FROM author_institution,institutions where  author_institution.author_id = ? and author_institution.institution_id = institutions.id",(row[0],))
                    row4 = cur.fetchone()
                    t = {'id': row[0], 'name': row[1]}
                    if row4:
                        t['inst_id']=row4[0]
                        t['inst_name']=row4[1]
                    authors.extend([t])
                paper['authors'] = authors
                papers.extend([paper])

        return render_template('result-papers.html', papers = papers)


@application.route('/result-authors', methods = ['POST', 'GET'])
def resultAuthors():
    if request.method == 'POST':
        name = request.form['query']
        institution = request.form['institution']
        topic = request.form['topic']
        method = request.form['method']
        mix = request.form['mixMethod']
        authorIds = []
        authors = []

        if (method == "whoosh"):
            authorIds = searchAuthors_whoosh(name=name, institution=institution, topic=topic)
        elif (method == "lucene"):
            authorIds = searchAuthors_lucene(name=name, institution=institution, topic=topic, mix=mix)

        with conn:
            cur = conn.cursor()
            cur.execute("select id, query_times from search_record WHERE query_string = ? and search_type='author'",(name,))
            row = cur.fetchone()
            if row:
                cur.execute("update search_record set query_times = ?, latest_search = ? where id = ?",(row[1]+1,to_integer(datetime.datetime.now()),row[0],))
            else:
                cur.execute("insert into search_record (id,query_string,query_times,latest_search,search_type) values (NULL, ?,1,?,'author') ",(name,to_integer(datetime.datetime.now()),))
            
            for id in authorIds:
                cur.execute("SELECT a.id, a.name, i.name, i.id FROM authors a LEFT JOIN author_institution ai ON a.id=ai.author_id " + "LEFT JOIN institutions i ON i.id=ai.institution_id WHERE a.id = ?", (id,))
                row = cur.fetchone()		    
                author = {'id': int(row[0]), 'name': row[1], 'institution': row[2],'inst_id':row[3]}
                authors.extend([author])

        return render_template('result-authors.html', authors = authors)


@application.route('/paper/<int:id>')
def paper(id):
    paper = {}
    authors = []
    with conn:
        cur = conn.cursor()

        # Get paper details and all the authors and the topic
        cur.execute("SELECT p.title, p.year, p.paper_text, t.name, t.id FROM papers p JOIN paper_topic pt ON p.id=pt.paper_id " +
            " JOIN topics t ON t.id=pt.topic_id WHERE p.id = ?", (id,))
        row = cur.fetchone()
        paper = {'id': id, 'title': row[0], 'year': int(row[1]), 'paper_text': row[2].replace("\n","<br />\n"), 'topic_name': row[3], 'topic_id': row[4]}
        cur.execute("SELECT a.id, a.name, i.name, i.id FROM paper_authors pa JOIN authors a ON pa.author_id=a.id LEFT JOIN author_institution ai ON a.id=ai.author_id " + 
            "LEFT JOIN institutions i ON i.id=ai.institution_id WHERE pa.paper_id = ?", (id,))
        rows = cur.fetchall()            
        for row in rows:
            author = {'id': int(row[0]), 'name': row[1], 'institution_name': row[2], 'institution_id': row[3]}
            authors.extend([author])
        paper['authors'] = authors

    return render_template('paper-page.html', paper = paper)


@application.route('/author/<int:id>')
def author(id):
    author = {}
    papers = []
    related_topic = []
    related_collaboration = []
    related_text = []
    topics = []
    topicsid = set()

    with conn:
        cur = conn.cursor()
        cur.execute("SELECT COUNT(id) FROM authors")
        row = cur.fetchone()
        totAuthors = row[0]

        # Get author details and papers he wrote
        cur.execute("SELECT a.name, i.name, i.id, ar.pagerank_citations_order, ar.pagerank_collaborations_order, ar.google_hindex, ar.ms_hindex " +
            "FROM authors a LEFT JOIN author_institution ai ON a.id=ai.author_id LEFT JOIN institutions i ON i.id=ai.institution_id " +
		  "JOIN author_ranking ar ON a.id=ar.author_id WHERE a.id = ?", (id,))
        row = cur.fetchone()
        author = {'name': row[0], 'institution_name': row[1], 'institution_id': row[2], 'pagerank_citations': row[3], 'pagerank_collaborations': row[4], 'google_hindex': row[5], 'ms_hindex': row[6]}
        cur.execute("SELECT p.id, p.title, p.year FROM papers p JOIN paper_authors pa on p.id=pa.paper_id WHERE pa.author_id = ?", (id,))
        rows = cur.fetchall()            
        for row in rows:
            paper = {'id': row[0], 'title': row[1], 'year': int(row[2])}
            papers.extend([paper])
        author['papers'] = papers
        author['totAuthors'] = totAuthors

        # Get authors in the same topic cluster
        cur.execute("SELECT cluster_id FROM topic_cluster WHERE author_id = ?", (id,))
        clusterId=cur.fetchone()
        if(clusterId):
            cluster_topic = clusterId[0]
            cur.execute("SELECT a.id, a.name, ar.pagerank_collaborations FROM authors a JOIN topic_cluster tc ON a.id = tc.author_id " +
                "JOIN author_ranking ar on a.id=ar.author_id WHERE tc.cluster_id = ? AND a.id != ? ORDER BY ar.pagerank_collaborations DESC LIMIT 10", (cluster_topic,id))
            rows = cur.fetchall()
            for row in rows:
                rel_auth = {'id': row[0], 'name': row[1]}
                related_topic.extend([rel_auth])
        author['related_topic'] = related_topic

        # Get authors in the same collaboration cluster
        cur.execute("SELECT cluster_id FROM collaboration_cluster WHERE author_id = ?", (id,))
        clusterId=cur.fetchone()
        if(clusterId):
            cluster_collaboration = clusterId[0]
            cur.execute("SELECT a.id, a.name, ar.pagerank_collaborations FROM authors a JOIN collaboration_cluster cc ON a.id = cc.author_id " +
                "JOIN author_ranking ar on a.id=ar.author_id WHERE cc.cluster_id = ? AND a.id != ? ORDER BY ar.pagerank_collaborations DESC LIMIT 10", (cluster_collaboration,id))
            rows = cur.fetchall()
            for row in rows:
                rel_auth = {'id': row[0], 'name': row[1]}
                related_collaboration.extend([rel_auth])
        author['related_collaboration'] = related_collaboration

        # Get authors in the same text cluster
        cur.execute("SELECT cluster_id FROM text_cluster WHERE author_id = ?", (id,))
        clusterId=cur.fetchone()
        if(clusterId):
            cluster_collaboration = clusterId[0]
            cur.execute("SELECT a.id, a.name, ar.pagerank_collaborations FROM authors a JOIN text_cluster tc ON a.id = tc.author_id " +
                "JOIN author_ranking ar on a.id=ar.author_id WHERE tc.cluster_id = ? AND a.id != ? ORDER BY ar.pagerank_collaborations DESC LIMIT 10", (cluster_collaboration,id))
            rows = cur.fetchall()
            for row in rows:
                rel_auth = {'id': row[0], 'name': row[1]}
                related_text.extend([rel_auth])
        author['related_text'] = related_text

        # Get topic and years to plot graph
        cur.execute("SELECT pa.paper_id, pa.author_id, pt.topic_id, p.year  FROM papers p JOIN paper_authors pa ON p.id=pa.paper_id JOIN paper_topic pt on pt.paper_id=p.id WHERE pa.author_id = ?", (id,))
        rows = cur.fetchall()
        data = []
        for row in rows:
            data.append([row[0], row[1], row[2], row[3]])
            cur.execute("select name from topics where id=?",(row[2],))
            rowxxx = cur.fetchone()
            xxx = {'id':row[2],'name':rowxxx[0]}
            if row[2] not in topicsid:
                topicsid.add(row[2])
                topics.extend([xxx])
        author['topics'] = topics
        df = pd.DataFrame(np.array(data), columns = ["paper_id","author_id","topic","year"])
        plot_topic_author(df, id,)
        author['random_number'] = random.randint(1, 1000)

    return render_template('author-page.html', author = author)

@application.route('/institution/<int:id>')
def institution(id):
    institution = {}
    authors = []
    related = []
    i = 0
    ia = 0
    ip=0
    papers = []
    with conn:
        cur = conn.cursor()

        # Get institution details and all authors
        cur.execute("SELECT name FROM institutions WHERE id = ?", (id,))
        row = cur.fetchone()
        institution = {'id': id, 'name': row[0]}
        cur.execute("SELECT a.id, a.name FROM authors a JOIN author_institution ai ON a.id=ai.author_id WHERE ai.institution_id = ?", (id,))
        rows = cur.fetchall()
        for row in rows:
            author = {'id': row[0], 'name': row[1],'pos':int(ia)}
            ia = ia + 1
            cur.execute("select papers.id, papers.title, papers.year, topics.id, topics.name from paper_authors, papers, paper_topic, topics where paper_authors.author_id = ? and paper_authors.paper_id = papers.id and paper_topic.paper_id = papers.id and topics.id=paper_topic.topic_id",(row[0],))
            rowx = cur.fetchall()
            for row1 in rowx:
                t={'id':row1[0],'title':row1[1],'year':row1[2],'topicid':row1[3], 'topicname':row1[4],'pos':int(ip)}
                ip = ip + 1
                papers.extend([t])
            author['papers']=papers
            authors.extend([author])
        institution['authors'] = authors

        # Get institutions in the same topic cluster
        cur.execute("SELECT cluster_id FROM institution_cluster WHERE institution_id = ?", (id,))
        clusterId=cur.fetchone()
        if(clusterId):
            cluster = clusterId[0]
            cur.execute("SELECT i.id, i.name FROM institutions i JOIN institution_cluster ic ON i.id = ic.institution_id WHERE ic.cluster_id = ? AND i.id != ?", (cluster,id))
            rows = cur.fetchall()
            for row in rows:
                rel_inst = {'id': row[0], 'name': row[1], 'pos':int(i)}
                i=i+1
                related.extend([rel_inst])
        institution['related'] = related

        # Get the most frequent topic
        cur.execute("SELECT t.id, t.name, count(*) FROM topics t JOIN paper_topic pt on t.id=pt.topic_id JOIN paper_authors pa on pt.paper_id=pa.paper_id " + 
            "JOIN author_institution ai ON pa.author_id=ai.author_id WHERE ai.institution_id = ? GROUP BY t.id, t.name ORDER BY count(*) DESC LIMIT 1", (id,))
        row = cur.fetchone()
        topic = {'id': row[0], 'name': row[1]}
        institution['topic'] = topic

    return render_template('institution-page.html', institution = institution)


@application.route('/topic/<int:id>')
def topic(id):
    topic = {}
    otherTopics = []
    papers = []
    i = 0
    with conn:
        cur = conn.cursor()

        # Get topic details and all papers with that topic
        cur.execute("SELECT name FROM topics WHERE id = ?", (id,))
        row = cur.fetchone()
        topic = {'id': id, 'name': row[0]}
        cur.execute("SELECT p.id, p.title, p.year FROM papers p JOIN paper_topic pt on p.id=pt.paper_id WHERE pt.topic_id = ?", (id,))
        rows = cur.fetchall()            
        for row in rows:
            paper = {'id': row[0], 'title': row[1], 'year': int(row[2]), 'pos':int(i)}
            i=i+1
            cur.execute("SELECT authors.id, authors.name FROM paper_authors, authors WHERE paper_authors.paper_id = ? and paper_authors.author_id = authors.id", (row[0],))
            row3 = cur.fetchall()
            authors = []
            for row in row3:
                t = {'id': row[0], 'name': row[1]}
                authors.extend([t])
            paper['authors'] = authors
            papers.extend([paper])
        topic['papers'] = papers

        cur.execute("SELECT id, name FROM topics WHERE id != ?", (id,))
        rows = cur.fetchall()
        for row in rows:
            t = {'id': row[0], 'name': row[1]}
            otherTopics.extend([t])
        topic['other'] = otherTopics
    return render_template('topic-page.html', topic = topic)


@application.route("/info")
def info():
	return render_template('info.html')


@application.route("/topic-analysis")
def topicAnalysis():
    return render_template('topic-analysis.html')



if __name__ == "__main__":
  application.run()

