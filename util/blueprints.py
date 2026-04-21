import routes


def register_blueprint(app):
    app.register_blueprint(routes.auth)
    app.register_blueprint(routes.users)
    app.register_blueprint(routes.temples)
    app.register_blueprint(routes.masters)
    app.register_blueprint(routes.padawans)
    app.register_blueprint(routes.species)
    app.register_blueprint(routes.lightsabers)
    app.register_blueprint(routes.crystals)
    app.register_blueprint(routes.courses)
    app.register_blueprint(routes.enrollments)
