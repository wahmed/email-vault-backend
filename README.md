# Remove all containers:
docker rm $(docker ps -aq)  

# Remove all images:
docker rmi $(docker images -q)   

# kil port
$ sudo lsof -i :5672
$ sudo lsof -i :15672
$ sudo kill <PID>

# If the process is a service, you might want to stop it with a command 
$ sudo systemctl stop <service_name>
$ docker rm <servic name>

# run docker image of flask project:
sudo docker build -t mail -f my_flask/Dockerfile .
sudo docker run -d -p 5000:5000 mail

# Pull the RabbitMQ Docker Image:
sudo docker pull rabbitmq:3-management

# run rebitMQ docker:
sudo docker run -d --hostname my-rabbit --name some-rabbit -p 5672:5672 -p 15672:15672 rabbitmq:3-management

# to confirm docker is working or not
sudo docker ps -a 

# If you want to add your current user
$ sudo usermod -aG docker $USER

# restart docker 
$ sudo systemctl restart docker
