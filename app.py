from flask import Flask, render_template, redirect, session, flash
from flask_debugtoolbar import DebugToolbarExtension
from models import connect_db, db, User, Tweet
from forms import UserForm, TweetForm
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://postgres:admin@localhost/auth_demo"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True
app.config["SECRET_KEY"] = "abc123"
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False


connect_db(app)
db.create_all()

toolbar = DebugToolbarExtension(app)


@app.route('/')
def home_page():
    return render_template('index.html')

@app.route('/tweets', methods=['GET', 'POST'])
def show_tweets():
    
    if 'user_id' not in session:
        flash('please login to view tweets', 'danger')
        return redirect('/')
    
    tweetForm = TweetForm()
    all_tweets = Tweet.query.all()
    if tweetForm.validate_on_submit():
        text = tweetForm.text.data
        new_tweet = Tweet(text=text, user_id=session['user_id'])
        db.session.add(new_tweet)
        db.session.commit()
        flash('TWEET CREATED', 'success')
        return redirect('/tweets')

    return render_template('tweets.html', form=tweetForm, tweets=all_tweets)

@app.route('/tweets/<int:id>/', methods=['POST'])
def delete_tweet(id):

    tweet = Tweet.query.get_or_404(id)
    if tweet.user_id == session['user_id']:
        db.session.delete(tweet)
        db.session.commit()
        flash('tweet deleted', 'info')
        return redirect('/tweets')
    flash("you don't have permission to do that")
    return redirect('/tweets')

@app.route('/register', methods=['GET', 'POST'])
def register_user():
    form = UserForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        
        new_user = User.register(username, password)
        
        db.session.add(new_user)
        db.session.commit()
        session['user_id'] = new_user.id

        flash('Welcome. Successfully created your account', 'success')
        return redirect('/tweets')
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login_user():
    form = UserForm()
    
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        
        user = User.authenticate(username, password)
        if user:
            flash(f'Welcome back {user.username}', 'primary')
            session['user_id'] = user.id
            return redirect('/tweets')
        else:
            form.username.errors = ['INVALID USERNAME/PASSWORD']
            
    
    
    return render_template('/login.html', form=form)





@app.route('/logout')
def logout_user():
    session.pop('user_id')
    flash('goodbye!', 'info')
    return redirect('/')