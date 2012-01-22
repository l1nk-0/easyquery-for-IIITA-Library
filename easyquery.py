import sys,os,re,thread,urllib2,urllib

def _exit(obj=None) :
	if not obj == None :
		if obj.tofile :
			obj.output.close()
	os._exit(0)

def fetch_book_list(obj,order_by) :
	__='s'+'q'+'l'
	while obj.bookcount > 0 :
		try :
			req=urllib.urlencode({"Option":"PageView",__:obj.query(obj.search,obj.condition)+"+ORDER+BY+"+order_by+"+asc","pageSize":str(obj.pagesize),"absolutePage":str(obj.absolutepage)})
			fd = obj.opener.open("http://library.iiita.ac.in"+obj.subdir+"?"+req)
			data=obj.htmlparser(fd.read(),"table")
			fd.close()
		except urllib2.HTTPError,e :
			if e.getcode()==407 :
				sys.stdout.write("proxy authentication error: try specifying --proxy argument\n")
				sys.stdout.write("If password authentication is required try specifying --user argument\n")
				_exit(obj)
			elif e.getcode()==408:
				sys.stdout.write("connection timed out: seems like you are on a slow internet connection :(\n")
				sys.stdout.write("Try specifying --pagesize argument with low value\n")
				_exit(obj)
			else :
				sys.stdout.write("grr .. error retrieving the list of books. retry\n")
				_exit(obj)
		except urllib2.URLError,e :
			if e :
				if e.errno == -2 :
					sys.stdout.write("unable to connect.name or service not known\n")
					sys.stdout.write("try specifying --proxy argument with proxy eg :- --proxy 172.31.1.4\n")
					_exit(obj)
				else :
					sys.stdout.write("grr .. error retrieving the list of books. retry\n")
					_exit(obj)
			else :
				sys.stdout.write("grr .. error retrieving the list of books. retry\n")
				sys.stdout.write("try specifying --proxy argument with proxy eg :- --proxy 172.31.1.4\n")
				_exit(obj)
		except :
			sys.stdout.write("grr .. error retrieving the list of books. retry\n")
			_exit(obj)
		

		while obj.mutex == 1:
			pass
		if len(data)==2 :
			books=obj.htmlparser(data[1],"tr")
			if len(books) > 0 :
				th = obj.htmlparser(books[0],"th")
				entry=[]
				for each in th :
					entry.append(each[4:len(each)-5])
				obj.booklist.append(entry)
				for i in range(1,len(books)) :
					td = obj.htmlparser(books[i],"td")
					entry=[]
					for each in td :
						info=each[4:len(each)-5]
						if info.endswith("</a>") :
							info=info[info.find(">")+1:len(info)-4]
						entry.append(info)
					obj.booklist.append(entry)
		obj.bookcount=obj.bookcount-obj.pagesize
		obj.absolutepage=obj.absolutepage+1
		obj.mutex=1
	while obj.mutex == 1:
		pass
	obj.done=True
	_exit(obj)

class easyquery :
	def __init__(self) :
		self.search=''
		self.condition=''
		self.absolutepage=1
		self._11_="+BookDetails+"
		self.pagesize=20
		self.bookcount=0
		self.mutex=0
		self.done = False
		self.booklist=[]
		self.tofile=False
		self.subdir="/cgi-bin/OPAC.exe"
		self.output=sys.stdout
		self.opener=urllib2.build_opener()

	def htmlparser(self,data,tagname) :
		try :
			regex = re.compile("<"+tagname+".*?</"+tagname+">",re.DOTALL)
		except :
			sys.stdout.write("error: unable to parse "+tagname+"\n")
			os._exit(0)
		return regex.findall(data)

	def getcondition(self,fields,avail=None) :
		field={}
		incl={}
		excl={}
		j=0
		incl_entry=True
		for i in range(len(fields)) :
			if fields[i]=='&' or i==len(fields)-1 or fields[i]=='|':
				if i==len(fields)-1 :
					data=fields[j:i+1].split("=")
				else :
					data=fields[j:i].split("=")
				if len(data)==2:
					content=data[1].replace("*","{")
					if incl_entry :	
						incl[data[0]]=content.replace(" ","+")
					else:
						excl[data[0]]=content.replace(" ","+")
				j=i+1
				if fields[i]=='&' :
					incl_entry=True
				else :
					incl_entry=False

		field["incl"]=incl
		field["excl"]=excl	

		if avail :
			field["avail"]=avail

		return field

	def getfields(self,fields='') :
		if len(fields)==0 :
			return set(["title","status","shelfno","reserved","lastissue"])
		else :
			field_list=fields.split('&')
			if len(field_list[0])==0:
				field_list.remove(field_list[0])
				field_list.extend(["title","status","shelfno","reserved","lastissue"])

		return set(field_list)

	def query(self,search,condition) :
		sString=''
		cString=''
		__='SELECT+'
		for each in search :
			sString=sString+each+','
	
		try :
			incl=condition["incl"]
			excl=condition["excl"]
		except :
			sys.stdout.write("--field argument is not specified properly\n")
			os._exit(0)

		for key in incl.keys() :
			if (('{' in incl[key]) or ('_' in incl[key])) :
				cString=cString+str(key)+"+LIKE+|"+str(incl[key])+"|+AND+"
			else :
				cString=cString+str(key)+"=|"+str(incl[key])+"|+AND+"

		try :
			cString=cString[0:len(cString)-5]
		except :
			pass

		if len(excl) > 0 :
			cString=cString+"+OR+"

		for key in excl.keys() :
			if key=="title" or key=="author" :
				cString=cString+str(key)+"+LIKE+|"+str(excl[key])+"|+OR+"
			else :
				cString=cString+str(key)+"="+str(excl[key])+"+OR+"

		try :
			sString=sString[0:len(sString)-1]
		except :
			pass

		if len(excl) > 0:
			cString=cString[0:len(cString)-4]

		return __+sString+self.___+cString

	def redirect_to_output(self,books) :
		tag = books[0]
		for i in range(1,len(books)) :
			data=books[i]
			if len(data) > 0 :
				self.output.write("serial no. :"+data[0]+"\n")
				for j in range(1,len(data)) :
					try :
						self.output.write("\t"+tag[j]+" : "+data[j]+"\n")
					except :
						pass

	def print_book_list(self,order_by="title") :
		try :
			thread.start_new_thread(fetch_book_list,(self,order_by))
		except :
			sys.stdout.write("error: thread for fetching book list terminated\n")
			_exit(self)

		while not self.done:
			while self.mutex == 0:
				pass			
			books=self.booklist
			self.booklist=[]
			if len(books) > 0 :
				self.redirect_to_output(books)
			self.mutex=0
			if not self.tofile :
				c=str(raw_input())
				if not c=='' :
					_exit(self)

	def calc_total_entry(self,args) :
		proxy={}
		http="http://"
		__='s'+'q'+'l'
		if "proxy" in args.keys() :
			if "user" in args.keys() :
				http=http+args["user"]+":"+args["pass"]+"@"
			http=http+args["proxy"]+":8080"
			proxy["http"]=http
			handler = urllib2.ProxyHandler(proxy)
			self.opener = urllib2.build_opener(handler)
	
		try :
			req = urllib.urlencode({"Option":"PageView",__:self.query(["count(*)"],self.condition)})

			fd = self.opener.open("http://library.iiita.ac.in"+self.subdir+"?"+req)
			data=self.htmlparser(fd.read(),"table")
			fd.close()
		except urllib2.HTTPError,e :
			if e.getcode()==407 :
				sys.stdout.write("proxy authentication error: try specifying --proxy argument\n")
				sys.stdout.write("If password authentication is required try specifying --user argument\n")
				os._exit(0)
			elif e.getcode()==408:
				sys.stdout.write("connection timed out: seems like you are on a slow internet connection :(\n")
				sys.stdout.write("Try specifying --pagesize argument with low value\n")
				os._exit(0)
			else :
				sys.stdout.write("grr .. error retrieving the list of books. retry\n")
				os._exit(0)
		except urllib2.URLError,e :
			if e :
				if e.errno == -2 :
					sys.stdout.write("unable to connect.name or service not known\n")
					sys.stdout.write("try specifying --proxy argument with proxy eg :- --proxy 172.31.1.4\n")
					os._exit(0)
				else :
					sys.stdout.write("grr .. error retrieving the list of books. retry\n")
					os._exit(0)
			else :
				sys.stdout.write("grr .. error retrieving the list of books. retry\n")
				sys.stdout.write("try specifying --proxy argument with proxy eg :- --proxy 172.31.1.4\n")
				os._exit(0)
		except :
			sys.stdout.write("grr .. error retrieving the list of books. retry\n")
			os._exit(0)
				
		if len(data)==2 :
			count=self.htmlparser(data[1],"td")
			self.bookcount=int(str(count[1])[4:len(count[1])-5])
			sys.stdout.write(str(self.bookcount)+" entries matches the request\n");
		else :
			sys.stdout.write("No entry found for\n")
			for key in self.condition.keys() :
				sys.stdout.write("\t"+str(key)+" : "+str(self.condition[key])+"\n")
			os._exit(0)
	

	def make_easy_query(self,args) :
		self.___="+FROM"+self._11_+"Where+"
		if "avail" in args.keys() :
			self.condition=self.getcondition(args["field"],args["avail"])
		else :
			self.condition=self.getcondition(args["field"])

		if "display" in args.keys() :
		        self.search=self.getfields(args["display"])
		else :
		        self.search=self.getfields()
	
		if "pagesize" in args.keys() :
			self.pagesize=args["pagesize"]

		self.calc_total_entry(args)

		if "saveto" in args.keys() :
			try :
				self.output=open(args["saveto"],"w")
				self.tofile=True
				sys.stdout.write("redirecting output to : ... "+args["saveto"]+"\n")
			except :
				sys.stdout.write("unable to open file to save into, redirecting to console\n")
				self.tofile=False

		if "avail" in args.keys() :			
			self.print_book_list("Status")
		else :
			self.print_book_list()
