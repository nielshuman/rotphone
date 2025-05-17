from print_color import print as printc
import time
import os
from dotenv import load_dotenv
import pjsua2 as pj
import queue
load_dotenv()

import simpleaudio as sa


class Sounds:
  startup = sa.WaveObject.from_wave_file('audio/startup.wav')
  connected = sa.WaveObject.from_wave_file('audio/connected.wav')
  ringing = sa.WaveObject.from_wave_file('audio/ringing.wav')
  disconnected = sa.WaveObject.from_wave_file('audio/disconnected.wav')
  
from convert_audio import convert_audio
convert_audio("audio")

from rot import rotaryDial, phoneHook, bells

ep = pj.Endpoint()

class FuckingkutzooiHandler():
  def __init__(self):
    self.command_queue = queue.Queue()
    self.onpickupPhone = None
    self.onhangupPhone = None
    self.ondigit = None

    self._number = ""
    
    phoneHook.when_pressed = lambda: self.command_queue.put("pickupPhone")
    phoneHook.when_released = lambda: self.command_queue.put("hangupPhone")
    rotaryDial.onDigit = lambda digit: self.command_queue.put(digit)
  
  def handleFuckingkutzooi(self):
    command = self.command_queue.get()  # Blocks indefinitely until something arrives

    if command == "pickupPhone":
        if self.onpickupPhone:
            self.onpickupPhone()
    elif command == "hangupPhone":
        if self.onhangupPhone:
            self.onhangupPhone()
    else:
        if self.ondigit and isinstance(command, int):
            self.ondigit(command)
  
  def onCallDisconnect(self):
    if phoneHook.is_pressed:
      Sounds.disconnected.play()
    if bells.ringing:
      bells.stop()
    self.onpickupPhone = None
    self.onhangupPhone = None
    self.ondigit = None

  def start_number_input(self):
    self.onhangupPhone = self.cancel_number_input
    printc("Starting number input", tag="Dialer", tag_color="green")
    Sounds.startup.play()
    self.ondigit = self.handle_number_digit
    
  def cancel_number_input(self):
    self.ondigit = None
    self._number = ""
    printc("Canceled number input", tag="Dialer", tag_color="red")
    
  def handle_number_digit(self, digit):
    self._number += str(digit)
    print('\rNumber:' + self._number, flush=True, end="")
    if len(self._number) == 10:
      print('')
      printc("Calling number: " + self._number, tag="Dialer", tag_color="green")
      #account.placeCall("sip:" + self._number + "@" + os.getenv("SIP_REG_HOST"))
      self._number = ""
      self.ondigit = None
    
    
fuckingkutzooiHandler = FuckingkutzooiHandler()

def initialize_pjsua():
    ep_cfg = pj.EpConfig()
    ep_cfg.logConfig.level = 1
    ep.libCreate()
    ep.libInit(ep_cfg)
    
    sipTpConfig = pj.TransportConfig();
    sipTpConfig.port = 5060
    ep.transportCreate(pj.PJSIP_TRANSPORT_UDP, sipTpConfig);
    
    ep.libStart();
    
def set_audio_devices():
  ep.audDevManager().setPlaybackDev(int(os.getenv("PJSUA_PLAYBACK_DEV")))
  ep.audDevManager().setCaptureDev(int(os.getenv("PJSUA_CAPTURE_DEV")))
  printc("Playback device:", ep.audDevManager().getDevInfo(ep.audDevManager().getPlaybackDev()).name, tag="Audio", tag_color="blue")
  printc("Capture device:", ep.audDevManager().getDevInfo(ep.audDevManager().getCaptureDev()).name, tag="Audio", tag_color="blue")

def get_account_config():
  acfg = pj.AccountConfig()
  acfg.idUri = os.getenv("SIP_ID_URI");
  acfg.regConfig.registrarUri = "sip:" + os.getenv("SIP_REG_HOST");
  cred = pj.AuthCredInfo("digest", "*", os.getenv("SIP_AUTH_ID"), 0, os.getenv("SIP_AUTH_PASS"));
  acfg.sipConfig.authCreds.append(cred);
  
  return acfg

def list_audio_devices():
    count = ep.audDevManager().getDevCount()
    printc(f"Found {count} audio devices:")
    for i in range(count):
        info = ep.audDevManager().getDevInfo(i)
        printc(f"{i}: {info.name} (input={info.inputCount}, output={info.outputCount})")

class Account(pj.Account):
  def __init__(self):
    super().__init__()
    self.current_call = None
  
  def onRegState(self, prm):
    printc("Registration state: " + prm.reason, tag="Account", tag_color="purple")
    
  def onIncomingCall(self, prm):
    # if self.current_call is not None:
    #   printc("Already in a call, rejecting incoming call", color="red")
    #   reject_prm = pj.CallOpParam()
    #   reject_prm.statusCode = pj.PJSIP_SC_BUSY_HERE
    #   self.current_call.hangup(reject_prm)
    #   return
    
    # already managed by PBX, not nessary to reject
    
    self.current_call = MyCall(self, prm.callId)
    c = self.current_call
    ci = c.getInfo()
    printc("Incoming call from %s" % (ci.remoteUri), color="yellow")
    
    if phoneHook.is_pressed:
      printc("Phone is off hook, rejecting incoming call", color="red")
      reject_prm = pj.CallOpParam()
      reject_prm.statusCode = pj.PJSIP_SC_BUSY_HERE
      c.hangup(reject_prm)
      return
    
    #  start ringing
    bells.ring()
    ringing_prm = pj.CallOpParam()
    ringing_prm.statusCode = pj.PJSIP_SC_RINGING # 180
    c.answer(ringing_prm)
    
    fuckingkutzooiHandler.onpickupPhone = self.answer_current_call
    
  def answer_current_call(self):
    if self.current_call is None:
      printc("No current call to answer", color="red")
      return
    self.ringing = False
    if bells.ringing:
      bells.stop()
    answer_prm = pj.CallOpParam()
    answer_prm.statusCode = pj.PJSIP_SC_OK
    self.current_call.answer(answer_prm)
    fuckingkutzooiHandler.onpickupPhone = None
    fuckingkutzooiHandler.onhangupPhone = self.hangup_current_call
    
  def hangup_current_call(self):
    if self.current_call is None:
      printc("No current call to hang up", color="red")
      return
    hangup_prm = pj.CallOpParam()
    hangup_prm.statusCode = pj.PJSIP_SC_OK
    self.current_call.hangup(hangup_prm)
    fuckingkutzooiHandler.onCallDisconnect()
    self.current_call = None
    printc("Call hung up", tag="Account", tag_color="purple")
    


class MyCall(pj.Call):
  def __init__(self, account, callId = pj.INVALID_ID):
    pj.Call.__init__(self, account, callId)
    self.account = account
    self.account.current_call = self
    
  def onCallState(self, prm):
    ci = self.getInfo()
    printc('Callstate: %s' % (ci.stateText), tag="Call", tag_color="blue")
    
    if ci.state == pj.PJSIP_INV_STATE_DISCONNECTED:
      fuckingkutzooiHandler.onCallDisconnect()
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
              
              # captureAudioMedia.startTransmit(callAudioMedia)
              callAudioMedia.startTransmit(playbackAudioMedia)
                
  def onDtmfDigit(self, prm):
       printc('Got DTMF:' + prm.digit, tag="Call", tag_color="blue")
       if prm.digit == '1':
           printc("Hangup call", color="yellow")
           call_prm = pj.CallOpParam()
           call_prm.statusCode = pj.PJSIP_SC_OK
           self.hangup(call_prm)
       elif prm.digit == '2':
         self.playFlyLikeMe()
       elif prm.digit == '3':
         self.stopFlyLikeMe()
  
  def playFlyLikeMe(self):
      self.player = pj.AudioMediaPlayer()
      self.player.createPlayer("audio/flylikeme.phone.wav")
      self.player.startTransmit(self.callAudioMedia)
      self.callAudioMedia.startTransmit(ep.audDevManager().getPlaybackDevMedia())
      printc("Playing fly like me", tag="Call", tag_color="blue")
      
  def stopFlyLikeMe(self):
      self.player.stopTransmit(self.callAudioMedia)
      self.callAudioMedia.stopTransmit(ep.audDevManager().getPlaybackDevMedia())
      printc("Stopped playing fly like me", tag="Call", tag_color="blue")


def main():
  initialize_pjsua()
  set_audio_devices()
  # Create the account
  acc = Account();
  acc.create(get_account_config())
  
  fuckingkutzooiHandler.onpickupPhone = fuckingkutzooiHandler.start_number_input

  # ep.libRegisterThread('gpiozero')
  while True:
    fuckingkutzooiHandler.handleFuckingkutzooi()


  # Destroy the library
  ep.libDestroy()



if __name__ == "__main__":
  main()