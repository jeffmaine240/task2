from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.response import Response


from rest_framework import serializers
from rest_framework import status
from rest_framework.exceptions import AuthenticationFailed
from .serializers import Userserializer
from .models import User, Organisation
import jwt, datetime

# Create your views here.


@api_view(['POST'])
def user_register(request):
    try:
        try:
            serializer = Userserializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            user = User.objects.get(email=request.data['email'])
            user.set_password(request.data['password'])
            user.save()
            print('cool')
            organisation = Organisation.objects.create(
                name=f"{user.firstName}'s Organisation",
                description=''
                )
            organisation.users.add(user)
            payload = {
                'id': user.userId,
                'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30),
                'iat': datetime.datetime.utcnow()
            }
            token = jwt.encode(payload, "secret", algorithm='HS256')
            return Response({
                "status": "success",
                "message": "Registration successful",
                "data": {
                "accessToken": token,
                "user": {
                    "userId": user.userId,
                    "firstName": user.firstName,
                    "lastName": user.lastName,
                    "email": user.email,
                    "phone": user.phone,
                }
                }
            }, status=status.HTTP_201_CREATED)
        except serializers.ValidationError as exc:
            errors = [
                    {"field": field, "message": message}
                    for field, messages in exc.detail.items()
                    for message in (messages if isinstance(messages, list) else [messages])
                ]
            return Response({"errors": errors}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
    except:
        return Response({
            "status": "Bad request",
            "message": "Registration unsuccessful",
            "statusCode": 400
        }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def login(request):
    try:
        user = User.objects.get(email=request.data['email'])
    except:
        return Response({
            "status": "Bad request",
            "message": "Authentication failed",
            "statusCode": 401
            }, status=status.HTTP_401_UNAUTHORIZED)
    if not user.check_password(request.data['password']):
        return Response({
            "status": "Bad request",
            "message": "Authentication failed",
            "statusCode": 401
            }, status=status.HTTP_401_UNAUTHORIZED)
    payload = {
            'id': user.userId,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30),
            'iat': datetime.datetime.utcnow()
        }
    token = jwt.encode(payload, "secret", algorithm='HS256')

    response = Response({
            "status": "success",
            "message": "Login successful",
            "data": {
            "accessToken": token,
            "user": {
                "userId": user.userId,
                "firstName": user.firstName,
                "lastName": user.lastName,
                "email": user.email,
                "phone": user.phone,
            }
            }
        }, status=status.HTTP_200_OK)
    response.set_cookie(key='jwt', value=token, httponly=True)
    return response

def authenticate(requests):
    token = requests.COOKIES.get('jwt')
    if not token:
        raise AuthenticationFailed('Unauthenticated')
    try:
        payload = jwt.decode(token, 'secret', algorithms='HS256')
    except jwt.ExpiredSignatureError:
        raise AuthenticationFailed('Unauthenticated')
    return payload

@api_view(['GET'])
def users_record(request, id):
    payload = authenticate(request)
    current_user = User.objects.get(userId=payload['id'])
    if current_user:
        organisations = current_user.organisations.all()
        print(organisations)
        for organisation in organisations:
            print(organisation)
            for user in organisation.users.all():
                if user.userId == id:
                    g_user = User.objects.get(pk=id)
                    response = Response({
                        "status": "success",
                        "message": "User in common organisation",
                        "data": {
                            "user": {
                                "userId": g_user.userId,
                                "firstName": g_user.firstName,
                                "lastName": g_user.lastName,
                                "email": g_user.email,
                                "phone": g_user.phone,
                            }
                        }
                    }, status=status.HTTP_200_OK)
                    return response
        return Response({
            "error": "you have no common organisation with this user"
        })

class current_user_membership(APIView):
    def get(self, request):
        payload = authenticate(request)
        current_user = User.objects.get(userId=payload['id'])
        if current_user:
            organisations = current_user.organisations.all()
            return Response({
                "status": "success",
                "message": "organiations i belong to",
                "data": {
                    "organisations": [
                    {
                        "orgId": organisation.orgId,
                        "name": organisation.name,
                        "description": organisation.description,
                    } for organisation in organisations
                    ]
                }
            }, status=status.HTTP_200_OK)
        
    def post(self, request):
        payload = authenticate(request)
        current_user = User.objects.get(userId=payload['id'])
        if current_user:
            try:
                organisation = Organisation.objects.create(name=request.data['name'], description=request.data['description'])
                response = Response({
                            "status": "success",
                            "message": "Organisation created successfully",
                            "data": {
                            "orgId": organisation.orgId, 
                            "name": organisation.name, 
                            "description": organisation.description
                            }
                        }, status=status.HTTP_200_OK)
                return response
            except:
                return Response({
                    "status": "Bad Request",
                    "message": "Client error",
                    "statusCode": 400
                }, status=status.HTTP_400_BAD_REQUEST)



        
@api_view(['GET'])
def organization_details(request, orgId):
    payload = authenticate(request)
    current_user = User.objects.get(userId=payload['id'])
    if current_user:
        try:
            organisation = Organisation.objects.get(pk=orgId)
            print(organisation)
            return Response({
                "status": "success",
                "message": "organisation found",
                "data": {
                        "orgId": organisation.orgId,
                        "name": organisation.name,
                        "description": organisation.description,
                }
            }, status=status.HTTP_200_OK)
        except:
            return Response({
                    "error": "There is no organisation with the provided id"
                })
@api_view(['POST'])
def user_orgg(request, orgId):
    try:
        user = User.objects.get(userId=request.data['userId'])
        organisation = Organisation.objects.get(orgId=orgId)
        organisation.users.add(user)
        organisation.save()
        return Response({
            "status": "success",
            "message": "User added to organisation successfully",
        }, status=status.HTTP_200_OK)
    except:
        return Response({
                    "error": "Adding user to organisation failed"
                })


