# Commands for generating keys for Authentication:

```shell
openssl genrsa -out jwt-private.pem 2048
```

```shell
openssl rsa -in jwt-private.pem -outform PEM -pubout -out jwt-public.pem
``` 