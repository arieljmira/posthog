from posthog.cdp.templates.hog_function_template import HogFunctionTemplate


template: HogFunctionTemplate = HogFunctionTemplate(
    status="alpha",
    id="template-Intercom",
    name="Send data to Intercom",
    description="Send events and contact information to Intercom",
    icon_url="/static/services/intercom.png",
    hog="""
let accessToken := inputs.access_token
let host := inputs.host
let email := inputs.email

if (empty(email)) {
    print('`email` input is empty. Skipping.')
    return
}

let body := {
    'event_name': event.name,
    'created_at': toInt(toUnixTimestamp(toDateTime(event.timestamp))),
    'email': inputs.email,
    'id': event.distinct_id,
}

let headers := {
    'Authorization': f'Bearer {accessToken}',
    'Content-Type': 'application/json',
    'Accept': 'application/json'
}

let res := fetch(f'https://{host}/events', {
  'method': 'POST',
  'headers': headers,
  'body': body
})

if (res.status >= 200 and res.status < 300) {
    print('Event sent successfully!')
    return
}

if (res.status == 404) {
    print('No existing contact found for email')
    return
}

print('Error sending event:', res.status, res.body)

""".strip(),
    inputs_schema=[
        {
            "key": "access_token",
            "type": "string",
            "label": "Intercom access token",
            "description": "Create an Intercom app (https://developers.intercom.com/docs/build-an-integration/learn-more/authentication), then go to Configure > Authentication to find your token.",
            "secret": True,
            "required": True,
        },
        {
            "key": "host",
            "type": "choice",
            "choices": [
                {
                    "label": "US (api.intercom.io)",
                    "value": "api.intercom.io",
                },
                {
                    "label": "EU (api.eu.intercom.com)",
                    "value": "api.eu.intercom.com",
                },
            ],
            "label": "Data region",
            "description": "Use the EU variant if your Intercom account is based in the EU region",
            "default": "api.intercom.io",
            "secret": False,
            "required": True,
        },
        {
            "key": "email",
            "type": "string",
            "label": "Email of the user",
            "description": "Where to find the email for the contact to be created. You can use the filters section to filter out unwanted emails or internal users.",
            "default": "{person.properties.email}",
            "secret": False,
            "required": True,
        },
    ],
    filters={
        "events": [{"id": "$identify", "name": "$identify", "type": "events", "order": 0}],
        "actions": [],
        "filter_test_accounts": True,
    },
)
