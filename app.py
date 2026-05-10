import json
import os
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

DATA_FILE = os.path.join(os.path.dirname(__file__), "doit_tasks.json")
STATUSES = ["Yet to Start", "Pending", "Done"]


def load_tasks():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            tasks = json.load(f)
        for t in tasks:
            if "status" not in t:
                t["status"] = "Done" if t.pop("done", False) else "Yet to Start"
            if "updated" not in t:
                t["updated"] = t.get("created", "")
            # migrate old single comment to list
            if "comments" not in t:
                old = t.pop("comment", "")
                old_time = t.pop("comment_time", "")
                t["comments"] = [{"id": 1, "text": old, "timestamp": old_time}] if old else []
            else:
                t.pop("comment", None)
                t.pop("comment_time", None)
        return tasks
    return []


def save_tasks(tasks):
    with open(DATA_FILE, "w") as f:
        json.dump(tasks, f, indent=2)


def next_comment_id(task):
    return max((c["id"] for c in task["comments"]), default=0) + 1


@app.route("/")
def index():
    tasks = load_tasks()
    filter_status = request.args.get("filter", "All")
    counts = {s: sum(1 for t in tasks if t["status"] == s) for s in STATUSES}
    counts["All"] = len(tasks)
    visible = tasks if filter_status == "All" else [t for t in tasks if t["status"] == filter_status]
    return render_template("index.html", tasks=visible, filter_status=filter_status,
                           counts=counts, statuses=STATUSES)


@app.route("/add", methods=["POST"])
def add():
    title = request.form.get("title", "").strip()
    if title:
        tasks = load_tasks()
        tasks.append({
            "id": max((t["id"] for t in tasks), default=0) + 1,
            "title": title,
            "status": "Yet to Start",
            "comments": [],
            "created": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "updated": datetime.now().strftime("%Y-%m-%d %H:%M"),
        })
        save_tasks(tasks)
    return redirect(url_for("index"))


@app.route("/advance/<int:task_id>", methods=["POST"])
def advance(task_id):
    tasks = load_tasks()
    for t in tasks:
        if t["id"] == task_id and t["status"] != "Done":
            t["status"] = STATUSES[STATUSES.index(t["status"]) + 1]
            t["updated"] = datetime.now().strftime("%Y-%m-%d %H:%M")
    save_tasks(tasks)
    return redirect(request.referrer or url_for("index"))


@app.route("/comment/<int:task_id>/add", methods=["POST"])
def comment_add(task_id):
    text = request.form.get("comment", "").strip()
    if text:
        tasks = load_tasks()
        for t in tasks:
            if t["id"] == task_id:
                t["comments"].append({
                    "id": next_comment_id(t),
                    "text": text,
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
                })
                t["updated"] = datetime.now().strftime("%Y-%m-%d %H:%M")
        save_tasks(tasks)
    return redirect(request.referrer or url_for("index"))


@app.route("/comment/<int:task_id>/edit/<int:comment_id>", methods=["POST"])
def comment_edit(task_id, comment_id):
    text = request.form.get("comment", "").strip()
    if text:
        tasks = load_tasks()
        for t in tasks:
            if t["id"] == task_id:
                for c in t["comments"]:
                    if c["id"] == comment_id:
                        c["text"] = text
                        c["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M")
                t["updated"] = datetime.now().strftime("%Y-%m-%d %H:%M")
        save_tasks(tasks)
    return redirect(request.referrer or url_for("index"))


@app.route("/comment/<int:task_id>/delete/<int:comment_id>", methods=["POST"])
def comment_delete(task_id, comment_id):
    tasks = load_tasks()
    for t in tasks:
        if t["id"] == task_id:
            t["comments"] = [c for c in t["comments"] if c["id"] != comment_id]
            t["updated"] = datetime.now().strftime("%Y-%m-%d %H:%M")
    save_tasks(tasks)
    return redirect(request.referrer or url_for("index"))


@app.route("/edit/<int:task_id>", methods=["POST"])
def edit_task(task_id):
    title = request.form.get("title", "").strip()
    if title:
        tasks = load_tasks()
        for t in tasks:
            if t["id"] == task_id:
                t["title"] = title
                t["updated"] = datetime.now().strftime("%Y-%m-%d %H:%M")
        save_tasks(tasks)
    return redirect(request.referrer or url_for("index"))


@app.route("/delete/<int:task_id>", methods=["POST"])
def delete(task_id):
    tasks = load_tasks()
    tasks = [t for t in tasks if t["id"] != task_id]
    save_tasks(tasks)
    return redirect(request.referrer or url_for("index"))


@app.route("/clear", methods=["POST"])
def clear():
    tasks = load_tasks()
    tasks = [t for t in tasks if t["status"] != "Done"]
    save_tasks(tasks)
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
