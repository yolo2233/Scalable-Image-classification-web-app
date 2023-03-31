# base image 
FROM tiangolo/uvicorn-gunicorn-fastapi:python3.9  

WORKDIR /code 

COPY ./requirements.txt /code/requirements.txt

# 在容器内当前的工作路径为 之后所有我们的代码, 都会被copy到这个/code的目录之前
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt 

# copy ./app指的是app下文件夹所有的内容，而不是app这个文件夹
COPY ./app /code/app

# copy 完成之后，directory structure应该如下：
# Dockerfile只是用来创建新的image，以及当我们docker run的时候执行什么命令

# CMD takes a list of strings, each of these strings is what you would type in the command line separated by spaces.
# This command will be run from the current working directory, the same /code directory you set above with WORKDIR /code.

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]
