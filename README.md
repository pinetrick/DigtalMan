Easy start:
docker run -it \
  --name people \
  --restart=always \
  --gpus '"device=0"' \
  -p 8383:8383 \
  pinetrick/people:v1 \
  /bin/bash -c "python /code/app_local.py & exec bash"




Usage: 
<img width="1195" height="452" alt="image" src="https://github.com/user-attachments/assets/442050fc-02c1-42c1-8c6a-2bcae295f9cb" />
<img width="1215" height="399" alt="image" src="https://github.com/user-attachments/assets/4257cdc3-e48b-41b6-828a-99cb3e34e0d5" />
