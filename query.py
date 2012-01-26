import os,sys,getpass,platform
from easyquery import easyquery

def showMenu() :
	try :
		fd = open("manfile.txt","r")
	except :
		sys.stdout.write("error: unable to open manfile, maybe the manfile is missing\n")
		return
	try :
		for line in fd.readlines() :
			try :
				if platform.system() == "Windows" :
					line = line.replace("'",'"')
			except :
				pass
			sys.stdout.write(line)
		fd.close()
	except :
		pass

def extract(arg,field) :
	if not field[0:2] == "--" :
		return field
	else :
		sys.stdout.write(str(arg)+"value is not provided\n")
		os._exit(0)
			
def getargument(query) :
	args={}
	try :
		for i in range(len(query)) :
			if query[i][0:2]=="--" :
				if query[i][2:].lower()=="field" :
					args["field"]=extract("field",query[i+1])
				elif query[i][2:].lower()=="pagesize" :
					args["pagesize"]=int(extract("pagesize",query[i+1]))
				elif query[i][2:].lower()=="display" :
					args["display"]=extract("display",query[i+1])
				elif query[i][2:].lower()=="help" :
					showMenu()
					os._exit(0)
				elif query[i][2:].lower()=="avail" :
					args["avail"]=1
				elif query[i][2:].lower()=="proxy" :
					args["proxy"]=extract("proxy",query[i+1])
				elif query[i][2:].lower()=="user" :
					args["user"]=extract("user",query[i+1])
					sys.stdout.write("Give password for proxy authentication : ")
					args["pass"]=getpass.getpass()
				elif query[i][2:].lower()=="saveto" :
					args["saveto"]=extract("saveto",query[i+1])
				else :
					sys.stdout.write("unknown argument"+str(query[i])+"\n")
					os._exit(0)
	except Exception,e:
		sys.stdout.write("Invalid argument"+str(query)+str(e)+"\n")
		os._exit(0)
	return args



if __name__ == "__main__" :
	inst = easyquery()
	args=getargument(sys.argv[1:])
	if "field" not in args.keys() :
		sys.stdout.write("Data to be searched not given.Give --field argument\n")
		os._exit(0)
	else :
		inst.make_easy_query(args)
