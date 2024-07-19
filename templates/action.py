import json


SUGGEST_COFFEE_CHAT_MODAL = {
    "type": "modal",
    "callback_id": "suggest_coffee_chat_modal",
    "title": {
        "type": "plain_text",
        "text": "커피챗 제안하기 :coffee-meow:",
    },
    "blocks": [
        {
            "type": "input",
            "block_id": "user_select",
            "label": {
                "type": "plain_text",
                "text": "누구와 커피챗을 하고 싶으신가요?",
            },
            "element": {
                "type": "users_select",
                "action_id": "user",
                "placeholder": {
                    "type": "plain_text",
                    "text": "사우 선택하기",
                },
            },
        },
        {
            "type": "input",
            "block_id": "pick_datetime",
            "label": {"type": "plain_text", "text": "날짜 선택"},
            "element": {
                "type": "datetimepicker",
                "action_id": "datetimepicker-action",
            },
            "hint": {
                "type": "plain_text",
                "text": "날짜를 선택하세요",
            },
        },
        {
            "type": "input",
            "block_id": "message_input",
            "label": {
                "type": "plain_text",
                "text": "어떤 이야기를 나누고 싶은지 미리 간단히 남겨주세요",
            },
            "element": {
                "type": "rich_text_input",
                "action_id": "rich_text_input-action",
                "placeholder": {
                    "type": "plain_text",
                    "text": "예: OO님, 그동안 바쁘셔서 업무 이야기만 하고 서로 대화 나누는 시간이 부족했던 것 같아요. 제가 잘하고 있는 점 또는 좀 더 신경썼으면 좋겠다고 생각하는 부분이 있다면 편하게 이야기 나누고 싶어 커피챗 요청드려요!",
                },
            },
        },
    ],
    "submit": {"type": "plain_text", "text": "제안하기"},
}


SELECT_RANDOM_COFFEE_CHAT_MODAL = lambda init_member, private_metadata: {
    "type": "modal",
    "callback_id": "suggest_random_coffee_chat_modal",
    "title": {"type": "plain_text", "text": "랜덤 커피챗"},
    "submit": {"type": "plain_text", "text": "제안하기"},
    "private_metadata": private_metadata,
    "blocks": [
        {
            "type": "input",
            "block_id": "selected_member",
            "label": {"type": "plain_text", "text": "랜덤 추첨된 사우"},
            "element": {
                "type": "users_select",
                "action_id": "user",
                "initial_user": init_member,
            },
        },
        {
            "type": "actions",
            "block_id": "roll_action",
            "elements": [
                {
                    "type": "button",
                    "action_id": "roll_button",
                    "text": {
                        "type": "plain_text",
                        "text": ":game_die: 다시 랜덤 추첨하기",
                        "emoji": True,
                    },
                },
            ],
        },
        {
            "type": "input",
            "block_id": "pick_datetime",
            "label": {"type": "plain_text", "text": "날짜 선택"},
            "element": {
                "type": "datetimepicker",
                "action_id": "datetimepicker-action",
            },
            "hint": {
                "type": "plain_text",
                "text": "시간은 직접 입력 가능합니다 (ex. 17:30)",
            },
        },
        {"type": "divider"},
        {
            "type": "input",
            "block_id": "message_input",
            "label": {
                "type": "plain_text",
                "text": "어떤 이야기를 나누고 싶은지 미리 간단히 남겨주세요",
            },
            "element": {
                "type": "rich_text_input",
                "action_id": "rich_text_input-action",
                "placeholder": {
                    "type": "plain_text",
                    "text": "예: OO님, 그동안 바쁘셔서 업무 이야기만 하고 서로 대화 나누는 시간이 부족했던 것 같아요. 제가 잘하고 있는 점 또는 좀 더 신경썼으면 좋겠다고 생각하는 부분이 있다면 편하게 이야기 나누고 싶어 커피챗 요청드려요!",
                },
            },
        },
    ],
}


SELECT_CHANNEL_MODAL = {
    "type": "modal",
    "callback_id": "select_random_coffee_chat_modal",
    "title": {"type": "plain_text", "text": "채널을 선택해주세요!"},
    "blocks": [
        {
            "type": "input",
            "block_id": "channel_select",
            "label": {"type": "plain_text", "text": "채널 선택"},
            "element": {
                "type": "channels_select",
                "action_id": "channel",
            },
        }
    ],
    "submit": {"type": "plain_text", "text": "다음"},
}


SEND_SUGGESTION_BLOCK = lambda sender_user, message_blocks, selected_date: [
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
                "action_id": "coffee_chat_complete",
                "value": json.dumps(
                    {"selected_date": selected_date, "sender_user": sender_user}
                ),
            }
        ],
    },
]

COMPLETION_BLOCK = lambda receiver_user, selected_date: [
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
                "text": f"*대상*\n<@{receiver_user}>",
            },
            {
                "type": "mrkdwn",
                "text": f"*일정*\n{selected_date}",
            },
        ],
    },
]
