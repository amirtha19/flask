from flask import (render_template, url_for, flash,
                   redirect, request, abort, Blueprint, send_from_directory)
from flask_login import current_user, login_required
from flaskblog import db
from flaskblog.models import Post,Experience
from flaskblog.posts.forms import PostForm,ExperienceForm
import os


posts = Blueprint('posts', __name__)
posts.config = {
    'UPLOAD_FOLDER': os.path.join(os.getcwd(), 'static', 'videos'),
    'ALLOWED_EXTENSIONS': {'mp4'}
}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in posts.config['ALLOWED_EXTENSIONS']

@posts.route('/upload', methods=['POST'])
def upload_video():
    if 'video' not in request.files:
        return redirect(request.url)
    
    video_file = request.files['video']

    if video_file.filename == '':
        return redirect(request.url)
    
    if video_file and allowed_file(video_file.filename):
        video_path = os.path.join(posts.config['UPLOAD_FOLDER'], video_file.filename)
        video_file.save(video_path)
        return redirect(url_for('posts.play_video1', filename=video_file.filename))
    
    return "Invalid file format"

@posts.route('/video/<filename>')
def play_video1(filename):
    video_url = f"/static/videos/{filename}"
    return render_template('video.html', video_url=video_url)
@posts.route("/video/<filename>")
@login_required
def play_video(filename):
    return render_template('video.html', video_url=filename)

@posts.route('/static/videos/<filename>')
def serve_video(filename):
    return send_from_directory(posts.config['UPLOAD_FOLDER'], filename)











@posts.route("/post/new", methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title=form.title.data, content=form.content.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Your post has been created!', 'success')
        return redirect(url_for('main.home'))
    return render_template('create_post.html', title='New Library',
                           form=form, legend='New Library')

@posts.route("/experience/new", methods=['GET', 'POST'])
@login_required
def new_experience():
    form = ExperienceForm()
    if form.validate_on_submit():
        experience = Experience(title=form.etitle.data, content=form.econtent.data, author=current_user)
        db.session.add(experience)
        db.session.commit()
        flash('Your post has been created!', 'success')
        return redirect(url_for('main.home'))
    return render_template('create_experience.html', etitle='New Experience',
                           form=form, legend='New Experience')
@posts.route("/libraries/existing", methods=['GET', 'POST'])
@login_required
def existing_experience():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)
    
    return render_template('existing_libraries.html', posts=posts)
    
    
   # return render_template('existing_libraries.html', etitle='Existing Libraries',
   #                         legend='Existing Libraries')






@posts.route("/post/<int:post_id>")
def post(post_id):
    post = Post.query.get_or_404(post_id)
    video_dir = 'static/videos'
    videos = [video for video in os.listdir(video_dir) if video.endswith('.mp4')]
    return render_template('post.html', title=post.title, post=post, videos=videos)


@posts.route("/post/<int:post_id>/update", methods=['GET', 'POST'])
@login_required
def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()
        flash('Your post has been updated!', 'success')
        return redirect(url_for('posts.post', post_id=post.id))
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content
    return render_template('create_post.html', title='Update Post',
                           form=form, legend='Update Post')


@posts.route("/post/<int:post_id>/delete", methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('Your post has been deleted!', 'success')
    return redirect(url_for('main.home'))

