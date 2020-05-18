FROM mysql:8.0.20
ENV MYSQL_DATABASE user_statistics
ENV MYSQL_ROOT_PASSWORD secret
COPY create_db.sql /docker-entrypoint-initdb.d/