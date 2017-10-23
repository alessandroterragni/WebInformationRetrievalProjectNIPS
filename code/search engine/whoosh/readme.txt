Configure the web service project with Tomcat, then you can run it on server.


1)API to generate or update the index : http://localhost:8080/nips-RESTService/api/update/para


Return [true, true], representing if the index of papers and authors are successfull updated


2)API to search papers: 

sample queries:
VSR:
http://localhost:8080/nips-RESTService/api/getpaper/para?author=Jordan&bYear=1987&eYear=2016&topic=1&mix=or&searchType=VSR&sentence=machine learning

fuzzy:
http://localhost:8080/nips-RESTService/api/getpaper/para?author=Jordan&bYear=1987&eYear=2016&topic=1&mix=or&searchType=fuzzy&sentence=machine learning

boolean(or and must)
http://localhost:8080/nips-RESTService/api/getpaper/para?author=Jordan&bYear=1987&eYear=2016&topic=1&mix=or&searchType=boolean&or=machine&must=learning

boolean(no)
http://localhost:8080/nips-RESTService/api/getpaper/para?author=Jordan&bYear=1987&eYear=2016&topic=1&mix=or&searchType=boolean&no=machine&no=learning

3)API to search authors:

sample queries:
http://localhost:8080/nips-RESTService/api/getauthor/para?name=Jordan&inst=Berkeley&topic=1&mix=or