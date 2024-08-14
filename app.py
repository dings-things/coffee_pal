from datetime import datetime, timedelta
import json
import random
from scheduler import Scheduler
from slack_bolt import App
from slack_sdk.web import WebClient, SlackResponse
from slack_bolt.adapter.socket_mode import SocketModeHandler
from slack_bolt.context.respond.async_respond import AsyncRespond
from slack_sdk.errors import SlackApiError
from db.reservation import FileDB, ReservationEntity
import logging
import endpoints
import templates.views, templates.blocks, templates.modals
import utils

logging.basicConfig(level=logging.INFO)
from config import settings
import ssl

ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

slack_client = WebClient(token=settings.SLACK_BOT_TOKEN, ssl=ssl_context)

app = App(client=slack_client)
db = FileDB(settings.FILE_PATH, settings.FILE_LOCK_PATH)
scheduler = Scheduler(db, "23:59:59")
logger = logging.getLogger(__name__)


###################################################### EVENT ######################################################
## EVENT : 1. 앱 홈 화면 View
@app.event(endpoints.HOME_OPEND)
def handle_app_home_opened(event, client: WebClient) -> SlackResponse:
    user_id = event["user"]
    # App Home 업데이트 로직
    return client.views_publish(
        user_id=user_id,  # App Home을 업데이트할 사용자 ID
        view=templates.views.HOME_OPENED(
            templates.blocks.RESERVATION_BLOCK(db.get_reservations_by_user_id(user_id))
        ),
    )


###################################################### VIEW ######################################################
## VIEW : 1. 커피챗 제안 모달
@app.view(endpoints.SUGGEST_COFFEE_CHAT_MODAL)
def handle_modal_submission(ack, body, client: WebClient):
    ack()
    try:
        # 제출된 데이터 처리 로직
        selected_user = body["view"]["state"]["values"]["user_select"]["user"][
            "selected_user"
        ]
        message_blocks = body["view"]["state"]["values"]["message_input"][
            "rich_text_input-action"
        ]["rich_text_value"]
        selected_datetime = utils.convert_unix_to_kst(
            body["view"]["state"]["values"]["pick_datetime"]["datetimepicker-action"][
                "selected_date_time"
            ]
        )
        sender_user = body["user"]["id"]  # 제출한 사용자의 ID

        # 메시지 내용 구성
        blocks = templates.blocks.SEND_SUGGESTION(
            sender_user, message_blocks, selected_datetime
        )

        # 선택된 유저에게 DM 보내기
        client.chat_postMessage(
            channel=selected_user, blocks=blocks, text="커피챗 제안이 왔어요!"
        )
    except SlackApiError as e:
        logger.info(f"Error handling modal submission: {e}")


## VIEW : 2. 랜덤 커피챗 선택 모달
@app.view(endpoints.SELECT_RANDOM_COFFEE_CHAT_MODAL)
def handle_select_random_coffee_chat_modal_submission(
    ack, body, payload, client: WebClient
):
    ack()
    try:
        channel_id = payload["state"]["values"]["channel_select"]["channel"][
            "selected_channel"
        ]
        members = _get_all_channel_members(client, channel_id)
        selected_member = random.choice(members)
        # member 중 자신 제외 (자신은 커피챗 대상이 될 수 없음)
        # members.remove(body["user"]["id"])
        view = templates.modals.SELECT_RANDOM_COFFEE_CHAT(
            selected_member, json.dumps({"members": members})
        )
        client.views_open(trigger_id=body["trigger_id"], view=view)

    except SlackApiError as e:
        logger.info(f"Error handling modal submission: {e}")


## VIEW : 그룹 커피챗 선택 모달
@app.view(endpoints.SELECT_GROUP_COFFEE_CHAT_MODAL)
def handle_select_group_coffee_chat_modal_submission(ack, body, client: WebClient):
    ack()
    try:
        channel_id = body["view"]["state"]["values"]["channel_select"]["channel"][
            "selected_channel"
        ]
        members = _get_all_channel_members(client, channel_id)
        view = templates.modals.SELECT_GROUP_COFFEE_CHAT(members)
        client.views_open(trigger_id=body["trigger_id"], view=view)

    except SlackApiError as e:
        logger.info(f"Error handling modal submission: {e}")


## VIEW : 그룹 커피챗 제안 모달
@app.view(endpoints.SUGGEST_GROUP_COFFEE_CHAT_MODAL)
def handle_group_modal_submission(ack, body, payload, client: WebClient):
    ack()
    try:
        # 제출된 데이터 처리 로직
        block_values: dict = payload["state"]["values"]
        selected_users = block_values["selected_members"]["multi_users_select-action"][
            "selected_users"
        ]
        message_blocks = block_values["message_input"]["rich_text_input-action"][
            "rich_text_value"
        ]
        selected_datetime = utils.convert_unix_to_kst(
            block_values["pick_datetime"]["datetimepicker-action"]["selected_date_time"]
        )

        sender_user = body["user"]["id"]  # 제출한 사용자의 ID

        # 메시지 내용 구성
        blocks = templates.blocks.SEND_SUGGESTION(
            sender_user, message_blocks, selected_datetime
        )

        for selected_user in selected_users:
            # 선택된 유저에게 DM 보내기
            client.chat_postMessage(
                channel=selected_user, blocks=blocks, text="커피챗 제안이 왔어요!"
            )

    except SlackApiError as e:
        logger.info(f"Error handling modal submission: {e}")


## VIEW : 3. 랜덤 커피챗 제안 모달
@app.view(endpoints.SUGGEST_RANDOM_COFFEE_CHAT_MODAL)
def handle_random_modal_submission(ack, body, payload, client: WebClient):
    ack()
    try:
        # 제출된 데이터 처리 로직
        selected_user = ""
        message_blocks = ""
        selected_datetime = ""

        block_values: dict = payload["state"]["values"]
        for block_id, block_value in block_values.items():
            if block_id.startswith("selected_member"):
                selected_user = block_value["user"]["selected_user"]
            elif block_id.startswith("message_input"):
                message_blocks = block_value["rich_text_input-action"][
                    "rich_text_value"
                ]
            elif block_id.startswith("pick_datetime"):
                selected_datetime = utils.convert_unix_to_kst(
                    block_value["datetimepicker-action"]["selected_date_time"]
                )

        if not selected_user or not message_blocks or not selected_datetime:
            return

        sender_user = body["user"]["id"]  # 제출한 사용자의 ID

        # 메시지 내용 구성
        blocks = templates.blocks.SEND_SUGGESTION(
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
@app.action(endpoints.SUGGEST_COFFEE_CHAT_BUTTON)
def handle_suggest_coffee_chat_button(ack, body, client: WebClient) -> SlackResponse:
    ack()
    try:
        # 모달 열기
        return client.views_open(
            trigger_id=body["trigger_id"],
            view=templates.modals.SUGGEST_COFFEE_CHAT,
        )
    except SlackApiError as e:
        logger.info(f"Error opening modal: {e}")


## ACTION : 2. 랜덤 커피챗 제안하기 버튼 상호작용
@app.action(endpoints.RANDOM_COFFEE_CHAT_BUTTON)
def handle_random_coffee_chat_button(ack, body, client: WebClient) -> SlackResponse:
    ack()
    try:
        # 랜덤으로 커피챗 제안 로직
        return client.views_open(
            trigger_id=body["trigger_id"],
            view=templates.modals.SELECT_CHANNEL,
        )
    except SlackApiError as e:
        logger.info(f"Error handling random coffee chat: {e}")


## ACTION : 그룹 커피챗 제안하기 버튼 상호작용
@app.action(endpoints.GROUP_COFFEE_CHAT_BUTTON)
def handle_group_coffee_chat_button(ack, body, client: WebClient):
    ack()
    try:
        # 그룹 커피챗 제안 로직
        return client.views_open(
            trigger_id=body["trigger_id"],
            view=templates.modals.SELECT_GROUP_CHANNEL,
        )
    except SlackApiError as e:
        logger.info(f"Error handling roll button: {e}")


## ACTION : 3. 채널 인원 중 랜덤 인원 한명 선별하기 버튼 상호작용
@app.action(endpoints.ROLL_BUTTON)
def handle_roll_button(ack, body, client: WebClient):
    ack()
    try:
        private_metadata = body["view"]["private_metadata"]
        members = json.loads(private_metadata)["members"]
        selected_member = random.choice(members)

        # 임의의 접미사를 block_id에 추가
        block_id_suffix = f"-{random.randint(0, 9999)}"
        updated_view = templates.modals.SELECT_RANDOM_COFFEE_CHAT(
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
@app.action(endpoints.COFFEE_CHAT_COMPLETE)
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
            blocks=templates.blocks.SEND_CONFIRMATION(sender, selected_date),
        )

        # 메시지 전송
        client.chat_postMessage(
            channel=sender,
            blocks=templates.blocks.COMPLETION(receiver, selected_date),
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
            # 예약 시간으로부터 5분 전을 unix timestamp로 변환
            reminder_time_unix = int(reminder_time_dt.timestamp())

        sender_reservation = ReservationEntity(
            target_id=receiver,
            date=selected_date_dt,
            message=body["message"]["blocks"][3],
        )
        receiver_reservation = ReservationEntity(
            target_id=sender,
            date=selected_date_dt,
            message=body["message"]["blocks"][3],
        )
        db.add(sender, sender_reservation)
        db.add(receiver, receiver_reservation)

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


# ACTION : 5. 메시지 보기 버튼 클릭 이벤트 핸들러
@app.action(endpoints.VIEW_MESSAGE_BUTTON)
def handle_view_message_button(ack, body, client: WebClient):
    ack()
    uuid = body["actions"][0]["value"]

    # FileDB에서 해당 UUID의 예약 정보를 가져옵니다
    reservation = None
    for reservations in db.data.values():
        for res in reservations:
            if res.uuid == uuid:
                reservation = res
                break
        if reservation:
            break

    if reservation:
        # 메시지를 보여주는 view 생성
        view = templates.views.MESSAGE_DETAIL(
            reservation.target_id, reservation.date, reservation.message
        )

        # View를 열기
        try:
            client.views_open(trigger_id=body["trigger_id"], view=view)
        except SlackApiError as e:
            logger.error(f"Error opening view: {e}")


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


# 앱 실행
if __name__ == "__main__":
    # SocketModeHandler를 사용하여 앱을 실행합니다.
    handler = SocketModeHandler(app, settings.SLACK_APP_TOKEN)
    scheduler.start()

    handler.start()
