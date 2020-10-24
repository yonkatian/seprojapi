# THIS WHERE THE API CALLED HAPPEN

#Import Django Library Some are kept just in case I need to use it 
from django.shortcuts import render ,redirect
from django.http import HttpResponse,JsonResponse

# for not equals 
from django.db.models import Q 

from django.contrib.auth.models import User 
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings  #Import your setting from Django


#Import the rest-frame work Library
from  rest_framework.response import Response
from  rest_framework.decorators import api_view  
from rest_framework.views import APIView



from .Verifyaccount import send_vertification_email
from .serializer import CreateUserSerailizer
from .serializer import LoginUserSeralizer
from .serializer import getUsernameSeralizer


from .serializer import PostItemSeralizer
from .serializer import DeleteItemSeralizer
from .serializer import SearchdetailSeralizer
from .serializer import searchItemSeralizer
from .serializer import ViewUserItemSeralizer
from .serializer import MakeOrderSeralizer
from .models import Post ,Order ,Profile
from .Verifyaccount import send_vertification_email;

#Administrator password is Unwanted1
#user2 password is         Unwanted2
#user3 password is         Unwanted3

#If not mention 0 mean API failed 1 mean API Pass 

# To get the username base on the userid 
#Since my list_view return the UID 
#JSON Syntax 
# {
# 
#  "Userid":2
# }
@api_view(['POST'] )
def get_username(request,*args, **kwargs):
    get_username_seralizer = getUsernameSeralizer()
    uid = get_username_seralizer.get_id(request.data)
    userobj = User.objects.get(pk=uid)
    
    data={
        "Result": userobj.username
    }

    return Response(data,status=200)




#Login APi the URL is at url.py 
#Check the login get data via the URL
#0= login fail  1=Pass
#JSON Syntax 
# {
#    "username":"user2",
#    "password":"Unwanted2"
# }
@api_view(['POST'] )
def login(request,*args,   **kwargs):
    
    Login_user_seralizer = LoginUserSeralizer()

    usercode =Login_user_seralizer.get_username(request.data)
    passcode = Login_user_seralizer.get_password(request.data)

    resultvalue = Login_user_seralizer.checkauthentication(usercode,passcode)
    data={
            "Result": resultvalue
     }
    return Response(data, status=200) 






# API to create user 

#Format to follow : CASE SENSETIVE
# {
# 	"username": "user2",
# 	"password": "123",
# 	"email": "2@2.com",
#   "Hall": " "
# }

#1= Sucess  0= Failure in REST/Serializer  -1= Email Failure
# HELPER METHOD usually it put on seperate File but Since only have 2 method I just leave it here 
def check_userExist( userCode):
    try:
        User.objects.get(username=userCode)
        #result found should not create the user 
        return 1
    except ObjectDoesNotExist:

        return 0

def check_emailExist(emailCode):
    try:
        User.objects.get(email=emailCode)
        #result found should not create the user 
        return 1
    except ObjectDoesNotExist:

         return 0

# Call this the above 2 are just helper method
#get data via JSON 
@api_view(['POST'] )
def create_User(request,*args,**kwargs):
    create_user_seralizer = CreateUserSerailizer(data=request.data)
    #Now come the hard part of sending the request.data into here

    usercode = create_user_seralizer.getUsername(request.data)
    emailcode = create_user_seralizer.getEmail(request.data)

    if check_emailExist(emailcode) == 1 :
        data={
            "Result": "Email already exist"
        }
        return Response(data,status=500)


    if  check_userExist(usercode) == 1: 
        data={
            "Result": "Username  already exist"
            
        }
        return Response(data,status=500)
    else :
        #IGNORE THE RED LINE if any 
        if create_user_seralizer.is_valid(raise_exception=True):
        #create_user_seralizer.save(is_active='False')
            create_user_seralizer.createUser(request.data)
            data= {
            "Result": 1
            }
            send_vertification_email(emailcode) 
            try:
                send_vertification_email(emailcode) 
                return Response(data, status=200) 
            except:
                #if email FAILED For some funny reason 
                return Response({"Result": -1}, status=500) 

        return Response({"Result": 0}, status=500) 
           
     







#-----------------------------------------  CRUD Product Table-------------------------------------------------

@api_view(['GET'])
def list_view(request,*args ,**kwargs):
    #Do not get the Administrator Post Item  


    #Another way
    qs = Post.objects.all().order_by('Userid')
    seralizer = searchItemSeralizer(qs,many=True)
    

    return Response(seralizer.data ,status=200)


#List the post belong to the User
#JSON Format for list_userview
# {
#     "username": "user2"
# }
@api_view(['POST'])
def list_user_view(request ,*args ,**kwargs):


    list_user_seralizer = ViewUserItemSeralizer(data=request.data)
    qs=None 
    try:
        userarg = list_user_seralizer.getusername(request.data)
        userobj = User.objects.get(username=userarg)
        qs = Post.objects.filter(Userid=userobj.pk).order_by("PostDate")
    except:
        return Response({"Result": "Username not found"}, status=500) 
    #qs = User.objects.filter(pk=userobj.pk)
   
    #set Many to true to return many value
    seralizer = searchItemSeralizer(qs, many=True)
    return Response(seralizer.data ,status=200)


#JSON format
# {
# "searchType": "ItemName/Category/Hall",
# "searchArg" : "XXXXXX",
#"searchOrd": "ASC,DESC"
# }
#ASC=  Oldest First #DESC is latest 
#Another way to define .. this is call class based vieW
class search_post_Item(APIView ):
    #if the API is a POST request
    def post(self,request,format=None):
        search_post_item_seralizer = SearchdetailSeralizer()

        searchType = search_post_item_seralizer.getSearchType(request.data)
        searchArg = search_post_item_seralizer.getSearchArg(request.data)
        searchOrder = search_post_item_seralizer.getSearchOrder(request.data)

        qs= None

        if searchOrder == "ASC":
             if searchType=="ItemName":
                    qs=Post.objects.filter(ItemName__icontains=searchArg).order_by("PostDate")
                    seralizer =searchItemSeralizer(qs,many=True)
                    return Response(seralizer.data ,status=200)
             elif  searchType =="Category":
                    qs =Post.objects.filter(Category__iexact=searchArg).order_by("PostDate")
                    seralizer =searchItemSeralizer(qs,many=True)
                    return Response(seralizer.data ,status=200)
             elif searchType =="Hall":
                    #Hallobj = Profile.objects.get(Hall=searchArg)
                    # keep thing simiple RAW SQL
                    qs= Post.objects.raw("SELECT * FROM Post as p INNER JOIN auth_user as u on p.Userid_id=u.id INNER JOIN Profile as pro on P.Userid_id= pro.Userid_id WHERE Hall=%s ORDER BY PostDate",[searchArg])
                    seralizer=searchItemSeralizer(qs,many=True)
                    return Response(seralizer.data ,status=200)
                 
        elif searchOrder == "DESC" :
             if searchType=="ItemName":
                    qs=Post.objects.filter(ItemName__icontains=searchArg).order_by("-PostDate")
                    seralizer =searchItemSeralizer(qs,many=True)
                    return Response(seralizer.data ,status=200)
             elif  searchType =="Category":
                    qs =Post.objects.filter(Category__iexact=searchArg).order_by("-PostDate") 
                    seralizer =searchItemSeralizer(qs,many=True)
                    return Response(seralizer.data ,status=200)
             elif searchType =="Hall":
                    #Hallobj = Profile.objects.get(Hall=searchArg)
                    # keep thing simiple RAW SQL
                    qs= Post.objects.raw("SELECT * FROM Post as p INNER JOIN auth_user as u on p.Userid_id=u.id INNER JOIN Profile as pro on P.Userid_id= pro.Userid_id WHERE Hall=%s ORDER BY PostDate DESC",[searchArg])
                    seralizer=searchItemSeralizer(qs,many=True)
                    return Response(seralizer.data ,status=200)


        return Response({"Result": -1}, status=500) 
        


  


    def get(self,request,format=None):
        return Response({"Result": -1}, status=500) 



#JSON format to POST Item
#postid is the post 

#Due to the model of Post and aut_user had a Many to  1 relation 
#the model.seralizer need an User instance in that the case just pass in 1 which is the UID of the administrator
#  {
#    "Userid":1,
#    "username": "user2",
#    "ItemName":"Apple2",
#    "Category":"Iphone",
#    "Description":"NOT 4 SALE",
#    "postDate":"2020-10-10",
#    "ImageId": "Apple"
#   }

@api_view(['POST','GET'] )
def postItem(request,*args, **kwargs):
    create_post_seralizer = PostItemSeralizer(data=request.data)

    if create_post_seralizer.is_valid(raise_exception=True):
        #create_user_seralizer.save(is_active='False')
        result_value=create_post_seralizer.CreatePost(request.data)

        data= {
        "Result": result_value
        }
    return Response(data, status=200) 



#use this with list_user_view

#JSON FORMAT
#{
#    "Postid" : 6
#}

@api_view(['POST','GET'] )
def DeleteItem(request,*args, **kwargs):
    Delete_post_seralizer = DeleteItemSeralizer()
    resultvalue = Delete_post_seralizer.DeletePost(request.data)
 
    
    data= {
    "Result": resultvalue
    }
    return Response(data, status=200) 




#-------------------------------------------CRUD Order table -------------------------------
#JSON format to POST Item
#Userid just leave it 1 

#Due to the model of Order and aut_user had a Many to  1 relation 
#and Order to Post therefore Please follow the syntax case senstive
#Postid is the postid of the item
#userid Leave it at 1
#Date format is YYYY-MM-DD"
#Time hr:mm
#movingService True or False
#  {
#     "Postid":5,
#     "Userid":1,
#     "username": "user2",
#     "Date":"2020-12-10",
#     "Time":"20:20",
#     "location":"Sing",
#     "movingService":"False/True"
#  }

@api_view(['POST','GET'] )
def makeOrder(request,*args, **kwargs):

    create_order_seralizer = MakeOrderSeralizer(data=request.data)

    if create_order_seralizer.is_valid(raise_exception=True):
        #create_user_seralizer.save(is_active='False')
        result_value=create_order_seralizer.makeOrder(request.data)
        data= {
        "Result": result_value
        }
    return Response(data, status=200) 





#-------------------------------REFERENCE CODE-------------------------------------------------------------------
# @api_view(['GET'])
# #This will throw an error if user is not authenticated 
# #@authentication_classes(['SessionAuthentication'])
# #@permission_classes([IsAuthenticated])
# def list_view(request,*args  ,**kwargs):
#     qs = Tweet.objects.all()
    
#     seralizer = TweetSerializer(qs, many=True)

   
#     return Response(seralizer.data ,status=200)



# @api_view(['GET'])
# def single_tweet_view(request, tweet_id ,*args ,**kwargs):

#     qs = Tweet.objects.filter(id= tweet_id)

#     if not qs.exists: 
#         print("This is a test ")
#         return Response({} ,status=404)

#     obj = qs.first()
#     if obj == None: 
#         return Response({} ,status=404)
        
#     seralizer = TweetSerializer(obj)
#     return Response(seralizer.data ,status=200)




# #this method only support POST  and must authenticated
# #WE CAN USE CLASS BASED VIEW TO help prevent repeating code 
# @api_view(['POST'])
# def create_tweet_view(request ,*args ,**kwargs):

#     serializer = TweetSerializer(data=request.POST)

#     #send back what the error is before
#     if serializer.is_valid(raise_exception=True):
#         serializer.save(user=request.user)
#         return Response(serializer.data, status=201)

#     return Response({},status =400)




# #THE MAINPAGE
# def home_view(request, *args,**kwargs):
#     #return HttpResponse("<h1> This is just a basic view for HTML</h1>")
#     return render(request,'public/index.html',context={},status=200)
