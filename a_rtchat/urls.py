from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from .views import (
    
    get_or_create_chatroom,
    chat_view,
    create_groupchat,
    chatroom_edit_view,
    chatroom_delete_view,
    chatroom_leave_view,
    chat_file_upload,
    search_messages,
    typing_indicator,
    send_message
)

urlpatterns = [
   
    path('chatroom/<str:username>/', get_or_create_chatroom, name='get_or_create_chatroom'),
    path('', chat_view, name="home"),
    path('chat/<username>', get_or_create_chatroom, name="start-chat"),
    path('chat/room/<chatroom_name>', chat_view, name="chatroom"),
    path('chat/new_groupchat/', create_groupchat, name="new-groupchat"),
    path('chat/edit/<chatroom_name>', chatroom_edit_view, name="edit-chatroom"),
    path('chat/delete/<chatroom_name>', chatroom_delete_view, name="chatroom-delete"),
    path('chat/leave/<chatroom_name>', chatroom_leave_view, name="chatroom-leave"),
    path('chat/file_upload/<chatroom_name>', chat_file_upload, name="chat-file-upload"),
    path('chat/search/<chatroom_name>', search_messages, name="search-messages"),
    path('chat/typing/<chatroom_name>', typing_indicator, name="typing-indicator"),
    path('chat/send_message/', send_message, name="send_message"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
