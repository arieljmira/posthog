from posthog.cdp.templates.hog_function_template import HogFunctionTemplate


template: HogFunctionTemplate = HogFunctionTemplate(
    status="beta",
    id="template-aws-kinesis",
    name="AWS Kinesis",
    description="Put data to an AWS Kinesis stream",
    # icon_url="/api/projects/@current/hog_functions/icon/?id=posthog.com&temp=true",
    hog="""
fn uploadToKinesis(data) {
  let region := inputs.aws_region
  let endpoint := f'https://kinesis.{region}.amazonaws.com'
  let service := 'kinesis'
  let amzDate := formatDateTime(now(), '%Y%m%dT%H%i%sZ')
  let date := formatDateTime(now(), '%Y%m%d')

  let payload := jsonStringify({
    'StreamName': inputs.aws_kinesis_stream_arn,
    'PartitionKey': inputs.aws_kinesis_partition_key,
    'Data': base64Encode(data),
  })

  let requestHeaders := {
    'Content-Type': 'application/x-amz-json-1.1',
    'X-Amz-Target': 'Kinesis_20131202.PutRecord',
    'X-Amz-Date': amzDate,
    'Host': f'kinesis.{region}.amazonaws.com',
  }

  let canonicalHeaderParts := []
  for (let key, value in requestHeaders) {
    let val := replaceAll(trim(value), '\\\\s+', ' ')
    canonicalHeaderParts := arrayPushBack(canonicalHeaderParts, f'{lower(key)}:{val}')
  }
  let canonicalHeaders := arrayStringConcat(arraySort(canonicalHeaderParts), '\\n') || '\\n'

  let signedHeaderParts := []
  for (let key, value in requestHeaders) {
    signedHeaderParts := arrayPushBack(signedHeaderParts, lower(key))
  }
  let signedHeaders := arrayStringConcat(arraySort(signedHeaderParts), ';')

  let canonicalRequest := arrayStringConcat([
    'POST',
    '/',
    '',
    canonicalHeaders,
    signedHeaders,
    sha256Hex(payload),
  ], '\\n')

  let credentialScope := f'{date}/{region}/{service}/aws4_request'
  let stringToSign := arrayStringConcat([
    'AWS4-HMAC-SHA256',
    amzDate,
    credentialScope,
    sha256Hex(canonicalRequest),
  ], '\\n')

  let signature := sha256HmacChainHex([
    f'AWS4{inputs.aws_secret_access_key}', date, region, service, 'aws4_request', stringToSign
  ])

  let authorizationHeader :=
      f'AWS4-HMAC-SHA256 Credential={inputs.aws_access_key_id}/{credentialScope}, ' ||
      f'SignedHeaders={signedHeaders}, ' ||
      f'Signature={signature}'

  requestHeaders['Authorization'] := authorizationHeader

  let res := fetch(endpoint, {
    'headers': requestHeaders,
    'body': payload,
    'method': 'POST'
  })

  if (res.status >= 200 and res.status < 300) {
    print('Event sent successfully!')
    return
  }

  print('Error sending event:', res.status, res.body)
}

uploadToKinesis(jsonStringify(inputs.payload))
""".strip(),
    inputs_schema=[
        {
            "key": "aws_access_key_id",
            "type": "string",
            "label": "AWS Access Key ID",
            "secret": True,
            "required": True,
        },
        {
            "key": "aws_secret_access_key",
            "type": "string",
            "label": "AWS Secret Access Key",
            "secret": True,
            "required": True,
        },
        {
            "key": "aws_region",
            "type": "string",
            "label": "AWS Region",
            "secret": False,
            "required": True,
            "default": "us-east-1",
        },
        {
            "key": "aws_kinesis_stream_arn",
            "type": "string",
            "label": "Kinesis Stream ARN",
            "secret": False,
            "required": True,
        },
        {
            "key": "aws_kinesis_partition_key",
            "type": "string",
            "label": "Kinesis Partition Key",
            "secret": False,
            "required": False,
        },
        {
            "key": "payload",
            "type": "json",
            "label": "Message Payload",
            "default": {"event": "{event}", "person": "{person}"},
            "secret": False,
            "required": False,
        },
    ],
)
