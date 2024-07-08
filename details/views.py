from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.response import Response


from rest_framework import serializers
from rest_framework import status
from rest_framework.exceptions import AuthenticationFailed
from .serializers import Userserializer, Organizationserializer
from .models import User, Organization
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
            organization = Organization.objects.create(
                name=f"{user.first_name}'s Organisation",
                description=''
                )
            organization.users.add(user)
            payload = {
                'id': user.id,
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
                    "userId": user.id,
                    "firstName": user.first_name,
                    "lastName": user.last_name,
                    "email": user.email,
                    "phone": str(user.phone),
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
            'id': user.id,
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
                "userId": user.id,
                "firstName": user.first_name,
                "lastName": user.last_name,
                "email": user.email,
                "phone": str(user.phone),
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
def users_record(request, Id):
    payload = authenticate(request)
    current_user = User.objects.get(id=payload['id'])
    if current_user:
        organizations = current_user.organizations.all()
        print(organizations)
        for organization in organizations:
            print(organization)
            for user in organization.users.all():
                if user.id == Id:
                    g_user = User.objects.get(pk=Id)
                    response = Response({
                        "status": "success",
                        "message": "User in common organization",
                        "data": {
                            "user": {
                                "userId": g_user.id,
                                "firstName": g_user.first_name,
                                "lastName": g_user.last_name,
                                "email": g_user.email,
                                "phone": str(g_user.phone),
                            }
                        }
                    }, status=status.HTTP_200_OK)
                    return response
        return Response({
            "error": "you have no common organization with this user"
        })

class current_user_membership(APIView):
    def get(self, request):
        payload = authenticate(request)
        current_user = User.objects.get(id=payload['id'])
        if current_user:
            organizations = current_user.organizations.all()
            return Response({
                "status": "success",
                "message": "organizations i belong to",
                "data": {
                    "organizations": [
                    {
                        "orgId": organization.id,
                        "name": organization.name,
                        "description": organization.description,
                    } for organization in organizations
                    ]
                }
            }, status=status.HTTP_200_OK)
        
    def post(self, request):
        payload = authenticate(request)
        current_user = User.objects.get(id=payload['id'])
        if current_user:
            try:
                organization = Organization.objects.create(name=request.data['name'], description=request.data['description'])
                response = Response({
                            "status": "success",
                            "message": "Organisation created successfully",
                            "data": {
                            "orgId": organization.id, 
                            "name": organization.name, 
                            "description": organization.description
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
    current_user = User.objects.get(id=payload['id'])
    if current_user:
        try:
            organization = Organization.objects.get(pk=orgId)
            print(organization)
            return Response({
                "status": "success",
                "message": "organization found",
                "data": {
                        "orgId": organization.id,
                        "name": organization.name,
                        "description": organization.description,
                }
            }, status=status.HTTP_200_OK)
        except:
            return Response({
                    "error": "There is no organization with the provided id"
                })
@api_view(['POST'])
def user_orgg(request, orgId):
    try:
        user = User.objects.get(id=request.data['userId'])
        organization = Organization.objects.get(id=orgId)
        organization.users.add(user)
        organization.save()
        return Response({
            "status": "success",
            "message": "User added to organisation successfully",
        }, status=status.HTTP_200_OK)
    except:
        return Response({
                    "error": "Adding user to organization failed"
                })


