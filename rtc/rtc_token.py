import os
import time
from .src.RtcTokenBuilder import RtcTokenBuilder, Role_Attendee, Role_Publisher


appID = os.environ["AG_APP_ID"]
appCertificate = os.environ["AG_APP_CERTIFICATE"]


def generate_rtc_token(uid: int, channel_name: str, role = Role_Publisher) -> str:
    expireTimeInSeconds = 30 * 24 * 60 * 60
    currentTimestamp = int(time.time())
    privilegeExpiredTs = currentTimestamp + expireTimeInSeconds
    return RtcTokenBuilder.buildTokenWithUid(appID, appCertificate, channel_name, uid, role, privilegeExpiredTs)
