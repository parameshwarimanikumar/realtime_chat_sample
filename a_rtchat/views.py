from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.http import Http404, HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from .models import ChatGroup, GroupMessage
from .forms import ChatmessageCreateForm, NewGroupForm, ChatRoomEditForm
from django.db.models import Q
from django.core.paginator import Paginator


@login_required
def chat_view(request, chatroom_name='public-chat'):
    chat_group = get_object_or_404(ChatGroup, group_name=chatroom_name)
    chat_messages = chat_group.chat_messages.all().order_by('-created')[:30]  # Fetch last 30 messages
    form = ChatmessageCreateForm()

    other_user = None
    if chat_group.is_private:
        if request.user not in chat_group.members.all():
            raise Http404()
        other_user = chat_group.members.exclude(id=request.user.id).first()

    # Ensure user is in the chat group
    if request.user not in chat_group.members.all():
        if hasattr(request.user, 'emailaddress') and request.user.emailaddress_set.filter(verified=True).exists():
            chat_group.members.add(request.user)
        else:
            messages.warning(request, 'You need to verify your email to join the chat!')
            return redirect('profile-settings')

    # Handle message posting via HTMX request
    if request.method == 'POST' and request.headers.get('HX-Request'):
        form = ChatmessageCreateForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.author = request.user
            message.group = chat_group
            message.save()

            # Send message via WebSocket
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f'chat_{chatroom_name}',
                {
                    'type': 'chat_message',
                    'message': {
                        'author': request.user.username,
                        'text': message.text,
                        'timestamp': message.created.isoformat(),
                        'status': 'sent',
                    }
                }
            )
            context = {'message': message}
            return render(request, 'a_rtchat/partials/chat_message_p.html', context)

        return JsonResponse({'error': 'Invalid form submission'}, status=400)

    context = {
        'chat_messages': chat_messages,
        'form': form,
        'other_user': other_user,
        'chatroom_name': chatroom_name,
        'chat_group': chat_group
    }
    return render(request, 'a_rtchat/chat.html', context)


@login_required
def get_or_create_chatroom(request, username):
    if request.user.username == username:
        return redirect('home')

    other_user = get_object_or_404(User, username=username)
    chatroom = ChatGroup.objects.filter(is_private=True, members=request.user).filter(members=other_user).first()

    if not chatroom:
        chatroom = ChatGroup.objects.create(is_private=True)
        chatroom.members.add(other_user, request.user)

    return redirect('chatroom', chatroom.group_name)


@login_required
def create_groupchat(request):
    form = NewGroupForm()

    if request.method == 'POST':
        form = NewGroupForm(request.POST)
        if form.is_valid():
            new_groupchat = form.save(commit=False)
            new_groupchat.admin = request.user
            new_groupchat.save()
            new_groupchat.members.add(request.user)
            return redirect('chatroom', new_groupchat.group_name)

    return render(request, 'a_rtchat/create_groupchat.html', {'form': form})


@login_required
def chatroom_edit_view(request, chatroom_name):
    chat_group = get_object_or_404(ChatGroup, group_name=chatroom_name)
    if request.user != chat_group.admin:
        raise Http404()

    form = ChatRoomEditForm(instance=chat_group)
    if request.method == 'POST':
        form = ChatRoomEditForm(request.POST, instance=chat_group)
        if form.is_valid():
            form.save()

            # Remove members if selected
            remove_members = request.POST.getlist('remove_members')
            chat_group.members.remove(*remove_members)

            return redirect('chatroom', chatroom_name)

    return render(request, 'a_rtchat/chatroom_edit.html', {'form': form, 'chat_group': chat_group})


@login_required
def chatroom_delete_view(request, chatroom_name):
    chat_group = get_object_or_404(ChatGroup, group_name=chatroom_name)
    if request.user != chat_group.admin:
        raise Http404()

    if request.method == "POST":
        chat_group.delete()
        messages.success(request, 'Chatroom deleted')
        return redirect('home')

    return render(request, 'a_rtchat/chatroom_delete.html', {'chat_group': chat_group})


@login_required
def chatroom_leave_view(request, chatroom_name):
    chat_group = get_object_or_404(ChatGroup, group_name=chatroom_name)
    if request.user not in chat_group.members.all():
        raise Http404()

    if request.method == "POST":
        chat_group.members.remove(request.user)
        messages.success(request, 'You left the chat')
        return redirect('home')

    return render(request, 'a_rtchat/chatroom_leave.html', {'chat_group': chat_group})


@login_required
@csrf_exempt
def chat_file_upload(request, chatroom_name):
    chat_group = get_object_or_404(ChatGroup, group_name=chatroom_name)

    if request.headers.get('HX-Request') and request.FILES:
        file = request.FILES['file']

        # File size limit (5MB)
        if file.size > 5 * 1024 * 1024:
            return JsonResponse({"error": "File too large"}, status=400)

        message = GroupMessage.objects.create(
            file=file,
            author=request.user,
            group=chat_group,
        )

        # Send file message via WebSocket
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f'chat_{chatroom_name}',
            {
                'type': 'chat_message',
                'message': {
                    'author': request.user.username,
                    'file': message.file.url,
                    'timestamp': message.created.isoformat(),
                    'status': 'sent',
                }
            }
        )
        return render(request, 'a_rtchat/partials/chat_message_p.html', {'message': message})

    return HttpResponse('Invalid request', status=400)


@login_required
def search_messages(request, chatroom_name):
    query = request.GET.get('query', '')
    chat_group = get_object_or_404(ChatGroup, group_name=chatroom_name)
    messages = chat_group.chat_messages.filter(Q(text__icontains=query))

    return render(request, 'a_rtchat/partials/search_results.html', {'messages': messages})


@login_required
def typing_indicator(request, chatroom_name):
    chat_group = get_object_or_404(ChatGroup, group_name=chatroom_name)

    if request.headers.get('HX-Request'):
        typing = request.POST.get('typing', 'false').lower() == 'true'

        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f'chat_{chatroom_name}',
            {
                'type': 'typing_status',
                'typing': typing,
                'user': request.user.username,
            }
        )
        return HttpResponse(status=204)

    return HttpResponse('Invalid request', status=400)


@login_required
@csrf_exempt
def send_message(request):
    if request.method == 'POST':
        message_text = request.POST.get('text')
        if message_text:
            return JsonResponse({"status": "success", "message": message_text})

    return JsonResponse({"status": "failure", "error": "Invalid request"}, status=400)
