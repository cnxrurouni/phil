1. Install Docker Desktop: https://www.docker.com/products/docker-desktop/

2. Git pull latest code and run the command:
```docker-compose -f docker-compose.yaml -p test up --build```

This will build the images to run postgres and ubuntu, then bring
up two services named db and ubuntu. 

3. On Docker Desktop, click the ubuntu service and under exec tab, run this command:
```source sqlAlchemy/bin/activate; python3 create_database.py```

[docker pic.pdf](https://github.com/user-attachments/files/16950079/docker.pic.pdf)

# To install material ui v5 compatible with react v18
npm install @mui/material @emotion/react @emotion/styled