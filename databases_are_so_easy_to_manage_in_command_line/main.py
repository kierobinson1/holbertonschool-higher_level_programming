from sys import argv
from models import *

def create_tables():
    my_models_db.connect()
    my_models_db.create_tables([School, Batch, User, Student])

def print_table():
    '''the second argument of your program should be the model name in lowercase'''
    '''your program should fetch from the DB all models depending of the value of'''
    '''the second argument and print the list one object by line'''
    if len(argv) == 3:
        if argv[2] == "school":
            rows = School.select()
            for row in rows:
                print row
        elif argv[2] == "batch":
            rows = Batch.select()
            for row in rows:
                print row
        elif argv[2] == "user":
            rows = User.select()
            for row in rows:
                print row
        elif argv[2] == "student":
            rows = Student.select()
            for row in rows:
                print row

def insert_record():
    try:
        with my_models_db.transaction():
            if argv[2] == "school":
                new = School.create(
                    name=argv[3]
                )
                print "New school: " + str(new)
            elif argv[2] == "batch":
                new = Batch.create(
                    school=argv[3],
                    name=argv[4],
                )
                print "New batch: " + str(new)
            elif argv[2] == "student":
                if len(argv) == 7:
                    new = Student.create(
                        batch=int(argv[3]),
                        age=int(argv[4]),
                        last_name=argv[5],
                        first_name=argv[6],
                    )
                else:
                    new = Student.create(
                        batch=int(argv[3]),
                        age=int(argv[4]),
                        last_name=argv[5],
                    )
                print "New student: " + str(new)
    except peewee.IntegrityError:
        flash('That username is already taken')

def delete_tables():
    # the second argument of your program should be the model name in lowercase
    # the third arguments should be the id of the object to delete
    # if in your database you don't have any object with this id, your program should print Nothing to delete
    # otherwise, the object will be deleted and your program should print Delete: <object to delete>
    if argv[2] == "school":
        query = School.select().where(Schools.id == argv[3])
        if query.exists():
            target = query.get()
            School.delete().where(School.id == argv[3]).execute()
            print "Delete: " + str(target)
        else:
            print "Nothing to delete"
    elif argv[2] == "batch":
        query = Batch.select().where(Batch.id == argv[3])
        if query.exists():
            target = query.get()
            Batch.delete().where(Batch.id == argv[3]).execute()
            print "Delete: " + str(target)
        else:
            print "Nothing to delete"
    elif argv[2] == "student":
        query = Student.select().where(Student.id == argv[3])
        if query.exists():
            target = query.get()
            Student.delete().where(Student.id == argv[3]).execute()
            print "Delete: " + str(target)
        else:
            print "Nothing to delete"

''' Prints the action or prints error '''
if len(argv) < 2:
    print "Please enter an action"
elif argv[1] == "create":
    create_tables()
    print "create"
elif argv[1] == "print":
    print_table()
elif argv[1] == "insert":
    insert_record()
elif argv[1] == "delete":
    delete_tables()
else:
    print "Undefined action " + argv[1]