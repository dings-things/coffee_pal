# 커피팔 그게 뭔데?
- hashtag Slack, Slack Bolt, Infra


# 목적
일을 하는 것에서 그치는 것이 아닌, 일을 잘 하고 싶은 조직에서 좋은 문화를 구성하는 것은 일의 생산성이나 품질에도 여러 이점을 가져온다

필자가 개발하고자 하는 "CoffeePal"은 문제에 막혀 길을 잃어버린 사람이나 소소한 스몰 토크로 일에도 능률을 키울 수 있는 그러한 앱을 만들 고자 `커피 친구`라는 의미에서 커피팔을 기획하게 되었다

# 개발에 앞서...

먼저 사내 커뮤니케이션 툴인 Slack에서 상호작용을 통해, 쉽고 빠르게 커피 친구를 매칭해줘야 하는 요구사항이 있다

이에 앞서 간단하게 [Slack Workflow](https://slack.com/intl/ko-kr/features/workflow-automation)를 통하여, 전반적인 흐름을 파악해 본다


1. **Trigger Point 생성**
   테스트 용이기 때문에, Trigger는 `:커피:` 이모지로 반응하였을 때 워크플로가 실행 되도록 한다

2. **활성화 하기**
   반응한 메시지를 전송한 사용자에게 메시지를 보내어, 커피팔 매칭을 시작할 지 여부를 확인한다

3. **양식에서 정보 수집**
   개인화된 서비스를 위해 MBTI, 생년월일을 입력 받는다.
   해당 데이터의 기입은 Optional 하게 만든다

4. **대상, 일시, 주제를 지정한다**
   커피팔 대상과 커피 일정, 그리고 전반적인 주제를 사전에 정의한다.

5. **커피팔 대상에게 초대 메시지 보내기**
   앞서 지정한 데이터를 통해 커피팔에게 간략하게 초대 메시지를 보낸다

---

개인적으로 `Slack 워크플로`를 처음 사용해 보았는데, UI가 깔끔하고 사용성이 괜찮음을 느꼈다

다만, 사용자와 "상호작용"이라기 보다는, 일방적인 소통에 가깝기 때문에 slack app으로 확장 해보도록 한다

먹고 싶지 않은 음식을 억지로 먹여주는 느낌... 이랄까요?

![bg right](assets/never-feed.png)

---

# 요구사항
1. 미리 저장된 데이터를 기반으로 사용자 기반의 매칭을 할 수 있어야 한다

   - 개인정보 입력 시, 매칭 시스템 Trigger

2. App을 사용한 상호작용을 위해 컴퓨팅 리소스를 확보한다
   - [x] 사내 서버 (방화벽 관리 어려움)
   - [ ] AWS Lambda (서버리스, 무료)
3. 사용자에게 한눈에 봐도 알 수 있는 UI 제공
   - [Slack Block kit](https://app.slack.com/block-kit-builder/T579HA9NY#%7B%22blocks%22:%5B%7B%22type%22:%22section%22,%22text%22:%7B%22type%22:%22mrkdwn%22,%22text%22:%22Hello,%20Assistant%20to%20the%20Regional%20Manager%20Dwight!%20*Michael%20Scott*%20wants%20to%20know%20where%20you'd%20like%20to%20take%20the%20Paper%20Company%20investors%20to%20dinner%20tonight.%5Cn%5Cn%20*Please%20select%20a%20restaurant:*%22%7D%7D,%7B%22type%22:%22divider%22%7D,%7B%22type%22:%22section%22,%22text%22:%7B%22type%22:%22mrkdwn%22,%22text%22:%22*Farmhouse%20Thai%20Cuisine*%5Cn:star::star::star::star:%201528%20reviews%5Cn%20They%20do%20have%20some%20vegan%20options,%20like%20the%20roti%20and%20curry,%20plus%20they%20have%20a%20ton%20of%20salad%20stuff%20and%20noodles%20can%20be%20ordered%20without%20meat!!%20They%20have%20something%20for%20everyone%20here%22%7D,%22accessory%22:%7B%22type%22:%22image%22,%22image_url%22:%22https://s3-media3.fl.yelpcdn.com/bphoto/c7ed05m9lC2EmA3Aruue7A/o.jpg%22,%22alt_text%22:%22alt%20text%20for%20image%22%7D%7D,%7B%22type%22:%22section%22,%22text%22:%7B%22type%22:%22mrkdwn%22,%22text%22:%22*Kin%20Khao*%5Cn:star::star::star::star:%201638%20reviews%5Cn%20The%20sticky%20rice%20also%20goes%20wonderfully%20with%20the%20caramelized%20pork%20belly,%20which%20is%20absolutely%20melt-in-your-mouth%20and%20so%20soft.%22%7D,%22accessory%22:%7B%22type%22:%22image%22,%22image_url%22:%22https://s3-media2.fl.yelpcdn.com/bphoto/korel-1YjNtFtJlMTaC26A/o.jpg%22,%22alt_text%22:%22alt%20text%20for%20image%22%7D%7D,%7B%22type%22:%22section%22,%22text%22:%7B%22type%22:%22mrkdwn%22,%22text%22:%22*Ler%20Ros*%5Cn:star::star::star::star:%202082%20reviews%5Cn%20I%20would%20really%20recommend%20the%20%20Yum%20Koh%20Moo%20Yang%20-%20Spicy%20lime%20dressing%20and%20roasted%20quick%20marinated%20pork%20shoulder,%20basil%20leaves,%20chili%20&%20rice%20powder.%22%7D,%22accessory%22:%7B%22type%22:%22image%22,%22image_url%22:%22https://s3-media2.fl.yelpcdn.com/bphoto/DawwNigKJ2ckPeDeDM7jAg/o.jpg%22,%22alt_text%22:%22alt%20text%20for%20image%22%7D%7D,%7B%22type%22:%22divider%22%7D,%7B%22type%22:%22actions%22,%22elements%22:%5B%7B%22type%22:%22button%22,%22text%22:%7B%22type%22:%22plain_text%22,%22text%22:%22Farmhouse%22,%22emoji%22:true%7D,%22value%22:%22click_me_123%22%7D,%7B%22type%22:%22button%22,%22text%22:%7B%22type%22:%22plain_text%22,%22text%22:%22Kin%20Khao%22,%22emoji%22:true%7D,%22value%22:%22click_me_123%22,%22url%22:%22https://google.com%22%7D,%7B%22type%22:%22button%22,%22text%22:%7B%22type%22:%22plain_text%22,%22text%22:%22Ler%20Ros%22,%22emoji%22:true%7D,%22value%22:%22click_me_123%22,%22url%22:%22https://google.com%22%7D%5D%7D%5D%7D) 활용

## 사용법
- `SLACK_APP_TOKEN, SLACK_BOT_TOKEN, SLACK_USER_TOKEN` 설정
- [개발 문서](https://dings-things.github.io/blog/posts/coffee-pal) 참고하여 커스터마이징
