FROM nginx:1.27.0-alpine

COPY crtf/aennaki_me.crt /etc/ssl/aennaki_me/
COPY crtf/aennaki_me.key /etc/ssl/aennaki_me/
COPY crtf/aennaki_me.ca-bundle /etc/ssl/aennaki_me/

COPY nginx.conf /etc/nginx/conf.d/

EXPOSE 80
EXPOSE 443

ENTRYPOINT ["nginx"]

CMD ["-g", "daemon off;"]