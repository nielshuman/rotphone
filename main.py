from print_color import print
import time
import os
from dotenv import load_dotenv
import pjsua2 as pj
load_dotenv()

from convert_audio import convert_audio
convert_audio("_audio", "audio")

ep = pj.Endpoint()

class Account(pj.Account):
  def __init__(self):
    super().__init__()
    self.current_call = None
  
  def onRegState(self, prm):
    print("Registration state: " + prm.reason, tag="Account", tag_color="purple")
    
  def onIncomingCall(self, prm):
    self.current_call = MyCall(self, prm.callId)
    c = self.current_call
    ci = c.getInfo()
    print("Incoming call from %s" % (ci.remoteUri), color="yellow")
    call_prm = pj.CallOpParam()
    call_prm.statusCode = pj.PJSIP_SC_OK # 200
    c.answer(call_prm)
    # print("Hangup call", color="yellow")

class MyCall(pj.Call):
  def __init__(self, account, callId = pj.INVALID_ID):
    pj.Call.__init__(self, account, callId)
    self.account = account
    self.account.current_call = self

  def onCallState(self, prm):
    ci = self.getInfo()
    print('Callstate: %s' % (ci.stateText), tag="Call", tag_color="blue")
    if ci.state == pj.PJSIP_TP_STATE_DISCONNECTED:
      self.account.current_call = None
      
  def onCallMediaState(self, prm):
      ci = self.getInfo()
      print("Call media state", tag="Call", tag_color="blue")
      for mi in ci.media:
          if mi.type != pj.PJMEDIA_TYPE_AUDIO:
            continue
          
          if (mi.status == pj.PJSUA_CALL_MEDIA_ACTIVE or mi.status == pj.PJSUA_CALL_MEDIA_REMOTE_HOLD):
              callAudioMedia = self.getAudioMedia(mi.index)
              self.callAudioMedia = callAudioMedia
              print('BAaasadsadps')

              # connect ports
              captureAudioMedia = ep.audDevManager().getCaptureDevMedia()
              playbackAudioMedia = ep.audDevManager().getPlaybackDevMedia()
              captureAudioMedia.startTransmit(callAudioMedia)
              callAudioMedia.startTransmit(playbackAudioMedia)
                
  def onDtmfDigit(self, prm):
       print('Got DTMF:' + prm.digit, tag="Call", tag_color="blue")
       if prm.digit == '1':
           print("Hangup call", color="yellow")
           call_prm = pj.CallOpParam()
           call_prm.statusCode = pj.PJSIP_SC_OK
           self.hangup(call_prm)
       elif prm.digit == '2':
         self.playFlyLikeMe()
       elif prm.digit == '3':
         self.stopFlyLikeMe()
  
  def playFlyLikeMe(self):
      self.player = pj.AudioMediaPlayer()
      self.player.createPlayer("audio/flylikeme.wav")
      self.player.startTransmit(self.callAudioMedia)
      self.callAudioMedia.startTransmit(ep.audDevManager().getPlaybackDevMedia())
      print("Playing fly like me", tag="Call", tag_color="blue")
      
  def stopFlyLikeMe(self):
      self.player.stopTransmit(self.callAudioMedia)
      self.callAudioMedia.stopTransmit(ep.audDevManager().getPlaybackDevMedia())
      print("Stopped playing fly like me", tag="Call", tag_color="blue")
                    
# pjsua2 test function
def pjsua2_test():
  # global ep
  # Create and initialize the library
  ep_cfg = pj.EpConfig()
  ep_cfg.logConfig.level = 1
  ep.libCreate()
  ep.libInit(ep_cfg)

  # Create SIP transport. Error handling sample is shown
  sipTpConfig = pj.TransportConfig();
  sipTpConfig.port = 5060;
  ep.transportCreate(pj.PJSIP_TRANSPORT_UDP, sipTpConfig);
  
  # Start the library
  ep.libStart();
  ep.audDevManager().setPlaybackDev(int(os.getenv("PJSUA_PLAYBACK_DEV")))
  print("Playback device:", ep.audDevManager().getDevInfo(ep.audDevManager().getPlaybackDev()).name, tag="Audio", tag_color="blue")
  ep.audDevManager().setCaptureDev(int(os.getenv("PJSUA_CAPTURE_DEV")))
  print("Capture device:", ep.audDevManager().getDevInfo(ep.audDevManager().getCaptureDev()).name, tag="Audio", tag_color="blue")
  acfg = pj.AccountConfig();
  acfg.idUri = os.getenv("SIP_ID_URI");
  acfg.regConfig.registrarUri = "sip:" + os.getenv("SIP_REG_HOST");
  cred = pj.AuthCredInfo("digest", "*", os.getenv("SIP_AUTH_ID"), 0, os.getenv("SIP_AUTH_PASS"));
  acfg.sipConfig.authCreds.append(cred);
  
  # Create the account
  acc = Account();
  acc.create(acfg);
  
  while True:
    time.sleep(1)

  # Destroy the library
  ep.libDestroy()


def list_audio_devices():
    count = ep.audDevManager().getDevCount()
    print(f"Found {count} audio devices:")
    for i in range(count):
        info = ep.audDevManager().getDevInfo(i)
        print(f"{i}: {info.name} (input={info.inputCount}, output={info.outputCount})")

if __name__ == "__main__":
  pjsua2_test()