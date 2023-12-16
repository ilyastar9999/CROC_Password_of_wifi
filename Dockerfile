# Используем официальный образ Python в качестве базового образа
FROM python:3.10
# Устанавливаем рабочую директорию внутри контейнера
WORKDIR /app
# Копируем файл requirements.txt внутрь контейнера
COPY requirements.txt ./
#RUN pip install --upgrade setuptools
# Устанавливаем зависимости, описанные в файле requirements.txt
#RUN python -m ensurepip --upgrade
RUN apt-get update && \
    apt-get install -y locales && \
    sed -i -e 's/# ru_RU.UTF-8 UTF-8/ru_RU.UTF-8 UTF-8/' /etc/locale.gen && \
    dpkg-reconfigure --frontend=noninteractive locales
ENV LANG ru_RU.UTF-8
ENV LC_ALL ru_RU.UTF-8
RUN pip install -r requirements.txt
CMD ["python3", "main.py"]
