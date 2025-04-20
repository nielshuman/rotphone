import pjsua2 as pj
from print_color import print
import time
import os
from dotenv import load_dotenv
load_dotenv()

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

  def onCallState(self, prm):
      ci = self.getInfo()
      print('Callstate: %s' % (ci.stateText), tag="Call", tag_color="blue")
      if ci.state == pj.PJSIP_TP_STATE_DISCONNECTED:
        self.account.current_call = None
      
  def onCallMediaState(self, prm):
        ci = self.getInfo()
        print("Call media state", tag="Call", tag_color="blue")
        print(f'Callstate: {ci.stateText}', tag="Call", tag_color="blue")
        for mi in ci.media:
            if mi.type == pj.PJMEDIA_TYPE_AUDIO and \
              (mi.status == pj.PJSUA_CALL_MEDIA_ACTIVE or \
               mi.status == pj.PJSUA_CALL_MEDIA_REMOTE_HOLD):
                m = self.getMedia(mi.index)
                am = pj.AudioMedia.typecastFromMedia(m)
                # connect ports
                ep.audDevManager().getCaptureDevMedia().startTransmit(am)
                am.startTransmit(ep.audDevManager().getPlaybackDevMedia())
                
  def onDtmfDigit(self, prm):
       print('Got DTMF:' + prm.digit, tag="Call", tag_color="blue")
       if prm.digit == '1':
           print("Hangup call", color="yellow")
           call_prm = pj.CallOpParam()
           call_prm.statusCode = pj.PJSIP_SC_OK
           self.hangup(call_prm)
                    
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

  acfg = pj.AccountConfig();
  acfg.idUri = os.getenv("SIP_ID_URI");
  acfg.regConfig.registrarUri = os.getenv("SIP_REG_URI");
  cred = pj.AuthCredInfo("digest", "*", os.getenv("SIP_AUTH_ID"), 0, os.getenv("SIP_AUTH_PASS"));
  acfg.sipConfig.authCreds.append(cred);
  
  # Create the account
  acc = Account();
  acc.create(acfg);
  
  # Here we don't have anything else to do..
  time.sleep(60);

  # Destroy the library
  ep.libDestroy()


if __name__ == "__main__":
  pjsua2_test()