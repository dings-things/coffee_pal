import json

import endpoints

RESERVATION_BLOCK = lambda reservations: [
    {
        "type": "section",
        "fields": [
            {"type": "mrkdwn", "text": f"*예약자*:\n<@{reservation.target_id}>"},
            {
                "type": "mrkdwn",
                "text": f"*일시*:\n{reservation.date.strftime('%Y년 %m월 %d일 %H시 %M분')}",
            },
        ],
        "accessory": {
            "type": "button",
            "text": {"type": "plain_text", "text": "메시지 보기"},
            "value": reservation.uuid,
            "action_id": "view_message_button",
        },
    }
    for reservation in reservations
]

SEND_SUGGESTION = lambda sender_user, message_blocks, selected_date: [
    {
        "type": "header",
        "text": {
            "type": "plain_text",
            "text": f":coffee-meow: 커피챗 제안이 왔어요! :coffee-meow:",
        },
    },
    {
        "type": "section",
        "text": {
            "text": "동료와 함께 커피 한 잔 어떠세요? :coffee:",
            "type": "mrkdwn",
        },
        "fields": [
            {
                "type": "mrkdwn",
                "text": f"*신청한 사우*\n<@{sender_user}>",
            },
            {
                "type": "mrkdwn",
                "text": f"*일정*\n{selected_date}",
            },
        ],
    },
    {"type": "divider"},
    message_blocks,
    {
        "type": "actions",
        "elements": [
            {
                "type": "button",
                "text": {"type": "plain_text", "text": "커피챗 일정 수락하기"},
                "action_id": endpoints.COFFEE_CHAT_COMPLETE,
                "value": json.dumps(
                    {"selected_date": selected_date, "sender_user": sender_user}
                ),
            }
        ],
    },
    {
        "type": "divider",
    },
]

SEND_CONFIRMATION = lambda sender_user, selected_date: [
    {
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": ":white_check_mark: 커피챗 일정이 수락되었어요! :white_check_mark:",
        },
        "fields": [
            {
                "type": "mrkdwn",
                "text": f"*함께할 사우*\n<@{sender_user}>",
            },
            {
                "type": "mrkdwn",
                "text": f"*일정*\n{selected_date}",
            },
        ],
    },
    {
        "type": "divider",
    },
]

COMPLETION = lambda receiver_user, selected_date: [
    {
        "type": "header",
        "text": {
            "type": "plain_text",
            "text": ":blanket_coffee: 상대방이 커피챗 일정을 수락했어요 :blanket_coffee:",
        },
    },
    {
        "type": "section",
        "text": {
            "text": "행복한 커피 타임 보내세요! :coffee-beans:",
            "type": "mrkdwn",
        },
        "fields": [
            {
                "type": "mrkdwn",
                "text": f"*함께할 사우*\n<@{receiver_user}>",
            },
            {
                "type": "mrkdwn",
                "text": f"*일정*\n{selected_date}",
            },
        ],
    },
    {
        "type": "divider",
    },
]
