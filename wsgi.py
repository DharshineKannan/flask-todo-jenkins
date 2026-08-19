from app import app, db


# Create the schema before Gunicorn starts serving requests. Database migrations
# should replace create_all() when the schema begins evolving between releases.
with app.app_context():
    db.create_all()
