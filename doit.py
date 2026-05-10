import json
import os
from datetime import datetime

DATA_FILE = os.path.join(os.path.dirname(__file__), "doit_tasks.json")

STATUSES = ["Yet to Start", "Pending", "Done"]


def load_tasks():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            tasks = json.load(f)
        for t in tasks:
            if "status" not in t:
                t["status"] = "Done" if t.pop("done", False) else "Yet to Start"
            if "comment" not in t:
                t["comment"] = ""
            if "updated" not in t:
                t["updated"] = t.get("created", "")
        return tasks
    return []


def save_tasks(tasks):
    with open(DATA_FILE, "w") as f:
        json.dump(tasks, f, indent=2)


def add_task(tasks, title):
    task = {
        "id": max((t["id"] for t in tasks), default=0) + 1,
        "title": title,
        "status": "Yet to Start",
        "comment": "",
        "created": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "updated": datetime.now().strftime("%Y-%m-%d %H:%M"),
    }
    tasks.append(task)
    save_tasks(tasks)
    print(f"  Added: [{task['id']}] {task['title']}  —  Yet to Start")


def list_tasks(tasks, filter_status=None):
    visible = tasks if filter_status is None else [t for t in tasks if t["status"] == filter_status]
    if not visible:
        print("  No tasks found.")
        return
    print()
    print(f"  {'ID':<5} {'Status':<15} {'Created':<18} {'Title':<30} Comment")
    print("  " + "-" * 80)
    for t in visible:
        comment = t.get("comment", "")
        print(f"  {t['id']:<5} {t['status']:<15} {t['created']:<18} {t['title']:<30} {comment}")
    print()


def advance_task(tasks, task_id):
    for t in tasks:
        if t["id"] == task_id:
            current = t["status"]
            if current == "Done":
                print(f"  Task {task_id} is already Done.")
                return
            next_status = STATUSES[STATUSES.index(current) + 1]
            t["status"] = next_status
            t["updated"] = datetime.now().strftime("%Y-%m-%d %H:%M")
            save_tasks(tasks)
            print(f"  Task [{task_id}] moved: {current}  →  {next_status}")
            return
    print(f"  Task {task_id} not found.")


def comment_task(tasks, task_id, comment):
    for t in tasks:
        if t["id"] == task_id:
            t["comment"] = comment
            t["updated"] = datetime.now().strftime("%Y-%m-%d %H:%M")
            save_tasks(tasks)
            print(f"  Comment added to task [{task_id}].")
            return
    print(f"  Task {task_id} not found.")


def delete_task(tasks, task_id):
    for i, t in enumerate(tasks):
        if t["id"] == task_id:
            removed = tasks.pop(i)
            save_tasks(tasks)
            print(f"  Deleted: [{task_id}] {removed['title']}")
            return
    print(f"  Task {task_id} not found.")


def clear_done(tasks):
    before = len(tasks)
    tasks[:] = [t for t in tasks if t["status"] != "Done"]
    save_tasks(tasks)
    print(f"  Cleared {before - len(tasks)} completed task(s).")


def print_help():
    print("""
  Commands:
    add <title>            Add a new task  (starts as 'Yet to Start')
    advance <id>           Move task to next stage: Yet to Start → Pending → Done
    comment <id> <text>    Add or update a comment on a task
    list                   List all tasks
    yts                    List only 'Yet to Start' tasks
    pending                List only 'Pending' tasks
    done                   List only 'Done' tasks
    delete <id>            Delete a task
    clear                  Remove all 'Done' tasks
    help                   Show this help
    quit / exit            Exit DoIt
""")


def main():
    tasks = load_tasks()
    print("\n  DoIt — To-Do List  (type 'help' for commands)\n")

    while True:
        try:
            raw = input("  > ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n  Bye!")
            break

        if not raw:
            continue

        parts = raw.split(maxsplit=2)
        cmd = parts[0].lower()
        arg1 = parts[1] if len(parts) > 1 else ""
        arg2 = parts[2] if len(parts) > 2 else ""

        if cmd in ("quit", "exit"):
            print("  Bye!")
            break
        elif cmd == "add":
            if not arg1:
                print("  Usage: add <task title>")
            else:
                title = arg1 + (" " + arg2 if arg2 else "")
                add_task(tasks, title)
        elif cmd == "advance":
            if not arg1.isdigit():
                print("  Usage: advance <id>")
            else:
                advance_task(tasks, int(arg1))
        elif cmd == "comment":
            if not arg1.isdigit() or not arg2:
                print("  Usage: comment <id> <text>")
            else:
                comment_task(tasks, int(arg1), arg2)
        elif cmd == "list":
            list_tasks(tasks)
        elif cmd == "yts":
            list_tasks(tasks, filter_status="Yet to Start")
        elif cmd == "pending":
            list_tasks(tasks, filter_status="Pending")
        elif cmd == "done":
            if arg1.isdigit():
                print("  To complete a task use: advance <id>")
            else:
                list_tasks(tasks, filter_status="Done")
        elif cmd == "delete":
            if not arg1.isdigit():
                print("  Usage: delete <id>")
            else:
                delete_task(tasks, int(arg1))
        elif cmd == "clear":
            clear_done(tasks)
        elif cmd == "help":
            print_help()
        else:
            print(f"  Unknown command '{cmd}'. Type 'help' for commands.")


if __name__ == "__main__":
    main()
