from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.core.exceptions import ObjectDoesNotExist
from .forms import SignupForm, LoginForm, VideoForm, VideoSearchForm
from .models import Video
import cv2
import threading
from django.http import StreamingHttpResponse,HttpResponseServerError,HttpResponse
from django.views.decorators import gzip
from pytube import YouTube
from urllib.parse import unquote


# Create your views here.
# Home page
def index(request):
    return render(request, 'index.html')

# signup page
def user_signup(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = SignupForm()
    return render(request, 'signup.html', {'form': form})

# login page
def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                return redirect('all_videos')
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})

# logout page
def user_logout(request):
    logout(request)
    return redirect('login')

def create_video(request):
    if request.method == 'POST':
        form = VideoForm(request.POST)
        if form.is_valid():
            video = form.save(commit=False)
            video.user = request.user
            video.save()
            return redirect('all_videos')
    else:
        form = VideoForm()
    return render(request, 'create_video.html', {'form': form})

def edit_video(request, pk):
    try:
        video = Video.objects.get(pk=pk, user=request.user)
    except ObjectDoesNotExist:
        # Video does not exist or user doesn't have permission
        return redirect('permission_denied')

    if request.method == 'POST':
        form = VideoForm(request.POST, instance=video)
        if form.is_valid():
            video = form.save()
            return redirect('all_videos')
    else:
        form = VideoForm(instance=video)
    return render(request, 'edit_video.html', {'form': form})


def delete_video_confirm(request, pk):
    try:
        video = Video.objects.get(pk=pk, user=request.user)
    except ObjectDoesNotExist:
        # Video does not exist or user doesn't have permission
        return redirect('permission_denied')

    return render(request, 'delete_video.html', {'video': video})


def permission_denied(request):
    return render(request, 'permission_denied.html')
def delete_video(request, pk):
    if request.method == 'POST':
        video = get_object_or_404(Video, pk=pk, user=request.user)
        if video:
            video.delete()
            return redirect('all_videos')
    return redirect('confirm_delete_video', pk=pk)



def all_videos(request):
    videos = Video.objects.all()
    search_form = VideoSearchForm(request.GET)  # Bind request data to the form

    if search_form.is_valid():
        query = search_form.cleaned_data['query']
        videos = videos.filter(name__icontains=query)

    return render(request, 'all_videos.html', {'videos': videos, 'search_form': search_form})

# def video_player_view(request, video_url):
#     # Render the video player template and pass the video URL to it
#     return render(request, 'video_player.html', {'video_url': video_url})


def video_detail(request, pk):
    # Retrieve the video object with the given primary key (pk) from the database
    video = get_object_or_404(Video, pk=pk)

    # Render the video detail template with the video object
    return render(request, 'video_detail.html', {'video': video})


class VideoCamera:
    def __init__(self, video_path):
        self.video = cv2.VideoCapture(video_path)
        self.lock = threading.Lock()

    def __del__(self):
        self.video.release()

    def get_frame(self):
        success, image = self.video.read()
        if success:
            ret, jpeg = cv2.imencode('.jpg', image)
            return jpeg.tobytes()
        else:
            return None


def frame_generator(camera):
    while True:
        with camera.lock:
            ret, frame = camera.video.read()
        if not ret:
            break
        ret, jpeg = cv2.imencode('.jpg', frame)
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n').decode(errors='ignore')




def handle_video_feed(camera):
    try:
        response = StreamingHttpResponse(frame_generator(camera),
                                         content_type='multipart/x-mixed-replace; boundary=frame')
        response['Content-Disposition'] = 'inline; filename="video_stream"'
        return response
    except Exception as e:
        return HttpResponseServerError(f"Error: {str(e)}")

@gzip.gzip_page
def video_feed(request, video_path):
    try:
        # Decode the video path
        decoded_video_path = unquote(video_path)
        print(decoded_video_path)
        # Download YouTube video and open it using OpenCV
        yt = YouTube(decoded_video_path)
        video_stream = yt.streams.filter(file_extension='mp4').first()
        video_path = video_stream.download(filename='temp_video')
        print(video_path)

        # Create a VideoCamera object
        camera = VideoCamera(video_path)

        # Create a new thread for handling the video feed
        thread = threading.Thread(target=handle_video_feed, args=(camera,))
        thread.daemon = True  # Daemonize the thread so it exits when the main thread exits
        thread.start()

        return HttpResponse("Video feed started successfully!")  # Return a response indicating the feed started
    except Exception as e:
        return HttpResponseServerError(f"Error: {str(e)}")


def video_player_view(request, video_url, video_name):
    try:
        # Download YouTube video and open it using OpenCV
        yt = YouTube(video_url)
        video_stream = yt.streams.filter(file_extension='mp4').first()
        video_path = video_stream.download(filename='temp_video')


        # Create a VideoCamera object
        camera = VideoCamera(video_path)

        # Define a function to start fetching the video feed data in the background
        def start_video_feed():
            video_feed_data = ''.join(frame_generator(camera))
            # Update the video player view with the feed data
            response = StreamingHttpResponse(video_feed_data, content_type='multipart/x-mixed-replace; boundary=frame')
            return response

        # Start fetching the video feed data in a separate thread
        thread = threading.Thread(target=start_video_feed)
        thread.daemon = True
        thread.start()

        # Render the video player template with video name
        return render(request, 'video_player.html', {'video_name': video_name})

    except Exception as e:
        return render(request, 'error.html', {'error_message': str(e)})

