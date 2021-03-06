from threading import Thread, Semaphore
from peewee import *
from h_swapi_models import *
import requests
import json

''' Sets global variable for the database '''
db = SqliteDatabase(None)

''' Defines URL Class to initialize the requests '''
class URLData(Thread):
    active_threads = 0
    active_processes = 0
    type_list = ['films', 'people', 'planets']

    def __init__(self, url):
        ''' Initializes the class and stores the url '''
        Thread.__init__(self)
        self.__url = url

    def run(self):
        ''' Defines the thread process that must complete '''
        global db
        URLData.active_threads += 1
        try:
            ''' Attempts the requests and loads the returned data'''
            url_type = self.__url.split('/')[4]
            if not url_type in URLData.type_list:
                print("URL is not supported.")
            elif SWAPI.stop_threads == True:
                URLData.active_threads -= 1
                return
            req = requests.get(self.__url)
            if req.status_code != 200:
                print("Error " + str(req.status_code) + ": Request for " + self.__url + " was unsuccessful")
            else:
                data = json.loads(req.text)
                next_url = data['next']
                if next_url:
                    next = URLData(next_url)
                    next.start()
                results = data['results']
            for result in results:
                self.process_result(url_type, result)
        finally:
            URLData.active_threads -= 1

    def process_result(self, url_type, result):
        ''' Prepares returned data to be stored in the database '''
        URLData.active_processes += 1
        result_id = int(result['url'].split('/')[-2])
        if SWAPI.stop_threads == True:
            URLData.active_processes -= 1
            return
        db.connect()
        try:
            if url_type == 'films':
                new = FilmModel.create(id=result_id,
                                title=result['title'],
                                release_date=result['release_date'],
                                episode_id=int(result['episode_id']))
            elif url_type == 'people':
                films_list = []
                for film in result['films']:
                    film = int(film.split('/')[-2])
                    films_list.append(film)
                new = PeopleModel.create(id=result_id,
                                         name=result['name'])
                if len(films_list) > 0:
                    new.films = films_list
            elif url_type == 'planets':
                residents_list = []
                films_list = []
                for resident in result['residents']:
                    resident = int(resident.split('/')[-2])
                    residents_list.append(resident)
                for film in result['films']:
                    film = int(film.split('/')[-2])
                    films_list.append(film)
                new = PlanetModel.create(id=result_id,
                                         name= result['name'],
                                         climate= result['climate'])
                if len(residents_list) > 0:
                    new.residents= residents_list
                    new.save()
                if len(films_list) > 0:
                    new.films= films_list
                    new.save()
        finally:
            db.close()
            URLData.active_processes -= 1


class SWAPI(Thread):
    ''' Manages the threads for obtaining the Star Wars API '''
    stop_threads = False
    groups_initialized = False

    def __init__(self, database_name):
        ''' Initializes the class and builds the database tables '''
        Thread.__init__(self)
        global db
        db = SqliteDatabase(database_name, pragmas=(
                            ('foreign_keys', 1),
                         ))
        models = [FilmModel, PeopleModel, PlanetModel,
                  PeopleModel.films.get_through_model(),
                  PlanetModel.films.get_through_model(),
                  PlanetModel.residents.get_through_model()]

        for model in models:
            model._meta.database = db
            if not model.table_exists():
                db.create_tables([model])

    def run(self):
        ''' Triggers the threads for each section of data '''
        films_url = 'http://swapi.co/api/films/'
        people_url = 'http://swapi.co/api/people/'
        planets_url = 'http://swapi.co/api/planets/'
        if SWAPI.stop_threads == True:
            SWAPI.groups_initialized = True
            return
        films = URLData(films_url)
        films.start()
        films.join()
        while URLData.active_threads > 0 or URLData.active_processes > 0:
            pass
        if SWAPI.stop_threads == True:
            SWAPI.groups_initialized = True
            return
        people = URLData(people_url)
        people.start()
        people.join()
        while URLData.active_threads > 0 or URLData.active_processes > 0:
            pass
        if SWAPI.stop_threads == True:
            SWAPI.groups_initialized = True
            return
        planets = URLData(planets_url)
        planets.start()
        planets.join()
        SWAPI.groups_initialized = True

    def is_done(self):
        ''' Returns true if all threads are complete '''
        if SWAPI.groups_initialized == True and URLData.active_threads == 0 and URLData.active_processes == 0:
            return True
        elif SWAPI.stop_threads == True:
            return True
        return False

    def stop(self):
        ''' Triggers a stop of all threads and processes '''
        SWAPI.stop_threads == True
        SWAPI.groups_initialized == True
