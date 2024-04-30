"""
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
"""

import json
import uuid
import pyotp
import string
import secrets
import asyncio
import tls_client

from websockets.client import connect
from anticaptchaofficial.turnstileproxyon import *

class StakeError(Exception):
    pass

class Stake:
    def __init__(self, access_token: str, two_factor: str, user_agent: str, client_hints: str, cf_clearance: str) -> None:
        if access_token == None or two_factor == None or user_agent == None or client_hints == None or cf_clearance == None:
            raise StakeError("必須要素が指定されていません")

        self.session = tls_client.Session(
            client_identifier="safari_ios_16_0",
            random_tls_extension_order=True
        )
        self.totp = pyotp.TOTP(two_factor)

        self.headers = {
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "ja,en-US;q=0.9,en;q=0.8",
            "Access-Control-Allow-Origin": "*",
            "Content-Type": "application/json",
            "Origin": "https://stake.com",
            "Referer": "https://stake.com/",
            "Sec-Ch-Ua": client_hints,
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": "\"Windows\"",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "User-Agent": user_agent,
            "X-Access-Token": access_token,
            "X-Language": "ja"
        }

        self.cookies = {
            "cf_clearance": cf_clearance
        }

    def get_currency_rate(self) -> dict:
        try:
            response = self.session.post(
                "https://stake.com/_api/graphql",
                headers=self.headers,
                json={
                    "query": "query CurrencyConversionRate {\n  info {\n    currencies {\n      name\n      eur: value(fiatCurrency: eur)\n      jpy: value(fiatCurrency: jpy)\n      usd: value(fiatCurrency: usd)\n      brl: value(fiatCurrency: brl)\n      cad: value(fiatCurrency: cad)\n      cny: value(fiatCurrency: cny)\n      idr: value(fiatCurrency: idr)\n      inr: value(fiatCurrency: inr)\n      krw: value(fiatCurrency: krw)\n      php: value(fiatCurrency: php)\n      rub: value(fiatCurrency: rub)\n      mxn: value(fiatCurrency: mxn)\n      dkk: value(fiatCurrency: dkk)\n    }\n  }\n}\n",
                    "variables": {}
                },
                cookies=self.cookies
            ).json()
        except:
            raise StakeError("通信内容を解析できませんでした(CFによるブロックの可能性)")

        return response
    
    def get_notification(self, limit: int = 20) -> dict:
        try:
            response = self.session.post(
                "https://stake.com/_api/graphql",
                headers=self.headers,
                json={
                    "query": "query NotificationList($limit: Int, $offset: Int) {\n  user {\n    id\n    notificationList(limit: $limit, offset: $offset) {\n      ...Notification\n    }\n  }\n}\n\nfragment Notification on Notification {\n  id\n  type\n  acknowledged\n  __typename\n  data {\n    __typename\n    ... on NotificationKyc {\n      kycStatus: status\n    }\n    ... on UserFlag {\n      createdAt\n      flag\n    }\n    ... on ChatTip {\n      createdAt\n      currency\n      amount\n      sendBy {\n        name\n      }\n    }\n    ... on NotificationKycBanned {\n      kycBannedMessage: message\n    }\n    ... on ChatRainUser {\n      amount\n      currency\n      rain {\n        createdAt\n        sendBy {\n          name\n        }\n      }\n    }\n    ... on CashAdvance {\n      id\n      advanceAmount\n      currency\n      createdAt\n    }\n    ... on UserBonus {\n      createdAt\n      currency\n      amount\n      credit\n    }\n    ... on SportBet {\n      id\n      amount\n      active\n      currency\n      status\n      payoutMultiplier\n      cashoutMultiplier\n      payout\n      createdAt\n      system\n      potentialMultiplier\n      adjustments {\n        id\n        payoutMultiplier\n        updatedAt\n        createdAt\n      }\n      user {\n        id\n        name\n      }\n      search {\n        iid\n      }\n      outcomes {\n        odds\n        status\n        outcome {\n          id\n          name\n          active\n          odds\n        }\n        market {\n          ...SportMarket\n        }\n        fixture {\n          id\n          slug\n          provider\n          tournament {\n            ...TournamentTree\n          }\n          data {\n            ...SportFixtureDataMatch\n            ...SportFixtureDataOutright\n            __typename\n          }\n        }\n      }\n    }\n    ... on SwishBet {\n      ...SwishBetFragment\n    }\n    ... on WalletDeposit {\n      id\n      createdAt\n      amount\n      currency\n      chain\n      walletStatus: status\n      tokensReceived {\n        currency\n        amount\n      }\n    }\n    ... on RacePosition {\n      position\n      payoutAmount\n      currency\n      race {\n        name\n        endTime\n      }\n    }\n    ... on CommunityMute {\n      active\n      message\n      expireAt\n    }\n    ... on ChallengeWin {\n      challenge {\n        ...Challenge\n      }\n    }\n    ... on Challenge {\n      ...Challenge\n    }\n    ... on NotificationFiatError {\n      code\n      limitType\n      fiatErrorAmount: amount\n      fiatErrorCurrency: currency\n    }\n    ... on VeriffUser {\n      veriffStatus: status\n      veriffReason: reason\n    }\n    ... on SportsbookPromotionBet {\n      id\n      bet {\n        id\n      }\n      betAmount\n      value\n      currency\n      payout\n      payoutValue\n      sportsbookPromotionBetStatus: status\n      sportsbookPromotionBetUser: user {\n        id\n        name\n      }\n      promotion {\n        id\n        name\n      }\n    }\n    ... on UserPostcardCode {\n      id\n      claimedAt\n      postcardCode: code\n    }\n  }\n}\n\nfragment SportMarket on SportMarket {\n  id\n  name\n  status\n  extId\n  specifiers\n  customBetAvailable\n  provider\n}\n\nfragment TournamentTree on SportTournament {\n  id\n  name\n  slug\n  category {\n    ...CategoryTree\n  }\n}\n\nfragment CategoryTree on SportCategory {\n  id\n  name\n  slug\n  sport {\n    id\n    name\n    slug\n  }\n}\n\nfragment SportFixtureDataMatch on SportFixtureDataMatch {\n  startTime\n  competitors {\n    ...SportFixtureCompetitor\n  }\n  teams {\n    name\n    qualifier\n  }\n  tvChannels {\n    language\n    name\n    streamUrl\n  }\n  __typename\n}\n\nfragment SportFixtureCompetitor on SportFixtureCompetitor {\n  name\n  extId\n  countryCode\n  abbreviation\n  iconPath\n}\n\nfragment SportFixtureDataOutright on SportFixtureDataOutright {\n  name\n  startTime\n  endTime\n  __typename\n}\n\nfragment SwishBetFragment on SwishBet {\n  __typename\n  active\n  amount\n  cashoutMultiplier\n  createdAt\n  currency\n  customBet\n  id\n  odds\n  payout\n  payoutMultiplier\n  updatedAt\n  status\n  user {\n    id\n    name\n    preferenceHideBets\n  }\n  outcomes {\n    __typename\n    id\n    odds\n    lineType\n    outcome {\n      ...SwishMarketOutcomeFragment\n    }\n  }\n}\n\nfragment SwishMarketOutcomeFragment on SwishMarketOutcome {\n  __typename\n  id\n  line\n  over\n  under\n  gradeOver\n  gradeUnder\n  suspended\n  balanced\n  name\n  competitor {\n    id\n    name\n  }\n  market {\n    id\n    stat {\n      name\n      value\n    }\n    game {\n      id\n      fixture {\n        id\n        name\n        slug\n        status\n        eventStatus {\n          ...SportFixtureEventStatus\n          ...EsportFixtureEventStatus\n        }\n        data {\n          ... on SportFixtureDataMatch {\n            __typename\n            startTime\n            competitors {\n              name\n              extId\n              countryCode\n              abbreviation\n            }\n          }\n        }\n        tournament {\n          id\n          slug\n          category {\n            id\n            slug\n            sport {\n              id\n              name\n              slug\n            }\n          }\n        }\n      }\n    }\n  }\n}\n\nfragment SportFixtureEventStatus on SportFixtureEventStatusData {\n  __typename\n  homeScore\n  awayScore\n  matchStatus\n  clock {\n    matchTime\n    remainingTime\n  }\n  periodScores {\n    homeScore\n    awayScore\n    matchStatus\n  }\n  currentTeamServing\n  homeGameScore\n  awayGameScore\n  statistic {\n    yellowCards {\n      away\n      home\n    }\n    redCards {\n      away\n      home\n    }\n    corners {\n      home\n      away\n    }\n  }\n}\n\nfragment EsportFixtureEventStatus on EsportFixtureEventStatus {\n  matchStatus\n  homeScore\n  awayScore\n  scoreboard {\n    homeGold\n    awayGold\n    homeGoals\n    awayGoals\n    homeKills\n    awayKills\n    gameTime\n    homeDestroyedTowers\n    awayDestroyedTurrets\n    currentRound\n    currentCtTeam\n    currentDefTeam\n    time\n    awayWonRounds\n    homeWonRounds\n    remainingGameTime\n  }\n  periodScores {\n    type\n    number\n    awayGoals\n    awayKills\n    awayScore\n    homeGoals\n    homeKills\n    homeScore\n    awayWonRounds\n    homeWonRounds\n    matchStatus\n  }\n  __typename\n}\n\nfragment Challenge on Challenge {\n  id\n  type\n  active\n  adminCreated\n  completedAt\n  award\n  claimCount\n  claimMax\n  currency\n  isRefunded\n  minBetUsd\n  betCurrency\n  startAt\n  expireAt\n  updatedAt\n  createdAt\n  targetMultiplier\n  game {\n    id\n    name\n    slug\n    thumbnailUrl\n  }\n  creatorUser {\n    ...UserTags\n  }\n  affiliateUser {\n    ...UserTags\n  }\n  wins {\n    id\n    claimedBy {\n      ...UserTags\n    }\n  }\n}\n\nfragment UserTags on User {\n  id\n  name\n  isMuted\n  isRainproof\n  isIgnored\n  isHighroller\n  isSportHighroller\n  leaderboardDailyProfitRank\n  leaderboardDailyWageredRank\n  leaderboardWeeklyProfitRank\n  leaderboardWeeklyWageredRank\n  flags {\n    flag\n    rank\n    createdAt\n  }\n  roles {\n    name\n    expireAt\n    message\n  }\n  createdAt\n  preferenceHideBets\n}\n",
                    "variables": {
                        "limit": limit,
                        "offset": 0
                    }
                },
                cookies=self.cookies
            ).json()
        except:
            raise StakeError("通信内容を解析できませんでした(CFによるブロックの可能性)")

        return response
    
    def get_vip_progress(self):
        try:
            response = self.session.post(
                "https://stake.com/_api/graphql",
                headers=self.headers,
                json={
                    "operationName": "VipProgressMeta",
                    "query": "query VipProgressMeta {\n  user {\n    id\n    flagProgress {\n      flag\n      progress\n      __typename\n    }\n    __typename\n  }\n}\n"
                },
                cookies=self.cookies
            ).json()
        except:
            raise StakeError("通信内容を解析できませんでした(CFによるブロックの可能性)")

        return response
    
    def get_balances(self):
        try:
            response = self.session.post(
                "https://stake.com/_api/graphql",
                headers=self.headers,
                json={
                    "operationName": "UserBalances",
                    "query": "query UserBalances {\n  user {\n    id\n    balances {\n      available {\n        amount\n        currency\n        __typename\n      }\n      vault {\n        amount\n        currency\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n}\n"
                },
                cookies=self.cookies
            ).json()
        except:
            raise StakeError("通信内容を解析できませんでした(CFによるブロックの可能性)")

        return response
    
    def get_deposit_address(self, currency: str = "ltc"):
        try:
            response = self.session.post(
                "https://stake.com/_api/graphql",
                headers=self.headers,
                json={
                    "operationName": "DepositAddress",
                    "query": "query DepositAddress($chain: CryptoChainEnum, $currency: CryptoCurrencyEnum!, $type: WalletAddressType!, $infoCurrency: CurrencyEnum!) {\n  info {\n    currency(currency: $infoCurrency) {\n      requiredConfirmations\n      __typename\n    }\n    __typename\n  }\n  user {\n    id\n    depositAddress(chain: $chain, currency: $currency, type: $type) {\n      id\n      address\n      currency\n      __typename\n    }\n    __typename\n  }\n}\n",
                    "variables": {
                        "currency": currency,
                        "infoCurrency": currency,
                        "type": "default"
                    }
                },
                cookies=self.cookies
            ).json()
        except:
            raise StakeError("通信内容を解析できませんでした(CFによるブロックの可能性)")

        return response
    
    def send_tip(self, stake_id: str, currency: str, amount: float) -> dict:
        try:
            response = self.session.post(
                "https://stake.com/_api/graphql",
                headers=self.headers,
                json={
                    "operationName": "SendTipMeta",
                    "query": "query SendTipMeta($name: String) {\n  user(name: $name) {\n    id\n    name\n    __typename\n  }\n  self: user {\n    id\n    hasTfaEnabled\n    isTfaSessionValid\n    balances {\n      available {\n        amount\n        currency\n        __typename\n      }\n      vault {\n        amount\n        currency\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n}\n",
                    "variables": {
                        "name": stake_id
                    }
                },
                cookies=self.cookies
            ).json()
        except:
            raise StakeError("通信内容を解析できませんでした(CFによるブロックの可能性)")
        if response["data"]["user"] == None:
            raise StakeError("IDを見つけられませんでした")
        user_id = response["data"]["user"]["id"]
        
        try:
            response = self.session.post(
                "https://stake.com/_api/graphql",
                headers=self.headers,
                json={
                    "operationName": "SendTip",
                    "query": "mutation SendTip($userId: String!, $amount: Float!, $currency: CurrencyEnum!, $isPublic: Boolean, $chatId: String!, $tfaToken: String) {\n  sendTip(\n    userId: $userId\n    amount: $amount\n    currency: $currency\n    isPublic: $isPublic\n    chatId: $chatId\n    tfaToken: $tfaToken\n  ) {\n    id\n    amount\n    currency\n    user {\n      id\n      name\n      __typename\n    }\n    sendBy {\n      id\n      name\n      balances {\n        available {\n          amount\n          currency\n          __typename\n        }\n        vault {\n          amount\n          currency\n          __typename\n        }\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n}\n",
                    "variables": {
                        "userId": user_id,
                        "amount": amount,
                        "currency": currency,
                        "isPublic": False,
                        "chatId": "c65b4f32-0001-4e1d-9cd6-e4b3538b43ae",
                        "tfaToken": self.totp.now()
                    }
                },
                cookies=self.cookies
            ).json()
        except:
            raise StakeError("通信内容を解析できませんでした(CFによるブロックの可能性)")

        return response
    
    def get_user_meta(self, signup_code: bool = True) -> dict:
        try:
            response = self.session.post(
                "https://stake.com/_api/graphql",
                headers=self.headers,
                json={
                    "query": "query UserMeta($name: String, $signupCode: Boolean = false) {\n  user(name: $name) {\n    id\n    name\n    isMuted\n    isRainproof\n    isBanned\n    createdAt\n    campaignSet\n    selfExclude {\n      id\n      status\n      active\n      createdAt\n      expireAt\n    }\n    signupCode @include(if: $signupCode) {\n      id\n      code {\n        id\n        code\n      }\n    }\n  }\n}\n",
                    "variables": {
                        "signupCode": signup_code
                    }
                },
                cookies=self.cookies
            ).json()
        except:
            raise StakeError("通信内容を解析できませんでした(CFによるブロックの可能性)")

        return response
    
    def get_email_meta(self) -> dict:
        try:
            response = self.session.post(
                "https://stake.com/_api/graphql",
                headers=self.headers,
                json={
                    "query": "query UserEmailMeta {\n  user {\n    ...UserEmailFragment\n  }\n}\n\nfragment UserEmailFragment on User {\n  id\n  email\n  hasEmailVerified\n  hasEmailSubscribed\n}\n",
                    "variables": {}
                },
                cookies=self.cookies
            ).json()
        except:
            raise StakeError("通信内容を解析できませんでした(CFによるブロックの可能性)")

        return response
    
    def get_phone_meta(self) -> dict:
        try:
            response = self.session.post(
                "https://stake.com/_api/graphql",
                headers=self.headers,
                json={
                    "query": "query UserPhoneMeta {\n  user {\n    ...UserPhoneFragment\n  }\n}\n\nfragment UserPhoneFragment on User {\n  id\n  phoneNumber\n  phoneCountryCode\n  hasPhoneNumberVerified\n}\n",
                    "variables": {}
                },
                cookies=self.cookies
            ).json()
        except:
            raise StakeError("通信内容を解析できませんでした(CFによるブロックの可能性)")

        return response
    
    def get_kyc_meta(self) -> dict:
        try:
            response = self.session.post(
                "https://stake.com/_api/graphql",
                headers=self.headers,
                json={
                    "query": "query UserKycInfo {\n  isDiscontinuedBlocked\n  user {\n    id\n    roles {\n      name\n    }\n    kycStatus\n    dob\n    createdAt\n    isKycBasicRequired\n    isKycExtendedRequired\n    isKycFullRequired\n    isKycUltimateRequired\n    hasEmailVerified\n    phoneNumber\n    hasPhoneNumberVerified\n    email\n    registeredWithVpn\n    isBanned\n    isSuspended\n    isSuspendedSportsbook\n    kycBasic {\n      ...UserKycBasic\n    }\n    kycExtended {\n      ...UserKycExtended\n    }\n    kycFull {\n      ...UserKycFull\n    }\n    kycUltimate {\n      ...UserKycUltimate\n    }\n    veriffStatus\n    jpyAlternateName: cashierAlternateName(currency: jpy) {\n      firstName\n      lastName\n    }\n    nationalId\n    outstandingWagerAmount {\n      currency\n      amount\n      progress\n    }\n    activeDepositBonus {\n      status\n    }\n    activeRollovers {\n      id\n      active\n      user {\n        id\n      }\n      amount\n      lossAmount\n      createdAt\n      note\n      currency\n      expectedAmount\n      expectedAmountMin\n      progress\n      activeBets {\n        id\n        iid\n        game {\n          id\n          slug\n          name\n        }\n        bet {\n          __typename\n        }\n      }\n    }\n  }\n}\n\nfragment UserKycBasic on UserKycBasic {\n  active\n  address\n  birthday\n  city\n  country\n  createdAt\n  firstName\n  id\n  lastName\n  phoneNumber\n  rejectedReason\n  status\n  updatedAt\n  zipCode\n  occupation\n}\n\nfragment UserKycExtended on UserKycExtended {\n  id\n  active\n  createdAt\n  id\n  rejectedReason\n  status\n}\n\nfragment UserKycFull on UserKycFull {\n  active\n  createdAt\n  id\n  rejectedReason\n  status\n}\n\nfragment UserKycUltimate on UserKycUltimate {\n  id\n  active\n  createdAt\n  id\n  rejectedReason\n  status\n}\n",
                    "variables": {}
                },
                cookies=self.cookies
            ).json()
        except:
            raise StakeError("通信内容を解析できませんでした(CFによるブロックの可能性)")

        return response
    
    def get_seed_pair(self):
        try:
            response = self.session.post(
                "https://stake.com/_api/graphql",
                headers=self.headers,
                json={
                    "operationName": "UserSeedPair",
                    "query": "query UserSeedPair {\n  user {\n    id\n    activeClientSeed {\n      id\n      seed\n      __typename\n    }\n    activeServerSeed {\n      id\n      nonce\n      seedHash\n      nextSeedHash\n      __typename\n    }\n    activeCasinoBets {\n      id\n      amount\n      currency\n      game\n      createdAt\n      __typename\n    }\n    __typename\n  }\n}\n"
                },
                cookies=self.cookies
            ).json()
        except:
            raise StakeError("通信内容を解析できませんでした(CFによるブロックの可能性)")

        return response
    
    def get_crash_history(self):
        try:
            response = self.session.post(
                "https://stake.com/_api/graphql",
                headers=self.headers,
                json={
                    "operationName": "CrashGameListHistory",
                    "query": "query CrashGameListHistory($limit: Int, $offset: Int) {\n  crashGameList(limit: $limit, offset: $offset) {\n    id\n    startTime\n    crashpoint\n    hash {\n      id\n      hash\n      __typename\n    }\n    __typename\n  }\n}\n",
                    "variables": {}
                },
                cookies=self.cookies
            ).json()
        except:
            raise StakeError("通信内容を解析できませんでした(CFによるブロックの可能性)")

        return response
    
    def bet_dice(self, bet_size: float, bet_currency: str, roll_over: float, condition: str):
        identifier_chars = string.ascii_letters + string.digits + "-_"
        identifier = "".join([secrets.choice(identifier_chars) for i in range(21)])

        try:
            response = self.session.post(
                "https://stake.com/_api/graphql",
                headers=self.headers,
                json={
                    "query": "mutation DiceRoll($amount: Float!, $target: Float!, $condition: CasinoGameDiceConditionEnum!, $currency: CurrencyEnum!, $identifier: String!) {\n  diceRoll(\n    amount: $amount\n    target: $target\n    condition: $condition\n    currency: $currency\n    identifier: $identifier\n  ) {\n    ...CasinoBet\n    state {\n      ...CasinoGameDice\n    }\n  }\n}\n\nfragment CasinoBet on CasinoBet {\n  id\n  active\n  payoutMultiplier\n  amountMultiplier\n  amount\n  payout\n  updatedAt\n  currency\n  game\n  user {\n    id\n    name\n  }\n}\n\nfragment CasinoGameDice on CasinoGameDice {\n  result\n  target\n  condition\n}\n",
                    "variables": {
                        "amount": bet_size,
                        "condition": condition,
                        "currency": bet_currency,
                        "identifier": identifier,
                        "target": roll_over
                    }
                },
                cookies=self.cookies
            ).json()
        except:
            raise StakeError("通信内容を解析できませんでした(CFによるブロックの可能性)")

        return response

class StakeSocket:
    def __init__(self, access_token: str, user_agent: str, cf_clearance: str):
        if access_token == None or access_token == "":
            raise StakeError("APIキーが指定されていません")
        
        self.ws = None
        self.access_token = access_token

        self.origin = "https://stake.com"
        self.protocols = ["graphql-transport-ws"]
        self.agent_text = user_agent
        self.headers = {
            "Cookie": f"session={self.access_token}; cf_clearance={cf_clearance}",
            "Host": "stake.com",
            "Sec-Websocket-Extensions": "permessage-deflate; client_max_window_bits",
        }

    def event(self):
        def register_handler(handler):
            self._event = handler
            return handler
        return register_handler

    def ev(self, *args, **kwargs):
        pass

    async def get_response(self):
        response = await self.ws.recv()
        return json.loads(response)

    async def send_request(self, payload):
        await self.ws.send(json.dumps(payload))
    
    async def ping_task(self):
        while True:
            await asyncio.sleep(10)
            await self.send_request({"type": "ping"})

    async def main(self):
        try:
            self.ws = await connect(
                "wss://stake.com/_api/websockets",
                origin=self.origin,
                subprotocols=self.protocols,
                user_agent_header=self.agent_text,
                extra_headers=self.headers
            )
        except:
            raise StakeError("WebSocketに接続できませんでした")

        asyncio.get_event_loop().create_task(self.ping_task())

        init_payload = {
            "type": "connection_init",
            "payload": {
                "accessToken": self.access_token,
                "language": "ja",
                "lockdownToken": "s5MNWtjTM5TvCMkAzxov"
            }
        }
        await self.send_request(init_payload)

        while True:
            data = await self.get_response()

            try:
                if data.get("type") == None:
                    continue
                elif data.get("type") == "connection_ack":
                    await self.send_request({
                        "id": str(uuid.uuid4()),
                        "payload": {
                            "query": "subscription AvailableBalances {\n  availableBalances {\n    amount\n    identifier\n    balance {\n      amount\n      currency\n    }\n  }\n}\n"
                        },
                        "type": "subscribe"
                    })

                    await self.send_request({
                        "id": str(uuid.uuid4()),
                        "payload": {
                            "query": "subscription VaultBalances {\n  vaultBalances {\n    amount\n    identifier\n    balance {\n      amount\n      currency\n    }\n  }\n}\n"
                        },
                        "type": "subscribe"
                    })

                    await self.send_request({
                        "id": str(uuid.uuid4()),
                        "payload": {
                            "context": {
                                "preferGetMethod": False,
                                "requestPolicy": "network-only",
                                "suspense": False,
                                "url": "/_api/graphql"
                            },
                            "key": "1age5vl",
                            "query": "subscription Announcements {\n  announcements {\n    ...Announcement\n    __typename\n  }\n}\n\nfragment Announcement on Announcement {\n  id\n  name\n  message\n  colour\n  location\n  expired\n  startTime\n  endTime\n}\n"
                        },
                        "type": "subscribe"
                    })

                    await self.send_request({
                        "id": str(uuid.uuid4()),
                        "payload": {
                            "context": {
                                "preferGetMethod": False,
                                "requestPolicy": "cache-first",
                                "suspense": False,
                                "url": "/_api/graphql"
                            },
                            "key": "h4mjbm",
                            "query": "subscription RaceStatus {\n  raceStatus {\n    ...RaceFragment\n    __typename\n  }\n}\n\nfragment RaceFragment on Race {\n  id\n  name\n  description\n  currency\n  type\n  startTime\n  endTime\n  status\n  scope\n  promotionPeriod\n}\n"
                        },
                        "type": "subscribe"
                    })

                    await self.send_request({
                        "id": str(uuid.uuid4()),
                        "payload": {
                            "context": {
                                "preferGetMethod": False,
                                "requestPolicy": "network-only",
                                "suspense": False,
                                "url": "/_api/graphql"
                            },
                            "key": "k3oe0v",
                            "query": "subscription FeatureFlagSubscription {\n  featureFlagUpdates {\n    ...FeatureFlagFragment\n    __typename\n  }\n}\n\nfragment FeatureFlagFragment on FeatureFlag {\n  id\n  name\n  createdAt\n  config {\n    ... on AgeVerificationFlagConfig {\n      minAge\n      enabled\n      type\n      __typename\n    }\n    ... on AddressVerificationFlagConfig {\n      bannedCountries\n      bannedStates\n      enabled\n      type\n      __typename\n    }\n    ... on DocumentVerificationFlagConfig {\n      provider\n      enabled\n      type\n      __typename\n    }\n    ... on RiskVerificationFlagConfig {\n      allowPoliticallyExposedPersons\n      allowThirdPartyAccounts\n      enabled\n      type\n      __typename\n    }\n    ... on PlaySessionFlagConfig {\n      expiryTime\n      enabled\n      type\n      __typename\n    }\n    ... on BiometricVerificationFlagConfig {\n      integration\n      enabled\n      type\n      __typename\n    }\n    ... on BooleanFlagConfig {\n      enabled\n      type\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n"
                        },
                        "type": "subscribe"
                    })
                    
                    await self.send_request({
                        "id": str(uuid.uuid4()),
                        "payload": {
                            "key": "c453c4",
                            "context": {
                                "preferGetMethod": False,
                                "requestPolicy": "network-only",
                                "suspense": False,
                                "url": "/_api/graphql"
                            },
                            "query": "subscription Notifications {\n  notifications {\n    ...Notification\n    __typename\n  }\n}\n\nfragment Notification on Notification {\n  id\n  type\n  acknowledged\n  __typename\n  data {\n    __typename\n    ... on NotificationKyc {\n      kycStatus: status\n      __typename\n    }\n    ... on UserFlag {\n      createdAt\n      flag\n      __typename\n    }\n    ... on ChatTip {\n      createdAt\n      currency\n      amount\n      sendBy {\n        name\n        __typename\n      }\n      __typename\n    }\n    ... on NotificationKycBanned {\n      kycBannedMessage: message\n      __typename\n    }\n    ... on ChatRainUser {\n      amount\n      currency\n      rain {\n        createdAt\n        sendBy {\n          name\n          __typename\n        }\n        __typename\n      }\n      __typename\n    }\n    ... on CashAdvance {\n      id\n      advanceAmount\n      currency\n      createdAt\n      __typename\n    }\n    ... on UserBonus {\n      createdAt\n      currency\n      amount\n      credit\n      __typename\n    }\n    ... on SportBet {\n      id\n      amount\n      active\n      currency\n      status\n      payoutMultiplier\n      cashoutMultiplier\n      payout\n      createdAt\n      system\n      potentialMultiplier\n      adjustments {\n        id\n        payoutMultiplier\n        updatedAt\n        createdAt\n        __typename\n      }\n      user {\n        id\n        name\n        __typename\n      }\n      search {\n        iid\n        __typename\n      }\n      outcomes {\n        odds\n        status\n        outcome {\n          id\n          name\n          active\n          odds\n          __typename\n        }\n        market {\n          ...SportMarket\n          __typename\n        }\n        fixture {\n          id\n          slug\n          provider\n          tournament {\n            ...TournamentTree\n            __typename\n          }\n          data {\n            ...SportFixtureDataMatch\n            ...SportFixtureDataOutright\n            __typename\n          }\n          __typename\n        }\n        __typename\n      }\n      __typename\n    }\n    ... on SwishBet {\n      ...SwishBetFragment\n      __typename\n    }\n    ... on WalletDeposit {\n      id\n      createdAt\n      amount\n      currency\n      chain\n      walletStatus: status\n      tokensReceived {\n        currency\n        amount\n        __typename\n      }\n      __typename\n    }\n    ... on RacePosition {\n      position\n      payoutAmount\n      currency\n      race {\n        name\n        endTime\n        __typename\n      }\n      __typename\n    }\n    ... on CommunityMute {\n      active\n      message\n      expireAt\n      __typename\n    }\n    ... on ChallengeWin {\n      challenge {\n        ...Challenge\n        __typename\n      }\n      __typename\n    }\n    ... on Challenge {\n      ...Challenge\n      __typename\n    }\n    ... on NotificationFiatError {\n      code\n      limitType\n      fiatErrorAmount: amount\n      fiatErrorCurrency: currency\n      __typename\n    }\n    ... on VeriffUser {\n      veriffStatus: status\n      veriffReason: reason\n      __typename\n    }\n    ... on SportsbookPromotionBet {\n      id\n      bet {\n        id\n        __typename\n      }\n      betAmount\n      value\n      currency\n      payout\n      payoutValue\n      sportsbookPromotionBetStatus: status\n      sportsbookPromotionBetUser: user {\n        id\n        name\n        __typename\n      }\n      promotion {\n        id\n        name\n        __typename\n      }\n      __typename\n    }\n    ... on UserPostcardCode {\n      id\n      claimedAt\n      postcardCode: code\n      __typename\n    }\n    ... on NotificationSessionExpiry {\n      expiry: expireAt\n      __typename\n    }\n  }\n}\n\nfragment SportMarket on SportMarket {\n  id\n  name\n  status\n  extId\n  specifiers\n  customBetAvailable\n  provider\n}\n\nfragment TournamentTree on SportTournament {\n  id\n  name\n  slug\n  category {\n    ...CategoryTree\n    __typename\n  }\n}\n\nfragment CategoryTree on SportCategory {\n  id\n  name\n  slug\n  sport {\n    id\n    name\n    slug\n    __typename\n  }\n}\n\nfragment SportFixtureDataMatch on SportFixtureDataMatch {\n  startTime\n  competitors {\n    ...SportFixtureCompetitor\n    __typename\n  }\n  teams {\n    name\n    qualifier\n    __typename\n  }\n  tvChannels {\n    language\n    name\n    streamUrl\n    __typename\n  }\n  __typename\n}\n\nfragment SportFixtureCompetitor on SportFixtureCompetitor {\n  name\n  extId\n  countryCode\n  abbreviation\n  iconPath\n}\n\nfragment SportFixtureDataOutright on SportFixtureDataOutright {\n  name\n  startTime\n  endTime\n  __typename\n}\n\nfragment SwishBetFragment on SwishBet {\n  __typename\n  active\n  amount\n  cashoutMultiplier\n  createdAt\n  currency\n  customBet\n  id\n  odds\n  payout\n  payoutMultiplier\n  updatedAt\n  status\n  user {\n    id\n    name\n    preferenceHideBets\n    __typename\n  }\n  outcomes {\n    __typename\n    id\n    odds\n    lineType\n    outcome {\n      ...SwishMarketOutcomeFragment\n      __typename\n    }\n  }\n}\n\nfragment SwishMarketOutcomeFragment on SwishMarketOutcome {\n  __typename\n  id\n  line\n  over\n  under\n  gradeOver\n  gradeUnder\n  suspended\n  balanced\n  name\n  competitor {\n    id\n    name\n    __typename\n  }\n  market {\n    id\n    stat {\n      name\n      value\n      __typename\n    }\n    game {\n      id\n      fixture {\n        id\n        name\n        slug\n        status\n        eventStatus {\n          ...SportFixtureEventStatus\n          ...EsportFixtureEventStatus\n          __typename\n        }\n        data {\n          ... on SportFixtureDataMatch {\n            __typename\n            startTime\n            competitors {\n              name\n              extId\n              countryCode\n              abbreviation\n              __typename\n            }\n          }\n          __typename\n        }\n        tournament {\n          id\n          slug\n          category {\n            id\n            slug\n            sport {\n              id\n              name\n              slug\n              __typename\n            }\n            __typename\n          }\n          __typename\n        }\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n}\n\nfragment SportFixtureEventStatus on SportFixtureEventStatusData {\n  __typename\n  homeScore\n  awayScore\n  matchStatus\n  clock {\n    matchTime\n    remainingTime\n    __typename\n  }\n  periodScores {\n    homeScore\n    awayScore\n    matchStatus\n    __typename\n  }\n  currentTeamServing\n  homeGameScore\n  awayGameScore\n  statistic {\n    yellowCards {\n      away\n      home\n      __typename\n    }\n    redCards {\n      away\n      home\n      __typename\n    }\n    corners {\n      home\n      away\n      __typename\n    }\n    __typename\n  }\n}\n\nfragment EsportFixtureEventStatus on EsportFixtureEventStatus {\n  matchStatus\n  homeScore\n  awayScore\n  scoreboard {\n    homeGold\n    awayGold\n    homeGoals\n    awayGoals\n    homeKills\n    awayKills\n    gameTime\n    homeDestroyedTowers\n    awayDestroyedTurrets\n    currentRound\n    currentCtTeam\n    currentDefTeam\n    time\n    awayWonRounds\n    homeWonRounds\n    remainingGameTime\n    __typename\n  }\n  periodScores {\n    type\n    number\n    awayGoals\n    awayKills\n    awayScore\n    homeGoals\n    homeKills\n    homeScore\n    awayWonRounds\n    homeWonRounds\n    matchStatus\n    __typename\n  }\n  __typename\n}\n\nfragment Challenge on Challenge {\n  id\n  type\n  active\n  adminCreated\n  completedAt\n  award\n  claimCount\n  claimMax\n  currency\n  isRefunded\n  minBetUsd\n  betCurrency\n  startAt\n  expireAt\n  updatedAt\n  createdAt\n  targetMultiplier\n  game {\n    id\n    name\n    slug\n    thumbnailUrl\n    __typename\n  }\n  creatorUser {\n    ...UserTags\n    __typename\n  }\n  affiliateUser {\n    ...UserTags\n    __typename\n  }\n  wins {\n    id\n    claimedBy {\n      ...UserTags\n      __typename\n    }\n    __typename\n  }\n}\n\nfragment UserTags on User {\n  id\n  name\n  isMuted\n  isRainproof\n  isIgnored\n  isHighroller\n  isSportHighroller\n  leaderboardDailyProfitRank\n  leaderboardDailyWageredRank\n  leaderboardWeeklyProfitRank\n  leaderboardWeeklyWageredRank\n  flags {\n    flag\n    rank\n    createdAt\n    __typename\n  }\n  roles {\n    name\n    expireAt\n    message\n    __typename\n  }\n  createdAt\n  preferenceHideBets\n}\n"
                        },
                        "type": "subscribe"
                    })

                    await self.send_request({
                        "id": str(uuid.uuid4()),
                        "payload": {
                            "context": {
                                "preferGetMethod": False,
                                "requestPolicy": "cache-first",
                                "suspense": False,
                                "url": "/_api/graphql"
                            },
                            "key": "1sqjsp2",
                            "query": "subscription HouseBets {\n  houseBets {\n    ...RealtimeHouseBet\n    __typename\n  }\n}\n\nfragment RealtimeHouseBet on Bet {\n  id\n  iid\n  game {\n    name\n    icon\n    __typename\n  }\n  bet {\n    __typename\n    ... on CasinoBet {\n      id\n      active\n      payoutMultiplier\n      amountMultiplier\n      amount\n      payout\n      updatedAt\n      currency\n      user {\n        id\n        name\n        preferenceHideBets\n        __typename\n      }\n      __typename\n    }\n    ... on EvolutionBet {\n      id\n      amount\n      currency\n      createdAt\n      payout\n      payoutMultiplier\n      user {\n        id\n        name\n        preferenceHideBets\n        __typename\n      }\n      __typename\n    }\n    ... on MultiplayerCrashBet {\n      id\n      payoutMultiplier\n      amount\n      payout\n      currency\n      updatedAt\n      user {\n        id\n        name\n        preferenceHideBets\n        __typename\n      }\n      __typename\n    }\n    ... on MultiplayerSlideBet {\n      id\n      payoutMultiplier\n      amount\n      payout\n      currency\n      updatedAt\n      createdAt\n      user {\n        id\n        name\n        preferenceHideBets\n        __typename\n      }\n      __typename\n    }\n    ... on SoftswissBet {\n      id\n      amount\n      currency\n      updatedAt\n      payout\n      payoutMultiplier\n      user {\n        id\n        name\n        preferenceHideBets\n        __typename\n      }\n      __typename\n    }\n    ... on ThirdPartyBet {\n      id\n      amount\n      currency\n      updatedAt\n      createdAt\n      payout\n      payoutMultiplier\n      user {\n        id\n        name\n        preferenceHideBets\n        __typename\n      }\n      __typename\n    }\n  }\n}\n"
                        },
                        "type": "subscribe"
                    })

                    await self.send_request({
                        "id": str(uuid.uuid4()),
                        "payload": {
                            "context": {
                                "preferGetMethod": False,
                                "requestPolicy": "cache-first",
                                "suspense": False,
                                "url": "/_api/graphql"
                            },
                            "key": "1mlozo4",
                            "query": "subscription SportBets {\n  sportBets {\n    id\n    active\n    status\n    cashoutMultiplier\n    outcomes {\n      id\n      status\n      __typename\n    }\n    __typename\n  }\n}\n"
                        },
                        "type": "subscribe"
                    })

                    await self.send_request({
                        "id": str(uuid.uuid4()),
                        "payload": {
                            "context": {
                                "preferGetMethod": False,
                                "requestPolicy": "cache-first",
                                "suspense": False,
                                "url": "/_api/graphql"
                            },
                            "key": "1udms4e",
                            "query": "subscription depositBonusTransaction {\n  depositBonusTransaction {\n    amount\n    currency\n    value\n    deposit {\n      hash\n      __typename\n    }\n    __typename\n  }\n}\n"
                        },
                        "type": "subscribe"
                    })

                await self._event(data)
            except:
                pass