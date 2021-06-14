from werkzeug import run_simple
from werkzeug.middleware.dispatcher import DispatcherMiddleware

from master.views import app
from movies.views import movies_blueprint
from user.views import user_blueprint

app.register_blueprint(movies_blueprint)
app.register_blueprint(user_blueprint)

application = DispatcherMiddleware(None, {
    '/api': app
})


if __name__ == '__main__':
    run_simple('0.0.0.0', 8000, application, use_debugger=False, use_reloader=True, threaded=True)

