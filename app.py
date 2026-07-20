import os
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Fetch the database URL from your docker-compose environment settings
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    'DATABASE_URL', 
    'postgresql://tododb_user:password@localhost:5432/tododb'
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
STATUSES = ["Yet to Start", "Pending", "Done"]

# ==========================================
# DATABASE MODELS (SCHEMA)
# ==========================================

class Task(db.Model):
    __tablename__ = 'tasks'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    status = db.Column(db.String(50), default="Yet to Start")
    created = db.Column(db.String(50), default=lambda: datetime.now().strftime("%Y-%m-%d %H:%M"))
    updated = db.Column(db.String(50), default=lambda: datetime.now().strftime("%Y-%m-%d %H:%M"))
    
    # Cascade ensures that when a task is deleted, its comments are deleted too
    comments = db.relationship('Comment', backref='task', cascade="all, delete-orphan", lazy=True)

class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.String(50), default=lambda: datetime.now().strftime("%Y-%m-%d %H:%M"))
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id'), nullable=False)

# ==========================================
# APPLICATION ROUTES
# ==========================================

@app.route("/")
def index():
    filter_status = request.args.get("filter", "All")
    
    # Fetch all tasks to compute summary counts
    all_tasks = Task.query.all()
    counts = {s: sum(1 for t in all_tasks if t.status == s) for s in STATUSES}
    counts["All"] = len(all_tasks)
    
    # Filter specific tasks based on query params
    if filter_status == "All":
        visible = all_tasks
    else:
        visible = Task.query.filter_by(status=filter_status).all()
        
    return render_template("index.html", tasks=visible, filter_status=filter_status,
                           counts=counts, statuses=STATUSES)


@app.route("/add", methods=["POST"])
def add():
    title = request.form.get("title", "").strip()
    if title:
        new_task = Task(title=title)
        db.session.add(new_task)
        db.session.commit()
    return redirect(url_for("index"))


@app.route("/advance/<int:task_id>", methods=["POST"])
def advance(task_id):
    task = Task.query.get_or_404(task_id)
    if task.status != "Done":
        current_index = STATUSES.index(task.status)
        task.status = STATUSES[current_index + 1]
        task.updated = datetime.now().strftime("%Y-%m-%d %H:%M")
        db.session.commit()
    return redirect(request.referrer or url_for("index"))


@app.route("/edit/<int:task_id>", methods=["POST"])
def edit_task(task_id):
    title = request.form.get("title", "").strip()
    if title:
        task = Task.query.get_or_404(task_id)
        task.title = title
        task.updated = datetime.now().strftime("%Y-%m-%d %H:%M")
        db.session.commit()
    return redirect(request.referrer or url_for("index"))


@app.route("/delete/<int:task_id>", methods=["POST"])
def delete(task_id):
    task = Task.query.get_or_404(task_id)
    db.session.delete(task)
    db.session.commit()
    return redirect(request.referrer or url_for("index"))


@app.route("/clear", methods=["POST"])
def clear():
    # Delete all tasks where status is "Done"
    Task.query.filter_by(status="Done").delete()
    db.session.commit()
    return redirect(url_for("index"))


# ==========================================
# NESTED COMMENT ROUTES
# ==========================================

@app.route("/comment/<int:task_id>/add", methods=["POST"])
def comment_add(task_id):
    text = request.form.get("comment", "").strip()
    if text:
        task = Task.query.get_or_404(task_id)
        new_comment = Comment(text=text, task_id=task.id)
        task.updated = datetime.now().strftime("%Y-%m-%d %H:%M")
        db.session.add(new_comment)
        db.session.commit()
    return redirect(request.referrer or url_for("index"))


@app.route("/comment/<int:task_id>/edit/<int:comment_id>", methods=["POST"])
def comment_edit(task_id, comment_id):
    text = request.form.get("comment", "").strip()
    if text:
        task = Task.query.get_or_404(task_id)
        comment = Comment.query.filter_by(id=comment_id, task_id=task_id).first_or_404()
        comment.text = text
        comment.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        task.updated = datetime.now().strftime("%Y-%m-%d %H:%M")
        db.session.commit()
    return redirect(request.referrer or url_for("index"))


@app.route("/comment/<int:task_id>/delete/<int:comment_id>", methods=["POST"])
def comment_delete(task_id, comment_id):
    task = Task.query.get_or_404(task_id)
    comment = Comment.query.filter_by(id=comment_id, task_id=task_id).first_or_404()
    db.session.delete(comment)
    task.updated = datetime.now().strftime("%Y-%m-%d %H:%M")
    db.session.commit()
    return redirect(request.referrer or url_for("index"))


if __name__ == "__main__":
    # Create the relational database tables before the server accepts traffic
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000, debug=True)
