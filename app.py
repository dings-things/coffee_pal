from datetime import datetime, timezone, timedelta
import json
import random
from typing import Union, Pattern, Dict, Optional, Sequence
from slack_bolt import App
from slack_sdk import WebClient
from slack_sdk.web import SlackResponse
from slack_bolt.adapter.socket_mode import SocketModeHandler
from slack_bolt.context.respond.async_respond import AsyncRespond
from slack_sdk.errors import SlackApiError
import logging
import templates.event, templates.action

logging.basicConfig(level=logging.INFO)
from config import settings
import asyncio

app = App(token=settings.SLACK_BOT_TOKEN)
logger = logging.getLogger(__name__)


###################################################### EVENT ######################################################
## EVENT : 1. 앱 홈 화면 View
@app.event("app_home_opened")
def handle_app_home_opened(
    event: Union[
        str,
        Pattern,
        Dict[str, Optional[Union[str, Sequence[Optional[Union[str, Pattern]]]]]],
    ],
    client: WebClient = None,
) -> SlackResponse:
    user_id = event["user"]
    # App Home 업데이트 로직
    return client.views_publish(
        user_id=user_id,  # App Home을 업데이트할 사용자 ID
        view=templates.event.HOME_OPENED,
    )


###################################################### VIEW ######################################################
## VIEW : 1. 커피챗 제안 모달
@app.view("suggest_coffee_chat_modal")
def handle_modal_submission(ack, body, client: WebClient = None):
    ack()
    try:
        # 제출된 데이터 처리 로직
        selected_user = body["view"]["state"]["values"]["user_select"]["user"][
            "selected_user"
        ]
        message_blocks = body["view"]["state"]["values"]["message_input"][
            "rich_text_input-action"
        ]["rich_text_value"]
        selected_datetime = __convert_unix_to_kst(
            body["view"]["state"]["values"]["pick_datetime"]["datetimepicker-action"][
                "selected_date_time"
            ]
        )
        sender_user = body["user"]["id"]  # 제출한 사용자의 ID

        # 메시지 내용 구성
        blocks = templates.action.SEND_SUGGESTION_BLOCK(
            sender_user, message_blocks, selected_datetime
        )

        # 선택된 유저에게 DM 보내기
        response = client.chat_postMessage(
            channel=selected_user, blocks=blocks, text="커피챗 제안이 왔어요!"
        )

        print("CHECK HERE")
        print(response)

    except SlackApiError as e:
        logger.info(f"Error handling modal submission: {e}")


## VIEW : 2. 랜덤 커피챗 선택 모달
@app.view("select_random_coffee_chat_modal")
def handle_select_random_coffee_chat_modal_submission(
    ack, body, client: WebClient = None
):
    ack()
    try:
        channel_id = body["view"]["state"]["values"]["channel_select"]["channel"][
            "selected_channel"
        ]
        members = _get_all_channel_members(client, channel_id)
        selected_member = random.choice(members)
        # member 중 자신 제외 (자신은 커피챗 대상이 될 수 없음)
        # members.remove(body["user"]["id"])
        view = templates.action.SELECT_RANDOM_COFFEE_CHAT_MODAL(
            selected_member, json.dumps({"members": members})
        )
        client.views_open(trigger_id=body["trigger_id"], view=view)

    except SlackApiError as e:
        logger.info(f"Error handling modal submission: {e}")


## VIEW : 3. 랜덤 커피챗 제안 모달
@app.view("suggest_random_coffee_chat_modal")
def handle_random_modal_submission(ack, body, client: WebClient = None):
    ack()
    try:
        # 제출된 데이터 처리 로직
        selected_user = ""
        message_blocks = ""
        selected_datetime = ""

        block_values: dict = body["view"]["state"]["values"]
        for block_id, block_value in block_values.items():
            if block_id.startswith("selected_member"):
                selected_user = block_value["user"]["selected_user"]
            elif block_id.startswith("message_input"):
                message_blocks = block_value["rich_text_input-action"][
                    "rich_text_value"
                ]
            elif block_id.startswith("pick_datetime"):
                selected_datetime = __convert_unix_to_kst(
                    block_value["datetimepicker-action"]["selected_date_time"]
                )

        if not selected_user or not message_blocks or not selected_datetime:
            return

        sender_user = body["user"]["id"]  # 제출한 사용자의 ID

        # 메시지 내용 구성
        blocks = templates.action.SEND_SUGGESTION_BLOCK(
            sender_user, message_blocks, selected_datetime
        )

        # 선택된 유저에게 DM 보내기
        client.chat_postMessage(
            channel=selected_user, blocks=blocks, text="커피챗 제안이 왔어요!"
        )

    except SlackApiError as e:
        logger.info(f"Error handling modal submission: {e}")


###################################################### ACTION ######################################################
## ACTION : 1. 커피 챗 제안하기 버튼 상호작용
@app.action("suggest_coffee_chat_button")
def handle_random_coffee_chat_button(
    ack, body, client: WebClient = None
) -> SlackResponse:
    ack()
    try:
        # 모달 열기
        return client.views_open(
            trigger_id=body["trigger_id"],
            view=templates.action.SUGGEST_COFFEE_CHAT_MODAL,
        )
    except SlackApiError as e:
        logger.info(f"Error opening modal: {e}")


## ACTION : 2. 랜덤 커피챗 제안하기 버튼 상호작용
@app.action("random_coffee_chat_button")
def handle_random_coffee_chat_button(
    ack, body, client: WebClient = None
) -> SlackResponse:
    ack()
    try:
        # 랜덤으로 커피챗 제안 로직
        return client.views_open(
            trigger_id=body["trigger_id"],
            view=templates.action.SELECT_CHANNEL_MODAL,
        )
    except SlackApiError as e:
        logger.info(f"Error handling random coffee chat: {e}")


## ACTION : 3. 채널 인원 중 랜덤 인원 한명 선별하기 버튼 상호작용
@app.action("roll_button")
def handle_roll_button(ack, body, client: WebClient):
    ack()
    try:
        private_metadata = body["view"]["private_metadata"]
        members = json.loads(private_metadata)["members"]
        selected_member = random.choice(members)

        # 임의의 접미사를 block_id에 추가
        block_id_suffix = f"-{random.randint(0, 9999)}"
        updated_view = templates.action.SELECT_RANDOM_COFFEE_CHAT_MODAL(
            selected_member, private_metadata
        )

        # block_id에 접미사 추가
        for block in updated_view["blocks"]:
            if "block_id" in block:
                block["block_id"] += block_id_suffix

        client.views_update(
            view_id=body["view"]["id"],
            view=updated_view,
        )
    except SlackApiError as e:
        logger.info(f"Error handling roll button: {e}")


## ACTION : 4. 커피챗 일정 완료 버튼 상호작용
@app.action("coffee_chat_complete")
def handle_coffee_chat_complete(ack, body, client: WebClient, respond: AsyncRespond):
    # 버튼 클릭 이벤트 확인
    ack()
    try:
        # 클릭한 버튼의 value에서 selected_date 가져오기
        receiver = body["user"]["id"]
        request_json = json.loads(body["actions"][0]["value"])
        sender = request_json["sender_user"]
        selected_date = request_json["selected_date"]

        # 메시지 업데이트
        respond(
            text="커피챗 일정을 완료했어요!",
            blocks=templates.action.SEND_CONFIRMATION_BLOCK(sender, selected_date),
        )

        # 메시지 전송
        client.chat_postMessage(
            channel=sender,
            blocks=templates.action.COMPLETION_BLOCK(receiver, selected_date),
            text="커피챗 일정 완료 알림",
        )

        # selected_date 문자열을 datetime 객체로 변환
        selected_date_dt = datetime.strptime(selected_date, "%Y년 %m월 %d일 %H시 %M분")

        # 현재 시간 가져오기
        now_dt = datetime.now()

        # 리마인드 시간 5분 전으로 설정
        reminder_time_dt = selected_date_dt - timedelta(minutes=5)

        # 유저 클라이언트로 변경
        client.token = settings.SLACK_USER_TOKEN
        if reminder_time_dt < now_dt:
            # 5분 보다 적은 시간으로 지정했을 경우 바로 알림
            reminder_time_unix = 1
        else:
            # 예약 시간으로부터 5분 전을 초로 바꾸어 설정
            reminder_time_unix = int((reminder_time_dt - now_dt).total_seconds())

        client.reminders_add(
            text=f"<@{receiver}>님과 예약된 커피 챗 알림을 드려요~ ! {selected_date}",
            time=reminder_time_unix,
            user=sender,
        )
        client.reminders_add(
            text=f"<@{sender}>님과 예약된 커피 챗 알림을 드려요~ ! {selected_date}",
            time=reminder_time_unix,
            user=receiver,
        )
        logger.info(f"Reminder set for {sender} at {reminder_time_dt}")

    except SlackApiError as e:
        logger.error(f"Error handling modal submission: {e}")


# 특정 채널의 모든 사용자 ID 가져오기
def _get_all_channel_members(client: WebClient, channel_id: str):
    members = []
    cursor = None

    while True:
        try:
            if cursor:
                response = client.conversations_members(
                    channel=channel_id, cursor=cursor
                )
            else:
                response = client.conversations_members(channel=channel_id)

            members.extend(response["members"])

            cursor = response.get("response_metadata", {}).get("next_cursor")
            if not cursor:
                break

        except SlackApiError as e:
            logger.error(f"Error fetching channel members: {e.response['error']}")
            break

    return members


def __convert_unix_to_kst(unix_timestamp: float) -> str:
    # UTC 시간대를 기준으로 datetime 객체 생성
    dt_utc = datetime.fromtimestamp(unix_timestamp, tz=timezone.utc)
    # KST 시간대 설정 (UTC+9)
    kst = timezone(timedelta(hours=9))
    # KST 시간대로 변환
    dt_kst = dt_utc.astimezone(kst)
    # 원하는 형식으로 포맷팅
    return dt_kst.strftime("%Y년 %m월 %d일 %H시 %M분")


# 모든 요청을 로깅하는 핸들러
@app.middleware
def log_request(logger, body, next):
    logger.info(body)
    return next()


# 앱 실행
if __name__ == "__main__":
    # SocketModeHandler를 사용하여 앱을 실행합니다.
    handler = SocketModeHandler(app, settings.SLACK_APP_TOKEN)
    handler.start()
