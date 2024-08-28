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

@login_required
def index(request):
    users = User.objects.exclude(id=request.user.id)
    groups = ChatGroup.objects.filter(members=request.user)
    context = {'users': users, 'groups': groups}
    return render(request, 'a_rtchat/index.html', context)

@login_required
def chat_view(request, chatroom_name='public-chat'):
    chat_group = get_object_or_404(ChatGroup, group_name=chatroom_name)
    chat_messages = chat_group.chat_messages.all()[:30]
    form = ChatmessageCreateForm()

    other_user = None
    if chat_group.is_private:
        if request.user not in chat_group.members.all():
            raise Http404()
        other_user = next((member for member in chat_group.members.all() if member != request.user), None)

    if request.user not in chat_group.members.all():
        if request.user.emailaddress_set.filter(verified=True).exists():
            chat_group.members.add(request.user)
        else:
            messages.warning(request, 'You need to verify your email to join the chat!')
            return redirect('profile-settings')

    if request.method == 'POST' and request.headers.get('HX-Request'):
        form = ChatmessageCreateForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.author = request.user
            message.group = chat_group
            message.save()

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
            context = {'message': message, 'user': request.user}
            return render(request, 'a_rtchat/partials/chat_message_p.html', context)
        else:
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
    my_chatrooms = request.user.chat_groups.filter(is_private=True)

    chatroom = my_chatrooms.filter(members=other_user).first()
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

    context = {'form': form}
    return render(request, 'a_rtchat/create_groupchat.html', context)

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

            remove_members = request.POST.getlist('remove_members')
            for member_id in remove_members:
                member = get_object_or_404(User, id=member_id)
                chat_group.members.remove(member)

            return redirect('chatroom', chatroom_name)

    context = {'form': form, 'chat_group': chat_group}
    return render(request, 'a_rtchat/chatroom_edit.html', context)

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
        message = GroupMessage.objects.create(
            file=file,
            author=request.user,
            group=chat_group,
        )

        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f'chat_{chatroom_name}',
            {
                'type': 'chat_message',
                'message': {
                    'author': request.user.username,
                    'file_url': message.file.url,
                    'timestamp': message.created.isoformat(),
                }
            }
        )
        context = {'message': message, 'user': request.user}
        return render(request, 'a_rtchat/partials/message_content.html', context)

    return HttpResponse(status=204)

@login_required
def search_messages(request, chatroom_name):
    chat_group = get_object_or_404(ChatGroup, group_name=chatroom_name)
    query = request.GET.get('q', '')
    if query:
        results = chat_group.chat_messages.filter(Q(text__icontains=query))
    else:
        results = chat_group.chat_messages.none()

    context = {'results': results, 'chatroom_name': chatroom_name, 'chat_group': chat_group}
    return render(request, 'a_rtchat/search_results.html', context)

@login_required
@csrf_exempt
def typing_indicator(request, chatroom_name):
    chat_group = get_object_or_404(ChatGroup, group_name=chatroom_name)

    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f'chat_{chatroom_name}',
        {
            'type': 'typing_status',
            'message': {
                'user': request.user.username,
                'status': 'typing'
            }
        }
    )
    return HttpResponse(status=204)

@login_required
@csrf_exempt
def send_message(request):
    if request.method == "POST":
        message_text = request.POST.get('message')
        chatroom_name = request.POST.get('chatroom_name')
        chat_group = get_object_or_404(ChatGroup, group_name=chatroom_name)

        message = GroupMessage.objects.create(
            text=message_text,
            author=request.user,
            group=chat_group,
        )

        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f'chat_{chatroom_name}',
            {
                'type': 'chat_message',
                'message': {
                    'author': request.user.username,
                    'text': message_text,
                    'timestamp': message.created.isoformat(),
                    'status': 'sent',
                }
            }
        )
        return JsonResponse({'message': message_text, 'author': request.user.username, 'timestamp': message.created.isoformat()})

    return JsonResponse({'error': 'Invalid request'}, status=400)
