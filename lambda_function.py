import boto3
import os
import sys

SECURITY_GROUP_ID = os.environ.get('SECURITY_GROUP_ID', '')
ALLOW_NAMES       = [x.strip() for x in os.environ.get('ALLOW_NAMES', '').split(',') if not x.strip() == '']
ALLOW_PORTS       = [x.strip() for x in os.environ.get('ALLOW_PORTS', '').split(',') if not x.strip() == '']

def lambda_handler(event, context):
	# parameter check
	username = event.get('queryStringParameters', {}).get('name')
	ip_addr  = event.get('requestContext', {}).get('http', {}).get('sourceIp')
	if username is None or ip_addr is None:
		return {
			'isBase64Encoded': False,
			'statusCode': 503,
			'headers': {},
			'body': 'no param',
		}

	if username not in ALLOW_NAMES:
		return {
			'isBase64Encoded': False,
			'statusCode': 503,
			'headers': {},
			'body': 'no user',
		}

	ec2 = boto3.resource('ec2', region_name=os.environ.get('REGION_NAME', 'ap-northeast-1'))

	security_group = ec2.SecurityGroup(SECURITY_GROUP_ID)

	if not getattr(security_group, 'ip_permissions'):
		return {
			'isBase64Encoded': False,
			'statusCode': 503,
			'headers': {},
			'body': 'no role',
		}

	target_list = security_group.ip_permissions

	if len(target_list)==0:
		return {
			'isBase64Encoded': False,
			'statusCode': 503,
			'headers': {},
			'body': 'no target',
		}

	authorize_IpPermissions = []
	revoke_IpPermissions    = []

	for port_data in ALLOW_PORTS:
		protocol, port_raw  = port_data.split(':', 2)
		port = int(port_raw)

		authorize_IpPermissions.append({
			'FromPort': port,
			'ToPort': port,
			'IpProtocol': protocol,
			'IpRanges': [{
				'CidrIp': '{}/32'.format(ip_addr),
				'Description': username,
			}],
		})

		for target in target_list:
			if 'FromPort' in target and target['FromPort']==port:
				IpRanges = []
				# キーチェック省略
				for rule in target['IpRanges']:
					if rule['Description'] == username:
						IpRanges.append(rule)

				if len(IpRanges):
						revoke_IpPermissions.append({
							'FromPort': port,
							'ToPort': port,
							'IpProtocol': target['IpProtocol'],
							'IpRanges': IpRanges,
						})

	try:
		if len(revoke_IpPermissions):
			print('revoke')
			ret = security_group.revoke_ingress(**{'IpPermissions':revoke_IpPermissions})
	except Exception as e:
		print('Exception:', e.args, file=sys.stderr)
	except:
		print('Unexpected error:', sys.exc_info()[0], file=sys.stderr)

	try:
		if len(authorize_IpPermissions):
			print('authorize')
			ret = security_group.authorize_ingress(**{'IpPermissions':authorize_IpPermissions})
			print(ret)

			return {
				'isBase64Encoded': False,
				'statusCode': 200,
				'headers': {},
				'body': 'OK',
			}
	except Exception as e:
		print('Exception:', e.args, file=sys.stderr)
		errmsg = e.response
	except:
		print('Unexpected error:', sys.exc_info()[0], file=sys.stderr)
		errmsg = 'Unexpected error'

	return {
		'isBase64Encoded': False,
		'statusCode': 503,
		'headers': {},
		'body': errmsg,
	}
