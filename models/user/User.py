from   flask import Flask, session
from   common.database import Database
from   models.admin import *
from   models import constants as UserConstants
from   models.System_file import File_system
from   array  import *
from   common.Utils import utils
from   models.user.error import  UserError
from   email.mime.text import   MIMEText
import smtplib

import os
import datetime
import uuid

class Users(object):
	parentAttr = 100
	
	def __init__(self,firstname, lastname, email,password,image, age,date=datetime.datetime.utcnow(), _id=None):
		self.firstname =  firstname
		self.lastname  =  lastname
		self.email = email
		self.password = password
		self.image = image
		self.age   = age
		self.date =  date
		self._id = uuid.uuid4().hex if _id is None else _id

	def parentMethod(self):
		print 'Calling parent  method'
	
	def setAttr(self,  attr):
		Users.parentAttr = attr
	
	def getAttr(self):
		print 'Parent  attribute :',  Users.parentAttr
	
	@staticmethod
	def __sendemail():
		to_addr_list = "ithollieyahoo.com"
		from_addr = "boysthollie@gmail.com"
		smtpserver = "smtp.gmail.com"
		message =    'thank you'
		server = smtplib.SMTP(smtpserver, 12397)
		server.starttls()
		server.login('boysthollie@gmail.com','69414422173943112')
		try :
		    server.sendmail(from_addr, to_addr_list, message)
		    server.quit()
		except smtplib.SMTPException:
	    	 print("not good")
	    	
	@staticmethod 
	def sendMail(sender, receiver):
		host = os.getenv('IP','127.0.0.1')
		port = int(os.getenv('PORT',6000))
		sender  = "boysthollie@gmail.com"
		
		message = """From: From Person <from@fromdomain.com>
						To: To Person <to@todomain.com>
						Subject: SMTP e-mail test 
						This is a test e-mail message."""
		try :
			smtObject  =  smtplib.SMTP(sender, host)
			smtObject.sendmail(sender, receiver, message)
		except smtplib.SMTPException:
			print("email not send  please contact an  adminstrator")
			
	@classmethod
	def get_by_id(cls,_id):
		data = Database.find_one(UserConstants.COLLECTION,{"_id":_id})
		if data is not None:
			return cls(**data)
		else:
			raise UserErrors.UserNotExistError("user does not exit")


	@classmethod
	def get_by_email(cls,email):
			data = Database.find_one(UserConstants.COLLECTION, {"email":email})
			if data is not None:
				#return cls(**data)
				return True
			else:
				return False
	@classmethod
	def search(cls,email):
			arra = []
			data = Database.find_one(UserConstants.COLLECTION, {"email":email})
			position  = 4
			correct  = ""
			if data['email'][:5] is not None:
				return True
			else:
				return False
	@staticmethod
	def Database_password(password):
		data =  Database.find_one(UserConstants.COLLECTION,{"password":password})
		return data
	
	@staticmethod
	def  login_email_name(email, password):
		 data =  Database.find_one(UserConstants.COLLECTION,{"email":email})
		 if data is not  None:
		 	return   data
	@staticmethod
	def login_valid(email,password):
			data =  Database.find_one(UserConstants.COLLECTION,{"email":email})
			user =  Users.get_by_email(email)
			if  user and utils.check_hash_password(password,data['password']) is not None:
				return True
			else:
				return  False
				#raise UserErrors.InvalideEmailError("invalid user")

	@classmethod
	def registration(cls, firstname, lastname , email,password, age,image):
		Link  =  LinkedLists(firstname, lastname, email, password, age,  image)
		
		if Link.insert() == firstname:
			if cls.get_by_email(email) == False and utils.email_is_valid(email):
				new_user = cls(firstname,lastname,email,utils.hash_password(password),image,  age)
				new_user.save_to_mongo()
				session['email'] = email
				return True
			else:
				return "there is a user with that email"
		else:
			return  False
		
	@classmethod
	def passhashed(cls,password):
		if  password is not None:
			return  utils.hash_password(password)
			
	@staticmethod
	def findByEmail(email):
		Database.find_one(UserConstants.COLLECTION,{"email":email})
		
	@staticmethod
	def login(email):
		session['email'] = email

	@classmethod
	def resetPassword(cls ,email,  hash_password):
		Database.updates(UserConstants.COLLECTION,{"email":email}, { "$set": { "password":hash_password }})
	
	@classmethod
	def resetEmail(cls , new_email, oldmail):
		Database.updates(UserConstants.COLLECTION, {"email":oldmail}, {"$set":{"email":new_email}})
		
	def save_to_mongo(self):
		Database.insert(UserConstants.COLLECTION,self.json())
		
	@classmethod
	def update_image(cls, email, image):
		Database.updates(UserConstants.COLLECTION,{"email":email },{"$set": {"image":image}})
 
	@classmethod
	def  save_image(cls ,email , image):
		if cls.get_by_email(email) == True:
			user = cls.get_by_email(email)
			utils.email_is_valid(email)
			cls.update_image(email, image)
		
	def json(self):
			return {
				"firstname":self.firstname,
				"lastname":self.lastname,
				"email":self.email,
				"password":self.password,
				"_id":self._id,
				"image":self.image, 
				"age":self.age,
				"data":self.date
			}
