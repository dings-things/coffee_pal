import endpoints


HOME_OPENED = lambda reservation_blocks=None: {
    "type": "home",
    "blocks": [
        {
            "type": "header",
            "text": {"type": "plain_text", "text": ":coffee-pal: CoffeePal"},
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "*커피팔과 함께 동료들과의 네트워킹을 쉽고 재미있게 만들어 보세요*\n\n잠깐의 커피타임을 통해 팀원들과 더 가까워지고, 새로운 인사이트를 얻어 보세요",
            },
        },
        {"type": "divider"},
        {
            "type": "header",
            "text": {"type": "plain_text", "text": ":coffee-meow: 커피챗 제안하기"},
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "특정 동료에게 직접 커피챗을 제안해보세요.\n더 깊은 대화나 특정 주제에 대해 이야기할 기회를 가질 수 있습니다.",
            },
            "accessory": {
                "type": "button",
                "text": {"type": "plain_text", "text": "제안하기"},
                "style": "primary",
                "value": "suggest_coffee_chat",
                "action_id": endpoints.SUGGEST_COFFEE_CHAT_BUTTON,
            },
        },
        {
            "type": "header",
            "text": {"type": "plain_text", "text": ":game_die: 랜덤 커피챗 제안하기"},
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "버튼을 누르면 랜덤으로 팀원 한 명과의 커피챗이 제안됩니다.\n선택 장애가 있는 그대에게 완벽한 선택입니다!",
            },
            "accessory": {
                "type": "button",
                "text": {"type": "plain_text", "text": "제안하기"},
                "style": "primary",
                "value": "random_coffee_chat",
                "action_id": endpoints.RANDOM_COFFEE_CHAT_BUTTON,
            },
        },
        {
            "type": "header",
            "text": {"type": "plain_text", "text": ":ablobcheer: 그룹 커피챗 등록하기"},
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "채널 중 한 곳을 선택하고, 커피챗을 등록해보세요.\n채널 인원 중 일부를 제외하고 신청할 수 있어요 :blob-secret:",
            },
            "accessory": {
                "type": "button",
                "text": {"type": "plain_text", "text": "제안하기"},
                "style": "primary",
                "value": "register_details",
                "action_id": endpoints.GROUP_COFFEE_CHAT_BUTTON,
            },
        },
        {"type": "divider"},
        {
            "type": "header",
            "text": {"type": "plain_text", "text": ":calendar: 나의 커피챗 일정"},
        },
    ]
    + (
        reservation_blocks
        if reservation_blocks
        else [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "현재 예약된 커피챗 일정이 없습니다.",
                },
            }
        ]
    ),
}

MESSAGE_DETAIL = lambda target, date, message: {
    "type": "modal",
    "callback_id": "message_view",
    "title": {"type": "plain_text", "text": "메시지 보기"},
    "blocks": [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*예약자*:\n<@{target}>",
            },
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*일시*:\n{date.strftime('%Y년 %m월 %d일 %H시 %M분')}",
            },
        },
        message,
    ],
}
