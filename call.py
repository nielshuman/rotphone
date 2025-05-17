import pjsua2 as pj
from print_color import print as printc

ep = pj.Endpoint()

def initialize_pjsua():
    ep_cfg = pj.EpConfig()
    ep_cfg.logConfig.level = 1
    ep.libCreate()
    ep.libInit(ep_cfg)
    
    sipTpConfig = pj.TransportConfig();
    sipTpConfig.port = 5060;
    ep.transportCreate(pj.PJSIP_TRANSPORT_UDP, sipTpConfig);
    
    ep.libStart();
    p.audDevManager().setPlaybackDev(int(os.getenv("PJSUA_PLAYBACK_DEV")))
    printc("Playback device:", ep.audDevManager().getDevInfo(ep.audDevManager().getPlaybackDev()).name, tag="Audio", tag_color="blue")
    ep.audDevManager().setCaptureDev(int(os.getenv("PJSUA_CAPTURE_DEV")))
    printc("Capture device:", ep.audDevManager().getDevInfo(ep.audDevManager().getCaptureDev()).name, tag="Audio", tag_color="blue")

class MyCall(pj.Call):
  def __init__(self, account, callId = pj.INVALID_ID):
    pj.Call.__init__(self, account, callId)
    self.account = account
    self.account.current_call = self

  def onCallState(self, prm):
    ci = self.getInfo()
    printc('Callstate: %s' % (ci.stateText), tag="Call", tag_color="blue")
    if ci.state == pj.PJSIP_TP_STATE_DISCONNECTED:
      self.account.current_call = None
      
  def onCallMediaState(self, prm):
      ci = self.getInfo()
      printc("Call media state", tag="Call", tag_color="blue")
      for mi in ci.media:
          if mi.type != pj.PJMEDIA_TYPE_AUDIO:
            continue
          
          if (mi.status == pj.PJSUA_CALL_MEDIA_ACTIVE or mi.status == pj.PJSUA_CALL_MEDIA_REMOTE_HOLD):
              callAudioMedia = self.getAudioMedia(mi.index)
              self.callAudioMedia = callAudioMedia

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
      printc("Playing fly like me", tag="Call", tag_color="blue")
      
  def stopFlyLikeMe(self):
      self.player.stopTransmit(self.callAudioMedia)
      self.callAudioMedia.stopTransmit(ep.audDevManager().getPlaybackDevMedia())
      printc("Stopped playing fly like me", tag="Call", tag_color="blue")
      
class Account(pj.Account):
  def __init__(self):
    super().__init__()
    self.current_call = None
  
  def onRegState(self, prm):
    printc("Registration state: " + prm.reason, tag="Account", tag_color="purple")
    
  def onIncomingCall(self, prm):
    self.current_call = MyCall(self, prm.callId)
    c = self.current_call
    ci = c.getInfo()
    printc("Incoming call from %s" % (ci.remoteUri), color="yellow")
    call_prm = pj.CallOpParam()
    call_prm.statusCode = pj.PJSIP_SC_OK # 200
    c.answer(call_prm)
    # print("Hangup call", color="yellow")