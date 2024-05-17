from django.shortcuts import render
from .models import *
import json
from django.core import serializers
from django.http import HttpResponse, JsonResponse
from django.db.models import Q
from django.db.models import Count
import re
import os
from datetime import datetime
from datetime import date
from django.views.decorators.cache import never_cache
from django.core.files.storage import FileSystemStorage
import qrcode
from django.views.decorators.csrf import csrf_exempt

from base64 import b64encode
from base64 import b64decode
from Crypto.Cipher import ChaCha20
from Crypto.Random import get_random_bytes
from chacha20poly1305 import ChaCha20Poly1305


# Create your views here.

@never_cache
def show_index(request):
    return render(request, "login.html", {})

@never_cache
def show_register(request):
    return render(request, "register.html", {})

@never_cache
def logout(request):
    if 'uid' in request.session:
        del request.session['uid']
    return render(request,'login.html')


def register(request):
	username = request.POST.get("username")
	password = request.POST.get("password")
	phone = request.POST.get("phone")
	email = request.POST.get("email")

	obj1=Users.objects.filter(username=username)
	c=obj1.count()
	if c==1:
		return HttpResponse("<script>alert('Username Already Taken');window.location.href='/show_register/'</script>")

	else:
		obj2=Users(username=username,password=password,phone=phone,email=email)
		obj2.save()

		return HttpResponse("<script>alert('Registered Successfully');window.location.href='/show_index/'</script>")


def check_login(request):
	username = request.POST.get("username")
	password = request.POST.get("password")

	print(username)
	print(password)

	d = Users.objects.filter(username=username, password=password)
	c = d.count()
	if c == 1:
		d2 = Users.objects.get(username=username, password=password)
		request.session["uid"] = d2.u_id
		request.session["username"] = d2.username

		return HttpResponse("<script>alert('Login Successful');window.location.href='/show_home_user/'</script>")
	else:
		return HttpResponse("<script>alert('Invalid');window.location.href='/show_index/'</script>")


		

@never_cache
###############ADMIN START
def show_home_user(request):
	if 'uid' in request.session:
		print(request.session['uid'])
		return render(request,'home_user.html') 
	else:
		return render(request,'login.html')

@never_cache
def display_upload_file(request):
	if 'uid' in request.session:

		return render(request,'display_upload_file.html',{}) 
	else:
		return render(request,'login.html')


def perform_encryption(content):

	#generate key
	key = os.urandom(32)
	cip = ChaCha20Poly1305(key)

	#generate nonce
	nonce = os.urandom(12)

	print("*****************")
	ciphertext = cip.encrypt(nonce, content)
	print(ciphertext)
	print(type(ciphertext))
	result ={'key':key,'nonce':nonce, 'ciphertext':ciphertext}
	print(result)


	return key,nonce,ciphertext

def perform_decryption(key,nonce,content,filename,username):
	print("************")
	print(key)
	print(nonce)
	print(content)
	print("************")

	cip = ChaCha20Poly1305(key)

	plaintext = cip.decrypt(nonce, content)
	print(plaintext)

	plaintext=plaintext.decode()

	if not os.path.isdir("DDE_app/static/decrypted/"+username):
		os.makedirs("DDE_app/static/decrypted/"+username)

	f3=open("DDE_app/static/decrypted/"+username+"/"+filename,'w')
	f3.write(plaintext)
	f3.close()


def upload_file(request):
	username=request.session["username"]
	
	f2= request.FILES["file"]
	file_name=str(f2.name)


	print("f2: ",f2)
	print("file_name: ",file_name)

	if Files.objects.filter(filename=file_name).exists():
		return HttpResponse("<script>alert('File with this name already exists');window.location.href='/display_upload_file/'</script>")

	else:

		fs1 = FileSystemStorage("DDE_app/static/files/"+username)#%username
		fs1.save(file_name, f2)

		f1=open("DDE_app/static/files/"+username+"/"+file_name,'rb')
		content=f1.read()
		f1.close()
		print("Content : ",content)

		key,nonce,ct=perform_encryption(content)


		now = datetime.now()
		time = now.strftime("%H:%M:%S")
		print("Current Time =", time)

		today = date.today()
		current_date = today.strftime("%d/%m/%Y")
		print("date =",current_date)

		

		if not os.path.isdir("DDE_app/static/encrypted/"+username):
			os.makedirs("DDE_app/static/encrypted/"+username)
		
		f3=open("DDE_app/static/encrypted/"+username+"/"+file_name,'wb')
		f3.write(ct)
		f3.close()

		if not os.path.isdir("DDE_app/static/chunks/"+username+"/"+file_name):
			os.makedirs("DDE_app/static/chunks/"+username+"/"+file_name)

		f4=open("DDE_app/static/encrypted/"+username+"/"+file_name,'rb')
		chunk = 0
 
		byte = f4.read(20)#1024
		while byte:
		 
		    # Open a temporary file and write a chunk of bytes
		    fileN = "DDE_app/static/chunks/"+username+"/"+file_name+"/"+file_name+"_chunk" + str(chunk) + ".txt"
		    fileT = open(fileN, "wb")
		    fileT.write(byte)
		    fileT.close()
		     
		    # Read next 1024 bytes
		    byte = f4.read(20)#1024
		 
		    chunk += 1
		    # print("chunk : ",chunk)
		print("final chunk :: ",chunk)


		obj1=Files(filename=file_name,username=username,date=current_date,time=time,chunks=chunk)
		obj1.save()

		obj2=Files.objects.get(filename=file_name,username=username,date=current_date,time=time,chunks=chunk)
		f_id=obj2.f_id

		obj3=Keys(f_id=f_id,key=key,nonce=nonce)
		obj3.save()


		return HttpResponse("<script>alert('File Uploaded Successfully');window.location.href='/display_upload_file/'</script>")


@never_cache
def view_my_files(request):
	username=request.session["username"]
	if 'uid' in request.session:
		req_list=Files.objects.filter(username=username)

		return render(request,'view_files_user.html',{'req': req_list}) 
	else:
		return render(request,'login.html')


def file_delete(request):
	f_id=request.POST.get('f_id')
	obj1=Files.objects.get(f_id=int(f_id))
	obj1.delete()

	obj2=Keys.objects.get(f_id=int(f_id))
	obj2.delete()
	return HttpResponse("<script>alert('File Deleted Successfully');window.location.href='/view_my_files/'</script>")


def merge_chunks(username,filename,chunks):
	print("Chunks :",chunks)
	chunks=int(chunks)

	if not os.path.isdir("DDE_app/static/chunks_merge/"+username):
		os.makedirs("DDE_app/static/chunks_merge/"+username)

	# Open original file for reconstruction
	fileM = open("DDE_app/static/chunks_merge/"+username+"/"+filename, "wb")
	 
	# Manually enter total amount of "chunks"
	chunk = 0
	 
	# Piece the file together using all chunks
	while chunk < chunks:
	    print(" - Chunk #" + str(chunk) + " done.")
	    fileName = "DDE_app/static/chunks/"+username+"/"+filename+"/"+filename+"_chunk" + str(chunk) + ".txt" #"chunk" + str(chunk) + ".txt"
	    fileTemp = open(fileName, "rb")
	 
	    byte = fileTemp.read(20)
	    fileM.write(byte)
	 
	    chunk += 1
	 
	fileM.close()


def download(request):
	f_id=request.POST.get("f_id")
	filename=request.POST.get("filename")
	username=request.session["username"]
	chunks=request.POST.get("chunks")

	obj1=Keys.objects.get(f_id=int(f_id))
	get_key=obj1.key
	get_nonce=obj1.nonce

	merge_chunks(username,filename,chunks)

	f1=open("DDE_app/static/chunks_merge/"+username+"/"+filename,'rb')
	content=f1.read()
	f1.close()
	print("Content : ",content)

	perform_decryption(get_key,get_nonce,content,filename,username)

	if True:
        
		file1_path = "DDE_app/static/decrypted/"+username+"/"+filename
		print(os.path.exists(file1_path))
		print(file1_path)

		if os.path.exists(file1_path):
			with open(file1_path, 'rb') as fh:
				response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
				response['Content-Disposition'] = 'inline; filename=' + os.path.basename(file1_path)
				return response
		raise HttpResponse("<script>alert('File does not exists');window.location.href='/view_my_files/'</script>")
	return HttpResponse("<script>alert('File Downloaded Successfully');window.location.href='/view_my_files/'</script>")