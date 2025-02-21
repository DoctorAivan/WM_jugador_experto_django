#!/bin/sh

docker exec -it $1 $2
# ./cmd_docker.sh server-backend "python manage.py makemigrations"
# ./cmd_docker.sh server-backend "python manage.py migrate"
# ./cmd_docker.sh server-backend "python manage.py remove_data"
# ./cmd_docker.sh server-backend "python manage.py get_json_players"
# ./cmd_docker.sh server-backend "python manage.py shell"
# ./cmd_docker.sh server-redis "cat /proc/sys/vm/overcommit_memory"

# ./cmd_docker.sh server-backend "python manage.py shell"