# tutorial: https://medium.com/google-cloud/how-to-run-a-static-site-on-google-cloud-run-345713ca4b40
# Use a nginx Docker image
FROM nginx

# Copy the static dbt docs HTMLs to the nginx directory
# target directory created using the command `dbt docs generate`
COPY ./target/ /usr/share/nginx/html

# Copy the nginx configuration template to the nginx config directory
COPY ./docs_website/default.template /etc/nginx/conf.d/default.template

# Substitute the environment variables and generate the final config
CMD envsubst < /etc/nginx/conf.d/default.template > /etc/nginx/conf.d/default.conf && exec nginx -g 'daemon off;'