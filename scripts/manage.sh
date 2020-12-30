# Runs Django's manage.py command within the web container
# Passes any arguments

docker exec -it hines_web pipenv run python manage.py "$@"