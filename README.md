# stake.py
Stake(stake.com)用の非公式APIライブラリ

## 可能な操作
- 為替レートを取得(`get_currency_rate()`)
- 通知を取得(`get_notification()`)
- VIP進行度を取得(`get_vip_progress()`)
- 残高を取得(`get_balances()`)
- 入金アドレスを取得(`get_deposit_address()`)
- チップを送信(`send_tip("star", "ltc", 0.1)`)
- ユーザーデータを取得(`get_user_meta()`)
- メールデータを取得(`get_email_meta()`)
- 番号データを取得(`get_phone_meta()`)
- KYCデータを取得(`get_kyc_meta()`)
- シードペアを取得(`get_seed_pair()`)
- Crashの履歴を取得(`get_crash_history()`)
- Diceのベット(`bet_dice(100, "jpy", 50.5, "above")`)
- リアルタイムなデータを取得(`StakeSocket()`)

## サンプル
### INIT
```py
from stake import Stake, StakeSocket, StakeSolver

# Request Base
stake = Stake(
	access_token="API KEY HERE",
	two_factor="TWO FACTOR KEY HERE",
	user_agent="USER-AGENT HERE",
	client_hints="UA-CH HERE",
	cf_clearance="CF_CLEARANCE COOKIE HERE"
)

# Websocket Base
stake_ws = StakeSocket(
	access_token="API KEY HERE",
	user_agent="USER-AGENT HERE",
	cf_clearance="CF_CLEARANCE COOKIE HERE"
)
```

## インストール
### 必要環境
- Python 3.9.13
- pip 22.0.4
- git 2.42.0
### インストール
`pip install -U git+https://github.com/yuki-1729/stake.py.git`

## ライセンス
```
MIT License

Copyright (c) 2024 Yuki

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```