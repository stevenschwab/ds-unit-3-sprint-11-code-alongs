from flask import Flask, render_template, request
from spotify import get_song_by_title
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
DB = SQLAlchemy(app)


@app.route('/', methods=['POST', 'GET'])
def root():
    if request.method == "GET":
        # get 5 most recent searches
        recent = RecentSearches.query.all()[-5:]
        # reverse list and display on the page
        return render_template('base.html', recent_searches=recent[::-1])
    elif request.method == "POST":

        song_title = request.values['song_title']
        song = get_song_by_title(song_title)
        if song:
            try:
                db_song = RecentSearches(song_id=song['id'],
                                         title=song['title'],
                                         href=song['href'],
                                         uri=song['uri'])
                DB.session.add(db_song)
            except Exception as e:
                print(f'Error processing {song_title}: {e}')
                raise e
            else:
                DB.session.commit()
                # get 5 most recent searches
                recent = RecentSearches.query.all()[-5:]
                # reverse list and display on the page
                return render_template('base.html', recent_searches=recent[::-1], message='')
        else:
            # get 5 most recent searches
            recent = RecentSearches.query.all()[-5:]
            message = "Sorry, we couldn't find a song with that title."
            return render_template('base.html', recent_searches=recent[::-1], message=message)


@app.route('/reset')
def reset():
    DB.drop_all()
    DB.create_all()
    return render_template('base.html')


# Database Class
class RecentSearches(DB.Model):
    # This allows for IDs to be auto-incremented so that we can have
    # duplicate recent searches (duplicate song_id, not duplicate primary key ids)
    id = DB.Column(DB.BigInteger().with_variant(DB.Integer, "sqlite"), primary_key=True)
    song_id = DB.Column(DB.String(100), nullable=False)
    title = DB.Column(DB.String(200), nullable=False)
    href = DB.Column(DB.String(300), nullable=False)
    uri = DB.Column(DB.String(300), nullable=False)

    def __repr__(self):
        return f"Title: {self.title}"