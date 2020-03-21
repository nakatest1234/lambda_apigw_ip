# lambda_apigw_ip

- python3.8
- AWS apigateway -> AWS lambda -> Security Group

## local

```
docker run --rm --env-file .env -v ${PWD}:/var/task:ro lambci/lambda:python3.8 test.lambda_handler $(printf '%s' $(cat in.json))
```

## lambda env

| name | example |
| ---- | ------- |
| SECURITY_GROUP_ID | sg-xxxxxxxxx |
| ALLOW_NAMES | judgment Descriotion ex)naka-test1 |
| ALLOW_PORTS | protocol:port ex)tcp:80, tcp:0 |

## ref

- https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ec2.html#securitygroup
