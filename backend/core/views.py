from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.decorators import action
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import User, Ticket, Message
from .serializers import (
    UserSerializer,
    RegisterSerializer,
    AdminUserCreateSerializer,
    TicketSerializer,
    MessageSerializer,
)


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    username_field = 'email'

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['email'] = user.email
        token['role'] = user.role
        return token


class LoginView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
    permission_classes = [AllowAny]


class LogoutView(APIView):
    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"detail": "Logout successful"}, status=status.HTTP_200_OK)
        except Exception:
            return Response({"detail": "Invalid refresh token"}, status=status.HTTP_400_BAD_REQUEST)


class TicketViewSet(viewsets.ModelViewSet):
    serializer_class = TicketSerializer

    def get_queryset(self):
        user = self.request.user

        if user.role == 'admin':
            return Ticket.objects.all().order_by('-created_at')

        if user.role == 'agent':
            return Ticket.objects.filter(status='open').order_by('-created_at')

        return Ticket.objects.filter(created_by=user).order_by('-created_at')

    def perform_create(self, serializer):
        if self.request.user.role != 'customer':
            raise PermissionError("Only customers can create tickets.")
        serializer.save(created_by=self.request.user)

    def partial_update(self, request, *args, **kwargs):
        ticket = self.get_object()
        user = request.user

        if user.role == 'customer':
            if ticket.created_by != user:
                return Response({"detail": "Forbidden"}, status=status.HTTP_403_FORBIDDEN)

            allowed_fields = {'title', 'description'}
            requested_fields = set(request.data.keys())

            if not requested_fields.issubset(allowed_fields):
                return Response(
                    {"detail": "Customer can only update title and description."},
                    status=status.HTTP_403_FORBIDDEN
                )

        elif user.role == 'agent':
            return Response(
                {"detail": "Agent cannot use this endpoint to update ticket."},
                status=status.HTTP_403_FORBIDDEN
            )

        return super().partial_update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        if request.user.role != 'admin':
            return Response({"detail": "Only admin can delete tickets."}, status=status.HTTP_403_FORBIDDEN)
        return super().destroy(request, *args, **kwargs)

    @action(detail=True, methods=['patch'])
    def assign(self, request, pk=None):
        if request.user.role != 'admin':
            return Response({"detail": "Only admin can assign tickets."}, status=status.HTTP_403_FORBIDDEN)

        ticket = self.get_object()
        agent_id = request.data.get('assigned_to')

        try:
            agent = User.objects.get(id=agent_id, role='agent')
        except User.DoesNotExist:
            return Response({"detail": "Agent not found."}, status=status.HTTP_404_NOT_FOUND)

        ticket.assigned_to = agent
        ticket.save()
        return Response(TicketSerializer(ticket).data)

    @action(detail=True, methods=['patch'])
    def status(self, request, pk=None):
        if request.user.role != 'agent':
            return Response({"detail": "Only agent can update status."}, status=status.HTTP_403_FORBIDDEN)

        ticket = self.get_object()
        new_status = request.data.get('status')

        valid_statuses = ['open', 'in_progress', 'resolved', 'closed']
        if new_status not in valid_statuses:
            return Response({"detail": "Invalid status."}, status=status.HTTP_400_BAD_REQUEST)

        ticket.status = new_status
        ticket.save()
        return Response(TicketSerializer(ticket).data)

    @action(detail=True, methods=['patch'])
    def priority(self, request, pk=None):
        if request.user.role != 'admin':
            return Response({"detail": "Only admin can update priority."}, status=status.HTTP_403_FORBIDDEN)

        ticket = self.get_object()
        new_priority = request.data.get('priority')

        valid_priorities = ['low', 'medium', 'high']
        if new_priority not in valid_priorities:
            return Response({"detail": "Invalid priority."}, status=status.HTTP_400_BAD_REQUEST)

        ticket.priority = new_priority
        ticket.save()
        return Response(TicketSerializer(ticket).data)

    @action(detail=True, methods=['post'])
    def close(self, request, pk=None):
        if request.user.role not in ['agent', 'admin']:
            return Response({"detail": "Forbidden"}, status=status.HTTP_403_FORBIDDEN)

        ticket = self.get_object()
        ticket.status = 'closed'
        ticket.save()
        return Response(TicketSerializer(ticket).data)


class TicketMessagesView(APIView):
    def get_ticket(self, ticket_id):
        try:
            return Ticket.objects.get(id=ticket_id)
        except Ticket.DoesNotExist:
            return None

    def get(self, request, ticket_id):
        ticket = self.get_ticket(ticket_id)
        if not ticket:
            return Response({"detail": "Ticket not found."}, status=status.HTTP_404_NOT_FOUND)

        if request.user.role == 'customer' and ticket.created_by != request.user:
            return Response({"detail": "Forbidden"}, status=status.HTTP_403_FORBIDDEN)

        messages = ticket.messages.all().order_by('created_at')
        return Response(MessageSerializer(messages, many=True).data)

    def post(self, request, ticket_id):
        ticket = self.get_ticket(ticket_id)
        if not ticket:
            return Response({"detail": "Ticket not found."}, status=status.HTTP_404_NOT_FOUND)

        if request.user.role == 'customer' and ticket.created_by != request.user:
            return Response({"detail": "Forbidden"}, status=status.HTTP_403_FORBIDDEN)

        serializer = MessageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(ticket=ticket, author=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by('id')

    def get_serializer_class(self):
        if self.action == 'create':
            return AdminUserCreateSerializer
        return UserSerializer

    def list(self, request, *args, **kwargs):
        if request.user.role != 'admin':
            return Response({"detail": "Forbidden"}, status=status.HTTP_403_FORBIDDEN)
        return super().list(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        if request.user.role != 'admin':
            return Response({"detail": "Forbidden"}, status=status.HTTP_403_FORBIDDEN)
        return super().retrieve(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        if request.user.role != 'admin':
            return Response({"detail": "Forbidden"}, status=status.HTTP_403_FORBIDDEN)
        return super().create(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        if request.user.role != 'admin':
            return Response({"detail": "Forbidden"}, status=status.HTTP_403_FORBIDDEN)
        return super().partial_update(request, *args, **kwargs)

    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        if request.user.role != 'admin':
            return Response({"detail": "Forbidden"}, status=status.HTTP_403_FORBIDDEN)

        user = self.get_object()
        user.is_active = False
        user.save()
        return Response(UserSerializer(user).data)