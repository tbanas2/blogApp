import os

from flask import Flask



def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # a simple page that says hello
    @app.route('/hello')
    def hello():
        return 'Hello, World, yeah!'

    #we're within context of our factory function so we finally have an instance of our app - let's use these setters for our app
    #to tell it what to do with DB connection when 1) cleaning up a resonse and 2) adding a new command for the app we call from cmd line which calls our function to build the DB from schema
    from . import db
    db.init_app(app)

    #more registration - this time, let's register that authorization blueprint we created
    from . import auth
    from . import blog
    
    app.register_blueprint(auth.bp)
    app.register_blueprint(blog.bp)
    app.add_url_rule('/', endpoint='index')

    return app